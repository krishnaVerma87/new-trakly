"""Label schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LabelBase(BaseModel):
    """Base label schema."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#6B7280", pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(None, max_length=255)


class LabelCreate(LabelBase):
    """Schema for creating a label."""
    pass


class LabelUpdate(BaseModel):
    """Schema for updating a label."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(None, max_length=255)


class LabelResponse(LabelBase):
    """Label response schema."""
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
