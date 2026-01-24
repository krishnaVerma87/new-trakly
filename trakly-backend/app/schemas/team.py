"""Team schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class TeamMemberResponse(BaseModel):
    """Team member response schema."""
    id: str
    user_id: str
    role: str
    user: Optional[UserResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    """Schema for adding a team member."""
    user_id: str
    role: str = "member"  # lead, member


class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., min_length=1, max_length=255)


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    organization_id: str
    description: Optional[str] = None
    team_type: Optional[str] = None  # engineering, qa, product
    parent_team_id: Optional[str] = None


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    team_type: Optional[str] = None
    parent_team_id: Optional[str] = None


class TeamResponse(TeamBase):
    """Team response schema."""
    id: str
    organization_id: str
    description: Optional[str] = None
    team_type: Optional[str] = None
    parent_team_id: Optional[str] = None
    members: List[TeamMemberResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
