"""Notification schemas for request/response validation."""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: str
    user_id: str
    organization_id: str
    notification_type: str
    title: str
    message: str
    issue_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_read: bool
    read_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    slack_enabled: Optional[bool] = None
    email_digest: Optional[bool] = None
    digest_frequency: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""
    id: str
    user_id: str
    notification_type: str
    in_app_enabled: bool
    email_enabled: bool
    slack_enabled: bool
    email_digest: bool
    digest_frequency: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
