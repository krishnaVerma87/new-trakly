"""User management service."""
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user import UserRepository, RoleRepository
from app.repositories.organization import OrganizationRepository


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            ValidationError: If email exists or organization not found
        """
        # Check email uniqueness
        if await self.user_repo.email_exists(user_data["email"]):
            raise ValidationError(f"Email {user_data['email']} is already in use")

        # Verify organization exists
        organization = await self.org_repo.get(user_data["organization_id"])
        if not organization:
            raise NotFoundError("Organization not found")

        # Hash password
        password = user_data.pop("password")
        user_data["password_hash"] = get_password_hash(password)

        # Extract role_ids for later assignment
        role_ids = user_data.pop("role_ids", [])

        # Create user
        user = await self.user_repo.create(user_data)

        # Assign roles
        if role_ids:
            await self._assign_roles_to_user(user, role_ids)
            # Refresh to get roles
            user = await self.user_repo.get_with_roles(user.id)

        return user

    async def _assign_roles_to_user(
        self,
        user: User,
        role_ids: List[str],
    ) -> None:
        """Assign roles to a user."""
        for role_id in role_ids:
            role = await self.role_repo.get(role_id)
            if role and role.organization_id == user.organization_id:
                user.roles.append(role)
        await self.db.commit()

    async def get_user(self, user_id: str) -> User:
        """Get user by ID."""
        user = await self.user_repo.get_with_roles(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_users(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> List[User]:
        """List users in an organization."""
        return await self.user_repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )

    async def update_user(
        self,
        user_id: str,
        user_data: Dict[str, Any],
    ) -> User:
        """Update an existing user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check email uniqueness if changing
        if "email" in user_data and user_data["email"] != user.email:
            if await self.user_repo.email_exists(user_data["email"], exclude_id=user_id):
                raise ValidationError(f"Email {user_data['email']} is already in use")

        # Hash password if provided
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))

        # Handle role updates
        role_ids = user_data.pop("role_ids", None)

        # Update user
        updated_user = await self.user_repo.update(user_id, user_data)

        # Update roles if provided
        if role_ids is not None:
            updated_user.roles.clear()
            await self._assign_roles_to_user(updated_user, role_ids)
            updated_user = await self.user_repo.get_with_roles(user_id)

        return updated_user

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete a user (set is_active=False)."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.user_repo.update(user_id, {"is_active": False})
        return True
