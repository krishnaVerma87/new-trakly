"""Authentication service."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.models.user import User
from app.repositories.user import UserRepository, RoleRepository
from app.repositories.organization import OrganizationRepository
from app.services.role_service import RoleService
from app.services.workflow_service import WorkflowService


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.role_repo = RoleRepository(db)

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

    async def signup(
        self,
        organization_name: str,
        organization_slug: str,
        organization_description: Optional[str],
        user_email: str,
        user_password: str,
        user_full_name: str,
        user_timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Complete signup flow: create organization and first admin user.

        Args:
            organization_name: Name of the organization
            organization_slug: URL-friendly slug
            organization_description: Optional description
            user_email: Admin user's email
            user_password: Plain text password
            user_full_name: Admin user's full name
            user_timezone: User's timezone (default: UTC)

        Returns:
            Token response with access_token and user info

        Raises:
            ValidationError: If organization slug or user email already exists
        """
        # Check if organization slug already exists
        existing_org = await self.org_repo.get_by_slug(organization_slug)
        if existing_org:
            raise ValidationError(f"Organization slug '{organization_slug}' is already taken")

        # Check if user email already exists
        existing_user = await self.user_repo.get_by_email(user_email)
        if existing_user:
            raise ValidationError(f"Email '{user_email}' is already registered")

        # Create organization
        org_data = {
            "name": organization_name,
            "slug": organization_slug,
            "description": organization_description,
            "is_active": True,
        }
        organization = await self.org_repo.create(org_data)

        # Create system roles with proper permissions using RoleService
        role_service = RoleService(self.db)
        system_roles = await role_service.create_system_roles(organization.id)

        # Get the org_admin role for the first user
        admin_role = system_roles.get("org_admin")
        if not admin_role:
            raise ValidationError("Failed to create org_admin role")

        # Create admin user first (needed for workflow template creation)
        user_data = {
            "organization_id": organization.id,
            "email": user_email,
            "password_hash": get_password_hash(user_password),
            "full_name": user_full_name,
            "timezone": user_timezone,
            "is_active": True,
        }
        user = await self.user_repo.create(user_data)

        # Assign Admin role to user
        await self.user_repo.assign_role(user.id, admin_role.id)

        # Create default workflow templates
        workflow_service = WorkflowService(self.db)
        await workflow_service.create_default_templates(
            organization_id=organization.id,
            user_id=user.id,
        )

        # Reload user with roles
        user = await self.user_repo.get_with_roles(user.id)

        # Generate and return token
        return await self.create_user_token(user)
