"""Saved search endpoints."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.saved_search_service import SavedSearchService

router = APIRouter(prefix="/saved-searches", tags=["Saved Searches"])


class SavedSearchCreate(BaseModel):
    """Schema for creating a saved search."""
    project_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    filter_config: Dict[str, Any]
    is_shared: bool = False


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    filter_config: Dict[str, Any] | None = None
    is_shared: bool | None = None


class SavedSearchResponse(BaseModel):
    """Schema for saved search response."""
    id: str
    project_id: str
    created_by: str
    name: str
    description: str | None
    filter_config: Dict[str, Any]
    is_shared: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    search_data: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new saved search."""
    service = SavedSearchService(db)
    try:
        saved_search = await service.create_saved_search(
            project_id=search_data.project_id,
            user_id=current_user.id,
            name=search_data.name,
            filter_config=search_data.filter_config,
            description=search_data.description,
            is_shared=search_data.is_shared,
        )
        return SavedSearchResponse(
            id=saved_search.id,
            project_id=saved_search.project_id,
            created_by=saved_search.created_by,
            name=saved_search.name,
            description=saved_search.description,
            filter_config=saved_search.filter_config,
            is_shared=saved_search.is_shared,
            created_at=saved_search.created_at.isoformat(),
            updated_at=saved_search.updated_at.isoformat(),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/project/{project_id}", response_model=List[SavedSearchResponse])
async def get_project_searches(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all saved searches for a project (personal + shared)."""
    service = SavedSearchService(db)
    searches = await service.get_user_searches(project_id, current_user.id)

    return [
        SavedSearchResponse(
            id=search.id,
            project_id=search.project_id,
            created_by=search.created_by,
            name=search.name,
            description=search.description,
            filter_config=search.filter_config,
            is_shared=search.is_shared,
            created_at=search.created_at.isoformat(),
            updated_at=search.updated_at.isoformat(),
        )
        for search in searches
    ]


@router.get("/{search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a saved search by ID."""
    service = SavedSearchService(db)
    try:
        search = await service.get_saved_search(search_id, current_user.id)
        return SavedSearchResponse(
            id=search.id,
            project_id=search.project_id,
            created_by=search.created_by,
            name=search.name,
            description=search.description,
            filter_config=search.filter_config,
            is_shared=search.is_shared,
            created_at=search.created_at.isoformat(),
            updated_at=search.updated_at.isoformat(),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: str,
    search_data: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a saved search."""
    service = SavedSearchService(db)
    try:
        search = await service.update_saved_search(
            search_id=search_id,
            user_id=current_user.id,
            name=search_data.name,
            description=search_data.description,
            filter_config=search_data.filter_config,
            is_shared=search_data.is_shared,
        )
        return SavedSearchResponse(
            id=search.id,
            project_id=search.project_id,
            created_by=search.created_by,
            name=search.name,
            description=search.description,
            filter_config=search.filter_config,
            is_shared=search.is_shared,
            created_at=search.created_at.isoformat(),
            updated_at=search.updated_at.isoformat(),
        )
    except (NotFoundError, ValidationError) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved search."""
    service = SavedSearchService(db)
    try:
        await service.delete_saved_search(search_id, current_user.id)
    except (NotFoundError, ValidationError) as e:
        status_code = status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundError) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
