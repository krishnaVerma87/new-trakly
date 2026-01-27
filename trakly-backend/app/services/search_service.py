"""Service for advanced search and saved searches."""
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.issue import Issue
from app.models.saved_search import SavedSearch
from app.repositories.issue import IssueRepository
from app.repositories.saved_search import SavedSearchRepository
from app.repositories.project import ProjectRepository

logger = logging.getLogger(__name__)


class SearchService:
    """Service for advanced issue search and saved searches."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.issue_repo = IssueRepository(db)
        self.saved_search_repo = SavedSearchRepository(db)
        self.project_repo = ProjectRepository(db)

    async def advanced_search(
        self,
        project_id: str,
        filter_config: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Issue]:
        """
        Execute advanced search with complex filters.

        Supports filtering by:
        - status, priority, severity, issue_type
        - assignee_id, reporter_id, component_id, sprint_id
        - labels, is_regression, is_duplicate
        - created_after/before, updated_after/before
        - story_points_min/max
        - text_search (title, description, issue_key)
        """
        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Execute advanced search
        return await self.issue_repo.filter_by_criteria(
            project_id=project_id,
            filter_config=filter_config,
            skip=skip,
            limit=limit,
        )

    async def save_search(
        self,
        project_id: str,
        name: str,
        filter_config: Dict[str, Any],
        created_by: str,
        description: str = None,
        is_shared: bool = False,
    ) -> SavedSearch:
        """
        Save a search for reuse.

        Prevents duplicate names for the same user in the same project.
        """
        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Check for duplicate name
        existing = await self.saved_search_repo.get_by_name(
            project_id=project_id,
            name=name,
            user_id=created_by,
        )
        if existing:
            raise ValidationError(f"Saved search with name '{name}' already exists")

        # Validate filter config (basic validation)
        if not filter_config:
            raise ValidationError("Filter configuration cannot be empty")

        # Create saved search
        search_data = {
            "project_id": project_id,
            "created_by": created_by,
            "name": name,
            "description": description,
            "filter_config": filter_config,
            "is_shared": is_shared,
        }

        return await self.saved_search_repo.create(search_data)

    async def execute_saved_search(
        self,
        search_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Issue]:
        """Load saved search and execute it."""
        saved_search = await self.saved_search_repo.get(search_id)
        if not saved_search:
            raise NotFoundError("Saved search not found")

        return await self.advanced_search(
            project_id=saved_search.project_id,
            filter_config=saved_search.filter_config,
            skip=skip,
            limit=limit,
        )

    async def get_saved_searches(
        self,
        project_id: str,
        user_id: str,
    ) -> List[SavedSearch]:
        """Get all saved searches for a user (personal + shared)."""
        return await self.saved_search_repo.get_for_user(
            project_id=project_id,
            user_id=user_id,
        )

    async def get_saved_search(self, search_id: str) -> SavedSearch:
        """Get a single saved search by ID."""
        saved_search = await self.saved_search_repo.get(search_id)
        if not saved_search:
            raise NotFoundError("Saved search not found")
        return saved_search

    async def update_saved_search(
        self,
        search_id: str,
        user_id: str,
        name: str = None,
        description: str = None,
        filter_config: Dict[str, Any] = None,
        is_shared: bool = None,
    ) -> SavedSearch:
        """Update a saved search (only creator can update)."""
        saved_search = await self.saved_search_repo.get(search_id)
        if not saved_search:
            raise NotFoundError("Saved search not found")

        # Verify ownership
        if saved_search.created_by != user_id:
            raise PermissionDeniedError("You can only update your own saved searches")

        # Build update data
        update_data = {}
        if name is not None:
            # Check for duplicate name
            existing = await self.saved_search_repo.get_by_name(
                project_id=saved_search.project_id,
                name=name,
                user_id=user_id,
            )
            if existing and existing.id != search_id:
                raise ValidationError(f"Saved search with name '{name}' already exists")
            update_data["name"] = name

        if description is not None:
            update_data["description"] = description
        if filter_config is not None:
            if not filter_config:
                raise ValidationError("Filter configuration cannot be empty")
            update_data["filter_config"] = filter_config
        if is_shared is not None:
            update_data["is_shared"] = is_shared

        return await self.saved_search_repo.update(search_id, update_data)

    async def delete_saved_search(
        self,
        search_id: str,
        user_id: str,
    ) -> None:
        """Delete a saved search (only creator can delete)."""
        saved_search = await self.saved_search_repo.get(search_id)
        if not saved_search:
            raise NotFoundError("Saved search not found")

        # Verify ownership
        if saved_search.created_by != user_id:
            raise PermissionDeniedError("You can only delete your own saved searches")

        await self.saved_search_repo.delete(search_id)
