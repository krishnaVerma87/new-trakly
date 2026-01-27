"""Service for managing roles and permissions."""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import Role, Permission
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError


class RoleService:
    """Service for role operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_system_permissions(self) -> List[Permission]:
        """
        Ensure all system permissions exist in the database.
        Returns list of all permissions.
        """
        permissions_data = [
            # Issue permissions
            {"name": "issue.create", "resource": "issue", "action": "create", "description": "Create new issues"},
            {"name": "issue.read", "resource": "issue", "action": "read", "description": "View issues"},
            {"name": "issue.update", "resource": "issue", "action": "update", "description": "Update issues"},
            {"name": "issue.delete", "resource": "issue", "action": "delete", "description": "Delete issues"},
            {"name": "issue.assign", "resource": "issue", "action": "assign", "description": "Assign issues to users"},

            # Feature permissions
            {"name": "feature.create", "resource": "feature", "action": "create", "description": "Create features"},
            {"name": "feature.read", "resource": "feature", "action": "read", "description": "View features"},
            {"name": "feature.update", "resource": "feature", "action": "update", "description": "Update features"},
            {"name": "feature.delete", "resource": "feature", "action": "delete", "description": "Delete features"},

            # Project permissions
            {"name": "project.create", "resource": "project", "action": "create", "description": "Create projects"},
            {"name": "project.read", "resource": "project", "action": "read", "description": "View projects"},
            {"name": "project.update", "resource": "project", "action": "update", "description": "Update projects"},
            {"name": "project.delete", "resource": "project", "action": "delete", "description": "Delete projects"},
            {"name": "project.manage_members", "resource": "project", "action": "manage_members", "description": "Manage project members"},

            # User permissions
            {"name": "user.create", "resource": "user", "action": "create", "description": "Create users"},
            {"name": "user.read", "resource": "user", "action": "read", "description": "View users"},
            {"name": "user.update", "resource": "user", "action": "update", "description": "Update users"},
            {"name": "user.delete", "resource": "user", "action": "delete", "description": "Delete users"},
            {"name": "user.manage_roles", "resource": "user", "action": "manage_roles", "description": "Assign roles to users"},

            # Organization permissions
            {"name": "organization.update", "resource": "organization", "action": "update", "description": "Update organization settings"},
            {"name": "organization.manage", "resource": "organization", "action": "manage", "description": "Full organization management"},

            # Sprint permissions
            {"name": "sprint.create", "resource": "sprint", "action": "create", "description": "Create sprints"},
            {"name": "sprint.read", "resource": "sprint", "action": "read", "description": "View sprints"},
            {"name": "sprint.update", "resource": "sprint", "action": "update", "description": "Update sprints"},
            {"name": "sprint.delete", "resource": "sprint", "action": "delete", "description": "Delete sprints"},
        ]

        permissions = []
        for perm_data in permissions_data:
            # Check if permission exists
            result = await self.db.execute(
                select(Permission).where(Permission.name == perm_data["name"])
            )
            permission = result.scalar_one_or_none()

            if not permission:
                permission = Permission(**perm_data)
                self.db.add(permission)
                permissions.append(permission)
            else:
                permissions.append(permission)

        await self.db.commit()
        return permissions

    async def create_system_roles(self, organization_id: str) -> Dict[str, Role]:
        """
        Create all system roles for an organization with predefined permissions.

        Returns dict mapping role names to Role objects.
        """
        # First ensure all permissions exist
        all_permissions = await self.ensure_system_permissions()

        # Create permission lookup
        perm_lookup = {p.name: p for p in all_permissions}

        # Define system roles with their permissions
        system_roles_config = {
            "org_admin": {
                "description": "Organization administrator with full access",
                "permissions": [p.name for p in all_permissions],  # All permissions
            },
            "project_manager": {
                "description": "Can manage projects, sprints, and issues",
                "permissions": [
                    "issue.create", "issue.read", "issue.update", "issue.delete", "issue.assign",
                    "feature.create", "feature.read", "feature.update", "feature.delete",
                    "project.read", "project.update", "project.manage_members",
                    "user.read",
                    "sprint.create", "sprint.read", "sprint.update", "sprint.delete",
                ],
            },
            "developer": {
                "description": "Can create and update issues and features",
                "permissions": [
                    "issue.create", "issue.read", "issue.update",
                    "feature.read", "feature.update",
                    "project.read",
                    "user.read",
                    "sprint.read",
                ],
            },
            "reporter": {
                "description": "Can report and view issues",
                "permissions": [
                    "issue.create", "issue.read",
                    "feature.read",
                    "project.read",
                    "user.read",
                    "sprint.read",
                ],
            },
            "viewer": {
                "description": "Read-only access to projects and issues",
                "permissions": [
                    "issue.read",
                    "feature.read",
                    "project.read",
                    "user.read",
                    "sprint.read",
                ],
            },
        }

        created_roles = {}

        for role_name, config in system_roles_config.items():
            # Check if role already exists
            result = await self.db.execute(
                select(Role).where(
                    Role.name == role_name,
                    Role.organization_id == organization_id
                )
            )
            role = result.scalar_one_or_none()

            if not role:
                # Create role
                role = Role(
                    organization_id=organization_id,
                    name=role_name,
                    description=config["description"],
                    is_system_role=True,
                )
                self.db.add(role)
                await self.db.commit()
                await self.db.refresh(role)

                # Assign permissions using raw SQL to avoid lazy loading issues
                from sqlalchemy import insert
                from app.models.user import role_permissions

                for perm_name in config["permissions"]:
                    if perm_name in perm_lookup:
                        permission = perm_lookup[perm_name]
                        # Insert into role_permissions junction table
                        stmt = insert(role_permissions).values(
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        await self.db.execute(stmt)

                await self.db.commit()

            created_roles[role_name] = role

        return created_roles

    async def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get all permissions for a role."""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError("Role not found")

        return role.permissions

    async def has_permission(
        self,
        user_roles: List[Role],
        required_permission: str
    ) -> bool:
        """
        Check if user has a specific permission through any of their roles.

        Args:
            user_roles: List of user's roles
            required_permission: Permission name to check (e.g., "issue.create")

        Returns:
            True if user has permission, False otherwise
        """
        for role in user_roles:
            for permission in role.permissions:
                if permission.name == required_permission:
                    return True
        return False

    async def check_permission(
        self,
        user_roles: List[Role],
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user can perform an action on a resource.

        Args:
            user_roles: List of user's roles
            resource: Resource name (e.g., "issue", "project")
            action: Action name (e.g., "create", "update")

        Returns:
            True if user has permission, False otherwise
        """
        required_permission = f"{resource}.{action}"
        return await self.has_permission(user_roles, required_permission)
