"""User management service."""
from typing import Dict, Any, List, Optional
import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user import UserRepository, RoleRepository
from app.repositories.organization import OrganizationRepository
from app.services.email_service import EmailService


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

    def _generate_temp_password(self, length: int = 12) -> str:
        """
        Generate a secure temporary password.

        Args:
            length: Password length (default 12)

        Returns:
            Random password string
        """
        # Include uppercase, lowercase, digits, and special characters
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Ensure at least one of each type
        if not any(c.isupper() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_uppercase)
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice(string.digits)

        return password

    async def bulk_invite_users(
        self,
        users_data: List[Dict[str, Any]],
        organization_id: str,
        send_emails: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk invite users to the organization.

        Args:
            users_data: List of user data dictionaries with email, full_name, role_id
            organization_id: Organization ID
            send_emails: Whether to send welcome emails (default True)

        Returns:
            Dictionary with total, successful, failed counts and detailed results
        """
        # Verify organization exists
        organization = await self.org_repo.get(organization_id)
        if not organization:
            raise NotFoundError("Organization not found")

        results = []
        successful = 0
        failed = 0

        email_service = EmailService() if send_emails else None

        for user_data in users_data:
            email = user_data.get("email")
            full_name = user_data.get("full_name")
            role_id = user_data.get("role_id")

            result = {
                "email": email,
                "full_name": full_name,
                "success": False,
                "user_id": None,
                "error": None,
                "temp_password": None,
            }

            try:
                # Check if email already exists
                if await self.user_repo.email_exists(email):
                    result["error"] = f"Email {email} is already in use"
                    failed += 1
                    results.append(result)
                    continue

                # Verify role exists and belongs to this organization
                role = await self.role_repo.get(role_id)
                if not role:
                    result["error"] = "Role not found"
                    failed += 1
                    results.append(result)
                    continue

                if role.organization_id != organization_id:
                    result["error"] = "Role does not belong to this organization"
                    failed += 1
                    results.append(result)
                    continue

                # Generate temporary password
                temp_password = self._generate_temp_password()

                # Create user
                create_data = {
                    "email": email,
                    "full_name": full_name,
                    "password_hash": get_password_hash(temp_password),
                    "organization_id": organization_id,
                    "is_active": True,
                }

                user = await self.user_repo.create(create_data)

                # Assign role
                await self.user_repo.assign_role(user.id, role_id)

                # Send welcome email if enabled
                if email_service:
                    try:
                        await email_service.send_welcome_email(
                            to_email=email,
                            user_name=full_name,
                            temp_password=temp_password,
                            organization_name=organization.name,
                        )
                    except Exception as email_error:
                        # Log email error but don't fail the user creation
                        result["error"] = f"User created but email failed: {str(email_error)}"

                result["success"] = True
                result["user_id"] = user.id
                result["temp_password"] = temp_password
                successful += 1

            except Exception as e:
                result["error"] = str(e)
                failed += 1

            results.append(result)

        return {
            "total": len(users_data),
            "successful": successful,
            "failed": failed,
            "results": results,
        }
