"""User repository with role and permission handling."""
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Role, user_roles
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with roles and permissions loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.organization),
            )
        )
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: str) -> Optional[User]:
        """Get user with roles and permissions eagerly loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.organization),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> List[User]:
        """Get all users in an organization."""
        query = (
            select(User)
            .where(User.organization_id == organization_id)
            .options(selectinload(User.roles))
        )

        if active_only:
            query = query.where(User.is_active == True)

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def email_exists(
        self,
        email: str,
        exclude_id: Optional[str] = None,
    ) -> bool:
        """Check if email already exists."""
        query = select(User).where(User.email == email)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
    ) -> None:
        """Assign a role to a user."""
        stmt = insert(user_roles).values(
            user_id=user_id,
            role_id=role_id,
            assigned_at=datetime.utcnow(),
            assigned_by=assigned_by,
        )
        await self.db.execute(stmt)
        await self.db.commit()


class RoleRepository(BaseRepository[Role]):
    """Repository for Role operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_organization(
        self,
        organization_id: str,
    ) -> List[Role]:
        """Get all roles in an organization."""
        result = await self.db.execute(
            select(Role)
            .where(Role.organization_id == organization_id)
            .options(selectinload(Role.permissions))
            .order_by(Role.name)
        )
        return list(result.scalars().all())

    async def get_by_name(
        self,
        organization_id: str,
        name: str,
    ) -> Optional[Role]:
        """Get role by name within an organization."""
        result = await self.db.execute(
            select(Role)
            .where(Role.organization_id == organization_id)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        return result.scalar_one_or_none()
