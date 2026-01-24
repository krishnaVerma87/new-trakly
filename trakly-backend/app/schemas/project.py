"""Project, ProjectMember, and Component schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class ComponentResponse(BaseModel):
    """Component response schema."""
    id: str
    name: str
    description: Optional[str] = None
    lead_user_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComponentCreate(BaseModel):
    """Schema for creating a component."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    lead_user_id: Optional[str] = None


class ProjectMemberResponse(BaseModel):
    """Project member response schema."""
    id: str
    user_id: str
    role: str
    user: Optional[UserResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberCreate(BaseModel):
    """Schema for adding a project member."""
    user_id: str
    role: str = "member"  # admin, member, viewer


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    key: str = Field(..., min_length=2, max_length=10, pattern=r"^[A-Z0-9]+$")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    organization_id: str
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=2000)
    lead_user_id: Optional[str] = None
    default_assignee_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    lead_user_id: Optional[str] = None
    default_assignee_id: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: str
    organization_id: str
    slug: str
    description: Optional[str] = None
    lead_user_id: Optional[str] = None
    default_assignee_id: Optional[str] = None
    is_active: bool
    members: List[ProjectMemberResponse] = []
    components: List[ComponentResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
