"""WikiPage schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WikiPageBase(BaseModel):
    """Base wiki page schema."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")
    slug: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[str] = None


class WikiPageCreate(WikiPageBase):
    """Schema for creating a wiki page."""

    pass


class WikiPageUpdate(BaseModel):
    """Schema for updating a wiki page."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    slug: Optional[str] = Field(None, max_length=255)


class WikiPageMove(BaseModel):
    """Schema for moving a wiki page."""

    parent_id: Optional[str] = None
    position: int = Field(..., ge=0)


class UserBrief(BaseModel):
    """Brief user info for wiki page responses."""

    id: str
    email: str
    full_name: str

    class Config:
        from_attributes = True


class WikiPageResponse(BaseModel):
    """Wiki page response schema."""

    id: str
    project_id: str
    parent_id: Optional[str] = None
    title: str
    slug: str
    content: str
    position: int
    created_by: str
    updated_by: Optional[str] = None
    creator: Optional[UserBrief] = None
    updater: Optional[UserBrief] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WikiPageTreeNode(BaseModel):
    """Wiki page tree node for navigation."""

    id: str
    title: str
    slug: str
    parent_id: Optional[str] = None
    position: int
    created_at: datetime
    updated_at: datetime
    children: List['WikiPageTreeNode'] = []

    class Config:
        from_attributes = True


# Enable forward references for recursive model
WikiPageTreeNode.model_rebuild()
