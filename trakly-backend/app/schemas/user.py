"""User and Role schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RoleResponse(BaseModel):
    """Role response schema."""
    id: str
    name: str
    description: Optional[str] = None
    is_system_role: bool

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=100)
    organization_id: str
    role_ids: List[str] = []


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    role_ids: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    id: str
    organization_id: str
    is_active: bool
    avatar_url: Optional[str] = None
    timezone: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithRolesResponse(UserResponse):
    """User response with roles included."""
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True
