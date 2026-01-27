"""Activity repository."""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity, EntityType
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Activity, db)

    async def get_for_entity(
        self,
        entity_type: EntityType,
        entity_id: str,
        limit: int = 50,
    ) -> List[Activity]:
        """Get activities for a specific entity."""
        result = await self.db.execute(
            select(Activity)
            .where(Activity.entity_type == entity_type)
            .where(Activity.entity_id == entity_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
