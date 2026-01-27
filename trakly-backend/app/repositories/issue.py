"""Issue repository with duplicate detection support."""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue, IssueStatus, IssueType, Priority, Severity
from app.models.label import issue_labels
from app.models.sprint import Sprint
from app.repositories.base import BaseRepository


class IssueRepository(BaseRepository[Issue]):
    """Repository for Issue operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Issue, db)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[IssueStatus] = None,
        issue_type: Optional[IssueType] = None,
        assignee_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        include_backlog: bool = False,
        exclude_completed_sprints: bool = False,
    ) -> List[Issue]:
        """Get issues in a project with optional filters.

        Args:
            sprint_id: Filter by specific sprint. Use 'null' string to get backlog items.
            include_backlog: If True and sprint_id is None, only return issues with no sprint assigned.
            exclude_completed_sprints: If True, excludes issues from completed sprints (shows active sprints + backlog).
        """
        from app.models.sprint import Sprint

        query = (
            select(Issue)
            .where(Issue.project_id == project_id)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
                selectinload(Issue.labels),
                selectinload(Issue.component),
            )
        )

        if status:
            query = query.where(Issue.status == status)
        if issue_type:
            query = query.where(Issue.issue_type == issue_type)
        if assignee_id:
            query = query.where(Issue.assignee_id == assignee_id)

        # Sprint filtering
        if sprint_id == 'null' or (sprint_id is None and include_backlog):
            # Get backlog items (no sprint assigned)
            query = query.where(Issue.sprint_id.is_(None))
        elif sprint_id:
            # Get specific sprint items
            query = query.where(Issue.sprint_id == sprint_id)
        elif exclude_completed_sprints:
            # Get all issues from active/planned sprints + backlog (exclude completed sprints)
            query = query.outerjoin(Sprint, Issue.sprint_id == Sprint.id).where(
                or_(
                    Issue.sprint_id.is_(None),  # Backlog items
                    Sprint.is_completed == False  # Active or planned sprints only (not completed)
                )
            )

        query = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_key(self, issue_key: str) -> Optional[Issue]:
        """Get issue by its key (e.g., TRAK-123)."""
        result = await self.db.execute(
            select(Issue)
            .where(Issue.issue_key == issue_key)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
                selectinload(Issue.labels),
                selectinload(Issue.component),
                selectinload(Issue.feature_links),
                selectinload(Issue.comments),
            )
        )
        return result.scalar_one_or_none()

    async def get_next_issue_number(self, project_id: str) -> int:
        """Get next issue number for a project (atomic)."""
        result = await self.db.execute(
            select(func.max(Issue.issue_number))
            .where(Issue.project_id == project_id)
        )
        max_number = result.scalar_one_or_none()
        return (max_number or 0) + 1

    async def get_with_details(self, issue_id: str) -> Optional[Issue]:
        """Get issue with all related data loaded."""
        from app.models.issue import Checklist, ChecklistItem
        from app.models.user import User

        result = await self.db.execute(
            select(Issue)
            .where(Issue.id == issue_id)
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
                selectinload(Issue.labels),
                selectinload(Issue.component),
                selectinload(Issue.feature_links),
                selectinload(Issue.source_links),
                selectinload(Issue.target_links),
                selectinload(Issue.comments),
                selectinload(Issue.parent_issue),
                selectinload(Issue.sub_tasks),
                selectinload(Issue.checklists).selectinload(Checklist.items).selectinload(ChecklistItem.assignee),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_deduplication_hash(
        self,
        project_id: str,
        dedup_hash: str,
    ) -> Optional[Issue]:
        """Find issue by deduplication hash within a project."""
        result = await self.db.execute(
            select(Issue)
            .where(Issue.project_id == project_id)
            .where(Issue.deduplication_hash == dedup_hash)
            .where(Issue.is_duplicate == False)
        )
        return result.scalar_one_or_none()

    async def get_bugs_by_feature(
        self,
        feature_id: str,
    ) -> List[Issue]:
        """Get all bugs linked to a feature."""
        from app.models.feature_issue_link import FeatureIssueLink

        result = await self.db.execute(
            select(Issue)
            .join(FeatureIssueLink, Issue.id == FeatureIssueLink.issue_id)
            .where(FeatureIssueLink.feature_id == feature_id)
            .where(Issue.issue_type == IssueType.BUG)
            .options(selectinload(Issue.assignee))
        )
        return list(result.scalars().all())

    async def search(
        self,
        project_id: str,
        query: str,
        limit: int = 20,
    ) -> List[Issue]:
        """Search issues by title or description."""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Issue)
            .where(Issue.project_id == project_id)
            .where(
                or_(
                    Issue.title.ilike(search_pattern),
                    Issue.description.ilike(search_pattern),
                    Issue.issue_key.ilike(search_pattern),
                )
            )
            .options(
                selectinload(Issue.reporter),
                selectinload(Issue.assignee),
            )
            .order_by(Issue.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_open_issues_for_project(
        self,
        project_id: str,
    ) -> List[Issue]:
        """Get all non-closed issues for duplicate detection corpus."""
        result = await self.db.execute(
            select(Issue)
            .where(Issue.project_id == project_id)
            .where(Issue.status.not_in([IssueStatus.CLOSED, IssueStatus.DONE, IssueStatus.WONT_FIX]))
            .where(Issue.is_duplicate == False)
        )
        return list(result.scalars().all())

    async def filter_by_criteria(
        self,
        project_id: str,
        filter_config: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Issue]:
        """Apply advanced filters using IssueFilterBuilder."""
        builder = IssueFilterBuilder(project_id)

        # Apply all filters from config
        if "status" in filter_config:
            builder.add_status_filter(filter_config["status"])
        if "priority" in filter_config:
            builder.add_priority_filter(filter_config["priority"])
        if "severity" in filter_config:
            builder.add_severity_filter(filter_config["severity"])
        if "issue_type" in filter_config:
            builder.add_issue_type_filter(filter_config["issue_type"])
        if "assignee_id" in filter_config:
            builder.add_assignee_filter(filter_config["assignee_id"])
        if "reporter_id" in filter_config:
            builder.add_reporter_filter(filter_config["reporter_id"])
        if "component_id" in filter_config:
            builder.add_component_filter(filter_config["component_id"])
        if "sprint_id" in filter_config:
            builder.add_sprint_filter(filter_config["sprint_id"])
        if "labels" in filter_config:
            builder.add_label_filter(filter_config["labels"])
        if "is_regression" in filter_config:
            builder.add_regression_filter(filter_config["is_regression"])
        if "is_duplicate" in filter_config:
            builder.add_duplicate_filter(filter_config["is_duplicate"])
        if "created_after" in filter_config:
            builder.add_created_after_filter(filter_config["created_after"])
        if "created_before" in filter_config:
            builder.add_created_before_filter(filter_config["created_before"])
        if "updated_after" in filter_config:
            builder.add_updated_after_filter(filter_config["updated_after"])
        if "updated_before" in filter_config:
            builder.add_updated_before_filter(filter_config["updated_before"])
        if "story_points_min" in filter_config:
            builder.add_story_points_min_filter(filter_config["story_points_min"])
        if "story_points_max" in filter_config:
            builder.add_story_points_max_filter(filter_config["story_points_max"])
        if "text_search" in filter_config:
            builder.add_text_search(filter_config["text_search"])

        # Build and execute query
        query = builder.build().offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class IssueFilterBuilder:
    """Build complex SQLAlchemy queries from filter configuration."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.query = select(Issue).where(Issue.project_id == project_id)
        self.filters = []

    def add_status_filter(self, statuses: List[str]) -> "IssueFilterBuilder":
        """Filter by issue status."""
        if statuses:
            status_enums = [IssueStatus(s) for s in statuses]
            self.filters.append(Issue.status.in_(status_enums))
        return self

    def add_priority_filter(self, priorities: List[str]) -> "IssueFilterBuilder":
        """Filter by priority."""
        if priorities:
            priority_enums = [Priority(p) for p in priorities]
            self.filters.append(Issue.priority.in_(priority_enums))
        return self

    def add_severity_filter(self, severities: List[str]) -> "IssueFilterBuilder":
        """Filter by severity."""
        if severities:
            severity_enums = [Severity(s) for s in severities]
            self.filters.append(Issue.severity.in_(severity_enums))
        return self

    def add_issue_type_filter(self, issue_types: List[str]) -> "IssueFilterBuilder":
        """Filter by issue type."""
        if issue_types:
            type_enums = [IssueType(t) for t in issue_types]
            self.filters.append(Issue.issue_type.in_(type_enums))
        return self

    def add_assignee_filter(self, assignee_ids: List[str]) -> "IssueFilterBuilder":
        """Filter by assignee ID(s)."""
        if assignee_ids:
            self.filters.append(Issue.assignee_id.in_(assignee_ids))
        return self

    def add_reporter_filter(self, reporter_ids: List[str]) -> "IssueFilterBuilder":
        """Filter by reporter ID(s)."""
        if reporter_ids:
            self.filters.append(Issue.reporter_id.in_(reporter_ids))
        return self

    def add_component_filter(self, component_ids: List[str]) -> "IssueFilterBuilder":
        """Filter by component ID(s)."""
        if component_ids:
            self.filters.append(Issue.component_id.in_(component_ids))
        return self

    def add_sprint_filter(self, sprint_id: str) -> "IssueFilterBuilder":
        """Filter by sprint ID or 'current'."""
        if sprint_id == "current":
            from app.models.sprint import Sprint
            from datetime import datetime
            now = datetime.utcnow()
            # Join with sprint table to find current sprint
            self.query = self.query.join(Sprint, Issue.sprint_id == Sprint.id)
            self.filters.append(Sprint.start_date <= now)
            self.filters.append(Sprint.end_date >= now)
        elif sprint_id:
            self.filters.append(Issue.sprint_id == sprint_id)
        return self

    def add_label_filter(self, label_ids: List[str]) -> "IssueFilterBuilder":
        """Filter by label IDs (issues must have ALL specified labels)."""
        if label_ids:
            # Join with issue_labels table for each label
            self.query = self.query.join(issue_labels, Issue.id == issue_labels.c.issue_id)
            self.filters.append(issue_labels.c.label_id.in_(label_ids))
        return self

    def add_regression_filter(self, is_regression: bool) -> "IssueFilterBuilder":
        """Filter by regression status."""
        self.filters.append(Issue.is_regression == is_regression)
        return self

    def add_duplicate_filter(self, is_duplicate: bool) -> "IssueFilterBuilder":
        """Filter by duplicate status."""
        self.filters.append(Issue.is_duplicate == is_duplicate)
        return self

    def add_created_after_filter(self, date: str) -> "IssueFilterBuilder":
        """Filter issues created after date."""
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        self.filters.append(Issue.created_at >= dt)
        return self

    def add_created_before_filter(self, date: str) -> "IssueFilterBuilder":
        """Filter issues created before date."""
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        self.filters.append(Issue.created_at <= dt)
        return self

    def add_updated_after_filter(self, date: str) -> "IssueFilterBuilder":
        """Filter issues updated after date."""
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        self.filters.append(Issue.updated_at >= dt)
        return self

    def add_updated_before_filter(self, date: str) -> "IssueFilterBuilder":
        """Filter issues updated before date."""
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        self.filters.append(Issue.updated_at <= dt)
        return self

    def add_story_points_min_filter(self, min_points: int) -> "IssueFilterBuilder":
        """Filter by minimum story points."""
        self.filters.append(Issue.story_points >= min_points)
        return self

    def add_story_points_max_filter(self, max_points: int) -> "IssueFilterBuilder":
        """Filter by maximum story points."""
        self.filters.append(Issue.story_points <= max_points)
        return self

    def add_text_search(self, text: str) -> "IssueFilterBuilder":
        """Full-text search on title, description, issue_key."""
        search_pattern = f"%{text}%"
        self.filters.append(
            or_(
                Issue.title.ilike(search_pattern),
                Issue.description.ilike(search_pattern),
                Issue.issue_key.ilike(search_pattern),
            )
        )
        return self

    def build(self) -> select:
        """Build the final query with all filters and relationships."""
        # Apply all filters
        if self.filters:
            self.query = self.query.where(and_(*self.filters))

        # Load relationships
        self.query = self.query.options(
            selectinload(Issue.reporter),
            selectinload(Issue.assignee),
            selectinload(Issue.labels),
            selectinload(Issue.component),
            selectinload(Issue.sprint),
        ).order_by(Issue.created_at.desc())

        return self.query
