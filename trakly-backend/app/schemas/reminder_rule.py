"""Reminder rule schemas for request/response validation."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class ReminderRuleConditions(BaseModel):
    """Schema for reminder rule conditions."""
    sprint: str = Field(
        default="current",
        description="Sprint filter: 'current', 'next', '<sprint_id>', or 'any'"
    )
    status: Optional[list[str]] = Field(
        default=None,
        description="List of issue statuses to match"
    )
    priority: Optional[list[str]] = Field(
        default=None,
        description="List of priorities to match"
    )
    assignee_exists: Optional[bool] = Field(
        default=None,
        description="Filter by assignee existence"
    )
    days_without_update: int = Field(
        ...,
        ge=1,
        description="Number of days without update required to trigger reminder"
    )
    issue_type: Optional[list[str]] = Field(
        default=None,
        description="List of issue types to match"
    )

    @field_validator('sprint')
    @classmethod
    def validate_sprint(cls, v: str) -> str:
        """Validate sprint value."""
        allowed = ['current', 'next', 'any']
        if v not in allowed and not v.startswith('sprint-'):
            raise ValueError(
                f"Sprint must be one of {allowed} or a sprint ID"
            )
        return v


class ReminderRuleBase(BaseModel):
    """Base schema for reminder rules."""
    project_id: str = Field(..., min_length=1, max_length=36)
    name: str = Field(..., min_length=1, max_length=255)
    conditions: Dict[str, Any] = Field(
        ...,
        description="JSON conditions for matching issues"
    )
    notification_title: str = Field(..., min_length=1, max_length=500)
    notification_message: str = Field(..., min_length=1, max_length=2000)
    notify_assignee: bool = Field(default=True)
    notify_watchers: bool = Field(default=True)
    check_frequency_minutes: int = Field(default=60, ge=15, le=1440)
    is_enabled: bool = Field(default=True)


class ReminderRuleCreate(ReminderRuleBase):
    """Schema for creating a reminder rule."""
    pass


class ReminderRuleUpdate(BaseModel):
    """Schema for updating a reminder rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    conditions: Optional[Dict[str, Any]] = None
    notification_title: Optional[str] = Field(None, min_length=1, max_length=500)
    notification_message: Optional[str] = Field(None, min_length=1, max_length=2000)
    notify_assignee: Optional[bool] = None
    notify_watchers: Optional[bool] = None
    check_frequency_minutes: Optional[int] = Field(None, ge=15, le=1440)
    is_enabled: Optional[bool] = None


class ReminderRuleResponse(ReminderRuleBase):
    """Schema for reminder rule response."""
    id: str
    last_executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
