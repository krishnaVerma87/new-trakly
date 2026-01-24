"""Authentication service."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate user by email and password.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            Authenticated user

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        # Update last login time
        await self.user_repo.update(user.id, {"last_login_at": datetime.utcnow()})

        return user

    async def create_user_token(self, user: User) -> Dict[str, Any]:
        """
        Create JWT token for authenticated user.

        Args:
            user: Authenticated user

        Returns:
            Token response with access_token and user info
        """
        token_data = {
            "sub": user.id,
            "email": user.email,
            "organization_id": user.organization_id,
        }

        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "organization_id": user.organization_id,
                "roles": [role.name for role in user.roles],
            },
        }

    async def login(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Full login flow: authenticate and return token.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            Token response
        """
        user = await self.authenticate_user(email, password)
        return await self.create_user_token(user)

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token.

        Args:
            token: JWT token string

        Returns:
            Current user

        Raises:
            AuthenticationError: If token is invalid
        """
        payload = decode_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")

        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user
