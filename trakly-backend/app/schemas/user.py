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

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Schema for creating a role."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


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


class BulkUserInvite(BaseModel):
    """Schema for inviting a single user in bulk operation."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    role_id: str = Field(..., description="Role to assign to the user")


class BulkUserInviteRequest(BaseModel):
    """Schema for bulk user invitation request."""
    users: List[BulkUserInvite] = Field(..., min_items=1, max_items=50, description="List of users to invite (max 50)")

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "role_id": "role-uuid-developer"
                    },
                    {
                        "email": "jane@example.com",
                        "full_name": "Jane Smith",
                        "role_id": "role-uuid-developer"
                    }
                ]
            }
        }


class BulkUserInviteResult(BaseModel):
    """Result of bulk user invitation."""
    email: EmailStr
    full_name: str
    success: bool
    user_id: Optional[str] = None
    error: Optional[str] = None
    temp_password: Optional[str] = None


class BulkUserInviteResponse(BaseModel):
    """Response for bulk user invitation."""
    total: int
    successful: int
    failed: int
    results: List[BulkUserInviteResult]
