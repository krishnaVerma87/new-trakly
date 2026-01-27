"""Organization schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[str] = None  # JSON string for integration settings
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema."""
    id: str
    description: Optional[str] = None
    settings: Optional[str] = None  # JSON string for integration settings
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
