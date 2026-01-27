"""Repository for saved search operations."""
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_search import SavedSearch
from app.repositories.base import BaseRepository


class SavedSearchRepository(BaseRepository[SavedSearch]):
    """Repository for SavedSearch operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(SavedSearch, db)

    async def get_for_user(
        self,
        project_id: str,
        user_id: str,
    ) -> List[SavedSearch]:
        """Get all saved searches for a user (personal + shared)."""
        result = await self.db.execute(
            select(SavedSearch)
            .where(SavedSearch.project_id == project_id)
            .where(
                or_(
                    SavedSearch.created_by == user_id,  # Personal searches
                    SavedSearch.is_shared == True,  # Shared searches
                )
            )
            .options(
                selectinload(SavedSearch.creator),
                selectinload(SavedSearch.project),
            )
            .order_by(SavedSearch.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_personal_searches(
        self,
        user_id: str,
    ) -> List[SavedSearch]:
        """Get only personal (non-shared) searches for a user."""
        result = await self.db.execute(
            select(SavedSearch)
            .where(SavedSearch.created_by == user_id)
            .where(SavedSearch.is_shared == False)
            .options(
                selectinload(SavedSearch.creator),
                selectinload(SavedSearch.project),
            )
            .order_by(SavedSearch.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_shared_searches(
        self,
        project_id: str,
    ) -> List[SavedSearch]:
        """Get all shared searches for a project."""
        result = await self.db.execute(
            select(SavedSearch)
            .where(SavedSearch.project_id == project_id)
            .where(SavedSearch.is_shared == True)
            .options(
                selectinload(SavedSearch.creator),
                selectinload(SavedSearch.project),
            )
            .order_by(SavedSearch.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_name(
        self,
        project_id: str,
        name: str,
        user_id: str,
    ) -> Optional[SavedSearch]:
        """Check if a saved search with this name already exists for the user."""
        result = await self.db.execute(
            select(SavedSearch)
            .where(SavedSearch.project_id == project_id)
            .where(SavedSearch.created_by == user_id)
            .where(SavedSearch.name == name)
        )
        return result.scalar_one_or_none()
