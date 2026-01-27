"""Comment schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    """Schema for creating a comment."""
    content: str = Field(..., min_length=1)
    issue_id: Optional[str] = None
    feature_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    is_internal: bool = False


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: Optional[str] = Field(None, min_length=1)


class CommentResponse(BaseModel):
    """Comment response schema."""
    id: str
    issue_id: Optional[str] = None
    feature_id: Optional[str] = None
    author_id: str
    author: Optional[UserResponse] = None
    content: str
    is_internal: bool
    parent_comment_id: Optional[str] = None
    replies: List["CommentResponse"] = []
    mentions: List[UserResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Enable forward reference for nested replies
CommentResponse.model_rebuild()
