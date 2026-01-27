"""Watcher schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel


class WatcherCreate(BaseModel):
    """Schema for creating a watcher."""
    issue_id: str
    subscription_type: str = "manual"


class WatcherResponse(BaseModel):
    """Schema for watcher response."""
    id: str
    issue_id: str
    user_id: str
    subscription_type: str
    created_at: str

    class Config:
        from_attributes = True
