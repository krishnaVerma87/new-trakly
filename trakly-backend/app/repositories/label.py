"""Label repository."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label import Label
from app.repositories.base import BaseRepository


class LabelRepository(BaseRepository[Label]):
    """Repository for Label operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Label, db)

    async def get_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Label]:
        """Get all labels in a project."""
        result = await self.db.execute(
            select(Label)
            .where(Label.project_id == project_id)
            .order_by(Label.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(
        self,
        project_id: str,
        name: str,
    ) -> Optional[Label]:
        """Get label by name within a project."""
        result = await self.db.execute(
            select(Label)
            .where(Label.project_id == project_id)
            .where(Label.name == name)
        )
        return result.scalar_one_or_none()
