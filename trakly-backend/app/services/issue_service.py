"""Issue management service."""
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.issue import Issue, IssueStatus, IssueType, Checklist, ChecklistItem
from app.models.feature_issue_link import FeatureIssueLink, FeatureIssueLinkType
from app.repositories.issue import IssueRepository
from app.repositories.project import ProjectRepository
from app.repositories.feature import FeatureRepository
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.services.watcher_service import WatcherService
from app.services.activity_service import ActivityService
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType


class IssueService:
    """Service for issue operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.issue_repo = IssueRepository(db)
        self.project_repo = ProjectRepository(db)
        self.feature_repo = FeatureRepository(db)
        self.dedup_service = DuplicateDetectionService(db)
        self.watcher_service = WatcherService(db)
        self.activity_service = ActivityService(db)
        self.notification_service = NotificationService(db)

    async def create_issue(
        self,
        issue_data: Dict[str, Any],
        reporter_id: str,
    ) -> Issue:
        """
        Create a new issue.

        Args:
            issue_data: Issue creation data
            reporter_id: User ID of reporter

        Returns:
            Created issue
        """
        project_id = issue_data["project_id"]

        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Validate sprint assignment - prevent assignment to completed sprints
        if "sprint_id" in issue_data and issue_data["sprint_id"]:
            from app.repositories.sprint import SprintRepository
            sprint_repo = SprintRepository(self.db)
            target_sprint = await sprint_repo.get(issue_data["sprint_id"])
            if target_sprint and target_sprint.is_completed:
                raise ValidationError("Cannot assign issues to a closed/completed sprint")

        # Get next issue number atomically
        issue_number = await self.issue_repo.get_next_issue_number(project_id)

        # Generate issue key (e.g., TRAK-123)
        issue_key = f"{project.key}-{issue_number}"

        # Generate deduplication hash
        dedup_hash = self.dedup_service.generate_deduplication_hash(
            issue_data["title"],
            issue_data.get("description"),
        )

        # Extract feature linking info
        feature_id = issue_data.pop("feature_id", None)
        feature_link_type = issue_data.pop("feature_link_type", "implements")

        # Extract label_ids for later assignment
        label_ids = issue_data.pop("label_ids", [])

        # Prepare issue data
        issue_data["organization_id"] = project.organization_id
        issue_data["issue_number"] = issue_number
        issue_data["issue_key"] = issue_key
        issue_data["reporter_id"] = reporter_id
        issue_data["deduplication_hash"] = dedup_hash

        # Convert string enums to actual enums
        issue_data["issue_type"] = IssueType(issue_data["issue_type"])
        if "status" in issue_data:
            issue_data["status"] = IssueStatus(issue_data["status"])

        # Create issue
        issue = await self.issue_repo.create(issue_data)

        # Log activity
        await self.activity_service.log_issue_created(
            issue_id=issue.id,
            organization_id=issue.organization_id,
            user_id=reporter_id,
            issue_data={
                "title": issue.title,
                "status": issue.status.value,
                "issue_type": issue.issue_type.value,
            },
        )

        # Auto-subscribe reporter as watcher
        await self.watcher_service.subscribe(
            issue.id,
            reporter_id,
            subscription_type="auto_reporter",
        )

        # Auto-subscribe assignee if exists
        if issue.assignee_id:
            await self.watcher_service.auto_subscribe_on_assign(
                issue.id,
                issue.assignee_id,
            )
            # Send notification to assignee
            await self.notification_service.send_notification(
                user_id=issue.assignee_id,
                notification_type=NotificationType.ISSUE_ASSIGNED,
                title=f"You were assigned to {issue.issue_key}",
                message=f"Issue: {issue.title}",
                issue_id=issue.id,
                project_id=issue.project_id,
            )

        # Link to feature if provided
        if feature_id:
            await self._link_issue_to_feature(
                issue.id,
                feature_id,
                feature_link_type,
                reporter_id,
            )

        # TODO: Assign labels

        return issue

    async def _link_issue_to_feature(
        self,
        issue_id: str,
        feature_id: str,
        link_type: str,
        created_by: str,
    ) -> None:
        """Link an issue to a feature."""
        try:
            link_type_enum = FeatureIssueLinkType(link_type)
        except ValueError:
            link_type_enum = FeatureIssueLinkType.IMPLEMENTS

        link = FeatureIssueLink(
            feature_id=feature_id,
            issue_id=issue_id,
            link_type=link_type_enum,
            created_by=created_by,
        )
        self.db.add(link)
        await self.db.commit()

    async def get_issue(self, issue_id: str) -> Issue:
        """Get issue by ID with details."""
        issue = await self.issue_repo.get_with_details(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")
        return issue

    async def get_issue_by_key(self, issue_key: str) -> Issue:
        """Get issue by key (e.g., TRAK-123)."""
        issue = await self.issue_repo.get_by_key(issue_key)
        if not issue:
            raise NotFoundError(f"Issue {issue_key} not found")
        return issue

    async def list_issues(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        assignee_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        include_backlog: bool = False,
        exclude_completed_sprints: bool = False,
    ) -> List[Issue]:
        """List issues in a project with optional filters.

        Args:
            sprint_id: Filter by specific sprint. Use 'null' string to get backlog items.
            include_backlog: If True and sprint_id is None, only return issues with no sprint assigned.
            exclude_completed_sprints: If True, excludes issues from completed sprints (shows active sprints + backlog).
        """
        status_enum = None
        type_enum = None

        if status:
            try:
                status_enum = IssueStatus(status)
            except ValueError:
                pass

        if issue_type:
            try:
                type_enum = IssueType(issue_type)
            except ValueError:
                pass

        return await self.issue_repo.get_by_project(
            project_id,
            skip=skip,
            limit=limit,
            status=status_enum,
            issue_type=type_enum,
            assignee_id=assignee_id,
            sprint_id=sprint_id,
            include_backlog=include_backlog,
            exclude_completed_sprints=exclude_completed_sprints,
        )

    async def update_issue(
        self,
        issue_id: str,
        issue_data: Dict[str, Any],
        updated_by: str,
    ) -> Issue:
        """Update an existing issue."""
        issue = await self.issue_repo.get(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")

        # Validate sprint assignment - prevent assignment to completed sprints
        if "sprint_id" in issue_data and issue_data["sprint_id"]:
            from app.repositories.sprint import SprintRepository
            sprint_repo = SprintRepository(self.db)
            target_sprint = await sprint_repo.get(issue_data["sprint_id"])
            if target_sprint and target_sprint.is_completed:
                raise ValidationError("Cannot assign issues to a closed/completed sprint")

        # Capture old values for activity logging
        old_values = {}
        new_values = {}
        for field, value in issue_data.items():
            if hasattr(issue, field):
                old_val = getattr(issue, field)
                # Convert enums to values for comparison
                if hasattr(old_val, 'value'):
                    old_values[field] = old_val.value
                else:
                    old_values[field] = str(old_val) if old_val else None

                # Store new value
                if hasattr(value, 'value'):
                    new_values[field] = value.value
                else:
                    new_values[field] = str(value) if value else None

        # Handle issue type changes
        if "issue_type" in issue_data:
            new_type = IssueType(issue_data["issue_type"])
            issue_data["issue_type"] = new_type

        # Handle status changes
        if "status" in issue_data:
            new_status = IssueStatus(issue_data["status"])
            issue_data["status"] = new_status

            # Set resolution timestamp
            if new_status in [IssueStatus.DONE, IssueStatus.CLOSED]:
                if not issue.resolved_at:
                    issue_data["resolved_at"] = datetime.utcnow()
                    issue_data["resolved_by"] = updated_by

        # Handle label updates
        label_ids = issue_data.pop("label_ids", None)

        # Auto-subscribe new assignee if changed
        assignee_changed = False
        if "assignee_id" in issue_data and issue_data["assignee_id"]:
            if issue_data["assignee_id"] != issue.assignee_id:
                assignee_changed = True
                await self.watcher_service.auto_subscribe_on_assign(
                    issue_id,
                    issue_data["assignee_id"],
                )

        updated_issue = await self.issue_repo.update(issue_id, issue_data)

        # Log activity
        if old_values or new_values:
            await self.activity_service.log_issue_updated(
                issue_id=issue.id,
                organization_id=issue.organization_id,
                user_id=updated_by,
                old_values=old_values,
                new_values=new_values,
            )

        # Send notification if assignee changed
        if assignee_changed:
            await self.notification_service.send_notification(
                user_id=issue_data["assignee_id"],
                notification_type=NotificationType.ISSUE_ASSIGNED,
                title=f"You were assigned to {issue.issue_key}",
                message=f"Issue: {issue.title}",
                issue_id=issue.id,
                project_id=issue.project_id,
            )

        # TODO: Update labels if provided

        # Fetch issue with all relationships loaded for proper serialization
        updated_issue_with_details = await self.issue_repo.get_with_details(issue_id)
        return updated_issue_with_details if updated_issue_with_details else updated_issue

    async def delete_issue(self, issue_id: str) -> bool:
        """Delete an issue."""
        issue = await self.issue_repo.get(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")

        return await self.issue_repo.delete(issue_id)

    async def check_duplicates(
        self,
        project_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check for duplicate issues before creation.

        Returns similar issues and suggested deduplication hash.
        """
        # Generate hash
        dedup_hash = self.dedup_service.generate_deduplication_hash(title, description)

        # Find similar issues
        similar = await self.dedup_service.find_similar_issues(
            project_id,
            title,
            description,
        )

        # Determine if likely duplicate
        is_likely_duplicate = any(s["similarity_score"] >= 70 for s in similar)

        return {
            "similar_issues": [
                {
                    "id": s["issue"].id,
                    "issue_key": s["issue"].issue_key,
                    "title": s["issue"].title,
                    "status": s["issue"].status.value,
                    "issue_type": s["issue"].issue_type.value,
                    "similarity_score": s["similarity_score"],
                    "created_at": s["issue"].created_at,
                }
                for s in similar
            ],
            "suggested_deduplication_hash": dedup_hash,
            "is_likely_duplicate": is_likely_duplicate,
        }

    async def search_issues(
        self,
        project_id: str,
        query: str,
        limit: int = 20,
    ) -> List[Issue]:
        """Search issues by title or description."""
        return await self.issue_repo.search(project_id, query, limit)

    async def add_checklist_item(
        self,
        checklist_id: str,
        content: str,
        position: int,
        description: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> ChecklistItem:
        """Add a checklist item to a checklist."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        item = ChecklistItem(
            checklist_id=checklist_id,
            content=content,
            description=description,
            assignee_id=assignee_id,
            position=position,
            is_completed=False,
        )

        self.db.add(item)
        await self.db.commit()

        # Fetch with assignee relationship eagerly loaded
        result = await self.db.execute(
            select(ChecklistItem)
            .where(ChecklistItem.id == item.id)
            .options(selectinload(ChecklistItem.assignee))
        )
        refreshed_item = result.scalar_one()

        return refreshed_item

    async def update_checklist_item(
        self,
        checklist_id: str,
        item_id: str,
        data: Dict[str, Any],
    ) -> ChecklistItem:
        """
        Update a checklist item.

        Enforces status workflow: pending → in_progress → dev_done → qa_checked
        Once qa_checked, item is locked and cannot be modified.
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Fetch item with assignee eagerly loaded
        result = await self.db.execute(
            select(ChecklistItem)
            .where(ChecklistItem.id == item_id)
            .options(selectinload(ChecklistItem.assignee))
        )
        item = result.scalar_one_or_none()

        if not item or item.checklist_id != checklist_id:
            raise NotFoundError("Checklist item not found")

        # Check if item is locked (qa_checked status)
        if not item.can_update_status():
            raise ValidationError(
                "Cannot update item: status is 'qa_checked' and locked. "
                "QA-checked items cannot be modified."
            )

        # Validate status transitions if status is being updated
        if "status" in data and data["status"]:
            new_status = data["status"]
            current_status = item.status

            # Define valid transitions
            valid_transitions = {
                "pending": ["in_progress"],
                "in_progress": ["dev_done", "pending"],  # Can go back to pending
                "dev_done": ["qa_checked", "in_progress"],  # Can go back to in_progress
                "qa_checked": [],  # No transitions allowed from qa_checked
            }

            # Check if transition is valid
            if new_status != current_status:
                if new_status not in valid_transitions.get(current_status, []):
                    raise ValidationError(
                        f"Invalid status transition: '{current_status}' → '{new_status}'. "
                        f"Valid transitions from '{current_status}': {', '.join(valid_transitions.get(current_status, [])) or 'none'}"
                    )

        # Apply updates
        for key, value in data.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        await self.db.commit()

        # Refresh with assignee relationship loaded
        result = await self.db.execute(
            select(ChecklistItem)
            .where(ChecklistItem.id == item_id)
            .options(selectinload(ChecklistItem.assignee))
        )
        refreshed_item = result.scalar_one()

        return refreshed_item

    async def delete_checklist_item(
        self,
        checklist_id: str,
        item_id: str,
    ) -> bool:
        """Delete a checklist item."""
        item = await self.db.get(ChecklistItem, item_id)
        if not item or item.checklist_id != checklist_id:
            raise NotFoundError("Checklist item not found")

        await self.db.delete(item)
        await self.db.commit()
        return True

    async def create_checklist(
        self,
        issue_id: str,
        name: str,
        position: int = 0,
    ) -> "Checklist":
        """Create a new named checklist for an issue."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        checklist = Checklist(
            issue_id=issue_id,
            name=name,
            position=position,
        )
        self.db.add(checklist)
        await self.db.commit()

        # Fetch with items and their assignees eagerly loaded
        result = await self.db.execute(
            select(Checklist)
            .where(Checklist.id == checklist.id)
            .options(
                selectinload(Checklist.items).selectinload(ChecklistItem.assignee)
            )
        )
        refreshed_checklist = result.scalar_one()

        return refreshed_checklist

    async def update_checklist(
        self,
        checklist_id: str,
        name: Optional[str] = None,
        position: Optional[int] = None,
    ) -> "Checklist":
        """Update a checklist's metadata."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Fetch checklist with items and their assignees eagerly loaded
        result = await self.db.execute(
            select(Checklist)
            .where(Checklist.id == checklist_id)
            .options(
                selectinload(Checklist.items).selectinload(ChecklistItem.assignee)
            )
        )
        checklist = result.scalar_one_or_none()

        if not checklist:
            raise NotFoundError("Checklist not found")

        if name is not None:
            checklist.name = name
        if position is not None:
            checklist.position = position

        await self.db.commit()

        # Fetch again with relationships loaded after update
        result = await self.db.execute(
            select(Checklist)
            .where(Checklist.id == checklist_id)
            .options(
                selectinload(Checklist.items).selectinload(ChecklistItem.assignee)
            )
        )
        refreshed_checklist = result.scalar_one()

        return refreshed_checklist


    async def delete_checklist(self, checklist_id: str) -> bool:
        """Delete an entire checklist and its items."""
        checklist = await self.db.get(Checklist, checklist_id)
        if not checklist:
            raise NotFoundError("Checklist not found")

        await self.db.delete(checklist)
        await self.db.commit()
        return True

