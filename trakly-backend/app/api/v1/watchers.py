"""Watcher subscription endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.watcher import WatcherResponse
from app.schemas.user import UserResponse
from app.services.watcher_service import WatcherService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/watchers", tags=["Watchers"])


@router.post("/issues/{issue_id}/subscribe", response_model=WatcherResponse)
async def subscribe_to_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to issue notifications."""
    watcher_service = WatcherService(db)
    try:
        watcher = await watcher_service.subscribe(
            issue_id=issue_id,
            user_id=current_user.id,
        )
        return watcher
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/issues/{issue_id}/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsubscribe from issue notifications."""
    watcher_service = WatcherService(db)
    await watcher_service.unsubscribe(issue_id, current_user.id)
    return None


@router.get("/issues/{issue_id}", response_model=List[UserResponse])
async def get_issue_watchers(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all watchers for an issue."""
    watcher_service = WatcherService(db)
    watchers = await watcher_service.get_watchers(issue_id)
    return watchers


# Feature watcher endpoints
@router.post("/features/{feature_id}/subscribe", response_model=WatcherResponse)
async def subscribe_to_feature(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Subscribe to feature notifications."""
    watcher_service = WatcherService(db)
    try:
        watcher = await watcher_service.subscribe_to_feature(
            feature_id=feature_id,
            user_id=current_user.id,
        )
        return watcher
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/features/{feature_id}/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_feature(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unsubscribe from feature notifications."""
    watcher_service = WatcherService(db)
    await watcher_service.unsubscribe_from_feature(feature_id, current_user.id)
    return None


@router.get("/features/{feature_id}", response_model=List[UserResponse])
async def get_feature_watchers(
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all watchers for a feature."""
    watcher_service = WatcherService(db)
    watchers = await watcher_service.get_feature_watchers(feature_id)
    return watchers
