"""Time log schemas for time tracking."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TimeLogCreate(BaseModel):
    """Schema for creating a time log."""
    issue_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class TimeLogUpdate(BaseModel):
    """Schema for updating a time log."""
    ended_at: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class TimeLogResponse(BaseModel):
    """Schema for time log response."""
    id: str
    issue_id: str
    user_id: str
    user_name: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeLogSummary(BaseModel):
    """Summary of time logs for an issue or user."""
    total_time_minutes: int
    total_time_hours: float
    log_count: int
    by_user: dict[str, int] = {}  # user_name -> minutes
