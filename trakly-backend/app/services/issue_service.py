"""Issue management service."""
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.issue import Issue, IssueStatus, IssueType
from app.models.feature_issue_link import FeatureIssueLink, FeatureIssueLinkType
from app.repositories.issue import IssueRepository
from app.repositories.project import ProjectRepository
from app.repositories.feature import FeatureRepository
from app.services.duplicate_detection_service import DuplicateDetectionService


class IssueService:
    """Service for issue operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.issue_repo = IssueRepository(db)
        self.project_repo = ProjectRepository(db)
        self.feature_repo = FeatureRepository(db)
        self.dedup_service = DuplicateDetectionService(db)

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
    ) -> List[Issue]:
        """List issues in a project with optional filters."""
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

        updated_issue = await self.issue_repo.update(issue_id, issue_data)

        # TODO: Update labels if provided

        return updated_issue

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
