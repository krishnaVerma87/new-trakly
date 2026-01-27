"""Advanced search and saved search API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.user import User
from app.schemas.search import (
    AdvancedSearchRequest,
    SaveSearchRequest,
    SavedSearchUpdate,
    SavedSearchResponse,
)
from app.schemas.issue import IssueResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post(
    "/advanced",
    response_model=List[IssueResponse],
    summary="Advanced issue search",
)
async def advanced_search(
    search_request: AdvancedSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute advanced search with complex filter criteria.

    Supports filtering by:
    - **status**: List of issue statuses (e.g., ["new", "in_progress"])
    - **priority**: List of priorities (e.g., ["high", "critical"])
    - **severity**: List of severities (e.g., ["blocker", "critical"])
    - **issue_type**: List of issue types (e.g., ["bug", "task"])
    - **assignee_id**: List of assignee user IDs
    - **reporter_id**: List of reporter user IDs
    - **component_id**: List of component IDs
    - **sprint_id**: Sprint ID or "current" for active sprint
    - **labels**: List of label IDs (issues must have ALL labels)
    - **is_regression**: Boolean for regression bugs
    - **is_duplicate**: Boolean for duplicate issues
    - **created_after**: ISO datetime string
    - **created_before**: ISO datetime string
    - **updated_after**: ISO datetime string
    - **updated_before**: ISO datetime string
    - **story_points_min**: Minimum story points
    - **story_points_max**: Maximum story points
    - **text_search**: Full-text search on title, description, issue_key

    Returns paginated list of issues matching the criteria.
    """
    service = SearchService(db)
    issues = await service.advanced_search(
        project_id=search_request.project_id,
        filter_config=search_request.filter_config,
        skip=search_request.skip,
        limit=search_request.limit,
    )
    return issues


@router.post(
    "/save",
    response_model=SavedSearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a search",
)
async def save_search(
    search_request: SaveSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Save search criteria for quick reuse.

    Saved searches can be:
    - **Personal**: Only visible to the creator (is_shared=false)
    - **Shared**: Visible to all project members (is_shared=true)

    Search names must be unique per user within a project.
    """
    service = SearchService(db)
    saved_search = await service.save_search(
        project_id=search_request.project_id,
        name=search_request.name,
        filter_config=search_request.filter_config,
        created_by=current_user.id,
        description=search_request.description,
        is_shared=search_request.is_shared,
    )
    return saved_search


@router.get(
    "/saved",
    response_model=List[SavedSearchResponse],
    summary="List saved searches",
)
async def list_saved_searches(
    project_id: str = Query(..., description="Project ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all saved searches for a project.

    Returns both:
    - Personal searches created by the current user
    - Shared searches created by any team member
    """
    service = SearchService(db)
    searches = await service.get_saved_searches(
        project_id=project_id,
        user_id=current_user.id,
    )
    return searches


@router.get(
    "/saved/{search_id}",
    response_model=SavedSearchResponse,
    summary="Get saved search",
)
async def get_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific saved search."""
    service = SearchService(db)
    saved_search = await service.get_saved_search(search_id)
    return saved_search


@router.get(
    "/saved/{search_id}/execute",
    response_model=List[IssueResponse],
    summary="Execute saved search",
)
async def execute_saved_search(
    search_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a saved search and return matching issues.

    Applies the saved filter configuration and returns paginated results.
    """
    service = SearchService(db)
    issues = await service.execute_saved_search(
        search_id=search_id,
        skip=skip,
        limit=limit,
    )
    return issues


@router.patch(
    "/saved/{search_id}",
    response_model=SavedSearchResponse,
    summary="Update saved search",
)
async def update_saved_search(
    search_id: str,
    update_data: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a saved search.

    Only the creator can update their own saved searches.
    """
    service = SearchService(db)
    saved_search = await service.update_saved_search(
        search_id=search_id,
        user_id=current_user.id,
        name=update_data.name,
        description=update_data.description,
        filter_config=update_data.filter_config,
        is_shared=update_data.is_shared,
    )
    return saved_search


@router.delete(
    "/saved/{search_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved search",
)
async def delete_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a saved search.

    Only the creator can delete their own saved searches.
    """
    service = SearchService(db)
    await service.delete_saved_search(
        search_id=search_id,
        user_id=current_user.id,
    )
