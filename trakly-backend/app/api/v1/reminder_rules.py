"""Reminder rule management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.reminder_rule import (
    ReminderRuleCreate,
    ReminderRuleUpdate,
    ReminderRuleResponse
)
from app.services.reminder_service import ReminderService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reminder-rules", tags=["Reminder Rules"])


@router.post("", response_model=ReminderRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder_rule(
    rule_data: ReminderRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new reminder rule.

    Requires project manager or admin role.
    """
    reminder_service = ReminderService(db)
    try:
        rule = await reminder_service.create_rule(
            rule_data.model_dump(),
            created_by=current_user.id,
        )
        return rule
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/project/{project_id}", response_model=List[ReminderRuleResponse])
async def list_reminder_rules(
    project_id: str,
    include_disabled: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reminder rules for a project.

    Args:
        project_id: The project ID to list rules for
        include_disabled: Whether to include disabled rules (default: False)
    """
    reminder_service = ReminderService(db)
    rules = await reminder_service.list_rules(
        project_id,
        include_disabled=include_disabled,
    )
    return rules


@router.get("/{rule_id}", response_model=ReminderRuleResponse)
async def get_reminder_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific reminder rule by ID."""
    reminder_service = ReminderService(db)
    rule = await reminder_service.get_rule(rule_id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder rule not found"
        )

    return rule


@router.patch("/{rule_id}", response_model=ReminderRuleResponse)
async def update_reminder_rule(
    rule_id: str,
    rule_data: ReminderRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a reminder rule.

    Requires project manager or admin role.
    """
    reminder_service = ReminderService(db)
    try:
        rule = await reminder_service.update_rule(
            rule_id,
            rule_data.model_dump(exclude_unset=True),
        )
        return rule
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a reminder rule.

    Requires project manager or admin role.
    """
    reminder_service = ReminderService(db)
    try:
        await reminder_service.delete_rule(rule_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
