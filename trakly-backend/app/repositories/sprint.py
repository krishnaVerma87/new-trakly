"""Sprint repository."""
from typing import List, Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.sprint import Sprint
from app.repositories.base import BaseRepository


class SprintRepository(BaseRepository[Sprint]):
    """Repository for Sprint operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Sprint, db)

    async def get_next_sprint_number(self, project_id: str) -> int:
        """Get next sprint number for a project."""
        result = await self.db.execute(
            select(func.max(Sprint.sprint_number))
            .where(Sprint.project_id == project_id)
        )
        max_number = result.scalar_one_or_none()
        return (max_number or 0) + 1

    async def get_current_sprint(self, project_id: str) -> Optional[Sprint]:
        """Get the active sprint for a project."""
        result = await self.db.execute(
            select(Sprint)
            .where(Sprint.project_id == project_id)
            .where(Sprint.is_active == True)
            .where(Sprint.is_completed == False)
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: str,
        include_completed: bool = False,
    ) -> List[Sprint]:
        """Get sprints for a project."""
        query = select(Sprint).where(Sprint.project_id == project_id)

        if not include_completed:
            query = query.where(Sprint.is_completed == False)

        query = query.order_by(Sprint.start_date.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def deactivate_all(self, project_id: str) -> None:
        """Deactivate all sprints in a project."""
        await self.db.execute(
            update(Sprint)
            .where(Sprint.project_id == project_id)
            .values(is_active=False)
        )
        await self.db.commit()
