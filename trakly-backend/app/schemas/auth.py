"""Authentication schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Signup request payload for creating organization and first admin user."""
    # Organization fields
    organization_name: str = Field(..., min_length=1, max_length=255)
    organization_slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    organization_description: Optional[str] = None

    # User fields
    user_email: EmailStr
    user_password: str = Field(..., min_length=8)
    user_full_name: str = Field(..., min_length=1, max_length=255)
    user_timezone: str = "UTC"


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: dict  # Basic user info
