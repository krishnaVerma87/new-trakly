"""Attachment schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class AttachmentResponse(BaseModel):
    """Response schema for file attachment."""

    id: str
    issue_id: Optional[str] = None
    feature_id: Optional[str] = None
    uploaded_by: str
    filename: str
    original_filename: str
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
    download_url: str = Field(..., description="URL to download the file")
    created_at: datetime

    # Optional relationships
    uploader: Optional[UserResponse] = None

    class Config:
        from_attributes = True
