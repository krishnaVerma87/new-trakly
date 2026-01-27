"""Service for saved search operations."""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_search import SavedSearch
from app.repositories.saved_search import SavedSearchRepository
from app.core.exceptions import NotFoundError, ValidationError


class SavedSearchService:
    """Service for managing saved searches."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.saved_search_repo = SavedSearchRepository(db)

    async def create_saved_search(
        self,
        project_id: str,
        user_id: str,
        name: str,
        filter_config: Dict[str, Any],
        description: Optional[str] = None,
        is_shared: bool = False,
    ) -> SavedSearch:
        """Create a new saved search."""
        # Check if name already exists for this user
        existing = await self.saved_search_repo.get_by_name(project_id, name, user_id)
        if existing:
            raise ValidationError(f"A saved search named '{name}' already exists.")

        search_data = {
            "project_id": project_id,
            "created_by": user_id,
            "name": name,
            "description": description,
            "filter_config": filter_config,
            "is_shared": is_shared,
        }

        return await self.saved_search_repo.create(search_data)

    async def get_saved_search(self, search_id: str, user_id: str) -> SavedSearch:
        """Get a saved search by ID."""
        search = await self.saved_search_repo.get(search_id)
        if not search:
            raise NotFoundError("Saved search not found")

        # Check permissions: user must be creator or it must be shared
        if search.created_by != user_id and not search.is_shared:
            raise NotFoundError("Saved search not found")

        return search

    async def get_user_searches(
        self,
        project_id: str,
        user_id: str,
    ) -> List[SavedSearch]:
        """Get all saved searches available to a user (personal + shared)."""
        return await self.saved_search_repo.get_for_user(project_id, user_id)

    async def get_shared_searches(self, project_id: str) -> List[SavedSearch]:
        """Get all shared searches for a project."""
        return await self.saved_search_repo.get_shared_searches(project_id)

    async def update_saved_search(
        self,
        search_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        filter_config: Optional[Dict[str, Any]] = None,
        is_shared: Optional[bool] = None,
    ) -> SavedSearch:
        """Update a saved search."""
        search = await self.saved_search_repo.get(search_id)
        if not search:
            raise NotFoundError("Saved search not found")

        # Only the creator can update
        if search.created_by != user_id:
            raise ValidationError("You can only update your own saved searches")

        # Check if new name conflicts with existing
        if name and name != search.name:
            existing = await self.saved_search_repo.get_by_name(
                search.project_id, name, user_id
            )
            if existing:
                raise ValidationError(f"A saved search named '{name}' already exists.")

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if filter_config is not None:
            update_data["filter_config"] = filter_config
        if is_shared is not None:
            update_data["is_shared"] = is_shared

        return await self.saved_search_repo.update(search_id, update_data)

    async def delete_saved_search(self, search_id: str, user_id: str) -> None:
        """Delete a saved search."""
        search = await self.saved_search_repo.get(search_id)
        if not search:
            raise NotFoundError("Saved search not found")

        # Only the creator can delete
        if search.created_by != user_id:
            raise ValidationError("You can only delete your own saved searches")

        await self.saved_search_repo.delete(search_id)
