"""Feature repository."""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature import Feature, FeatureStatus
from app.repositories.base import BaseRepository


class FeatureRepository(BaseRepository[Feature]):
    """Repository for Feature operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Feature, db)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[FeatureStatus] = None,
    ) -> List[Feature]:
        """Get all features in a project."""
        query = (
            select(Feature)
            .where(Feature.project_id == project_id)
            .options(
                selectinload(Feature.owner),
                selectinload(Feature.component),
                selectinload(Feature.issue_links),
            )
        )

        if status:
            query = query.where(Feature.status == status)

        query = query.order_by(Feature.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_next_feature_number(self, project_id: str) -> int:
        """Get next feature number for a project."""
        result = await self.db.execute(
            select(func.max(Feature.feature_number))
            .where(Feature.project_id == project_id)
        )
        max_number = result.scalar_one_or_none()
        return (max_number or 0) + 1

    async def get_with_issues(self, feature_id: str) -> Optional[Feature]:
        """Get feature with linked issues loaded."""
        result = await self.db.execute(
            select(Feature)
            .where(Feature.id == feature_id)
            .options(
                selectinload(Feature.owner),
                selectinload(Feature.component),
                selectinload(Feature.issue_links),
                selectinload(Feature.comments),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feature]:
        """Get all features in an organization."""
        result = await self.db.execute(
            select(Feature)
            .where(Feature.organization_id == organization_id)
            .options(selectinload(Feature.project))
            .order_by(Feature.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
