"""Issue repository with duplicate detection support."""
from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue, IssueStatus, IssueType
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
    ) -> List[Issue]:
        """Get issues in a project with optional filters."""
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
