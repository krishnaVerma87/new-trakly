"""Time logging endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.time_log import (
    TimeLogCreate,
    TimeLogUpdate,
    TimeLogResponse,
    TimeLogSummary,
)
from app.services.time_log_service import TimeLogService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/time-logs", tags=["Time Logs"])


@router.post("/start", response_model=TimeLogResponse, status_code=status.HTTP_201_CREATED)
async def start_timer(
    issue_id: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a timer for an issue."""
    service = TimeLogService(db)
    try:
        time_log = await service.start_timer(issue_id, current_user.id, description)
        return time_log
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{time_log_id}/stop", response_model=TimeLogResponse)
async def stop_timer(
    time_log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop a running timer."""
    service = TimeLogService(db)
    try:
        time_log = await service.stop_timer(time_log_id, current_user.id)
        return time_log
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/log", response_model=TimeLogResponse, status_code=status.HTTP_201_CREATED)
async def log_time_manually(
    issue_id: str,
    duration_minutes: int,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log time manually without using a timer."""
    service = TimeLogService(db)
    try:
        time_log = await service.log_time(
            issue_id,
            current_user.id,
            duration_minutes,
            description
        )
        return time_log
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/issue/{issue_id}", response_model=List[TimeLogResponse])
async def get_issue_time_logs(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all time logs for an issue."""
    service = TimeLogService(db)
    time_logs = await service.get_time_logs(issue_id=issue_id)

    # Add user names
    from sqlalchemy.orm import selectinload
    for log in time_logs:
        if log.user:
            log.user_name = log.user.full_name

    return time_logs


@router.get("/my-logs", response_model=List[TimeLogResponse])
async def get_my_time_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all time logs for the current user."""
    service = TimeLogService(db)
    time_logs = await service.get_time_logs(user_id=current_user.id)

    # Add user names
    for log in time_logs:
        log.user_name = current_user.full_name

    return time_logs


@router.get("/issue/{issue_id}/summary", response_model=TimeLogSummary)
async def get_time_summary(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get time tracking summary for an issue."""
    service = TimeLogService(db)
    summary = await service.get_time_summary(issue_id)
    return summary


@router.patch("/{time_log_id}", response_model=TimeLogResponse)
async def update_time_log(
    time_log_id: str,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a time log."""
    service = TimeLogService(db)
    try:
        time_log = await service.update_time_log(time_log_id, current_user.id, description)
        if time_log.user:
            time_log.user_name = time_log.user.full_name
        return time_log
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{time_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_log(
    time_log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a time log."""
    service = TimeLogService(db)
    try:
        await service.delete_time_log(time_log_id, current_user.id)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
