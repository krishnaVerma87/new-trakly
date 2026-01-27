"""Project, ProjectMember, and Component repositories."""
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectMember, Component, ProjectPin
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)

    async def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Project]:
        """Get all projects in an organization."""
        query = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .options(
                selectinload(Project.members),
                selectinload(Project.components),
            )
        )

        if active_only:
            query = query.where(Project.is_active == True)

        query = query.order_by(Project.name).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_slug(
        self,
        organization_id: str,
        slug: str,
    ) -> Optional[Project]:
        """Get project by slug within an organization."""
        result = await self.db.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .where(Project.slug == slug)
            .options(
                selectinload(Project.members),
                selectinload(Project.components),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_key(
        self,
        organization_id: str,
        key: str,
    ) -> Optional[Project]:
        """Get project by key within an organization."""
        result = await self.db.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .where(Project.key == key)
        )
        return result.scalar_one_or_none()

    async def key_exists(
        self,
        organization_id: str,
        key: str,
        exclude_id: Optional[str] = None,
    ) -> bool:
        """Check if project key already exists in organization."""
        query = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .where(Project.key == key)
        )
        if exclude_id:
            query = query.where(Project.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_with_details(self, project_id: str) -> Optional[Project]:
        """Get project with all related data loaded."""
        from app.models.workflow import WorkflowTemplate, WorkflowColumn
        result = await self.db.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.members).selectinload(ProjectMember.user),
                selectinload(Project.components),
                selectinload(Project.lead_user),
                selectinload(Project.labels),
                selectinload(Project.workflow_template).selectinload(WorkflowTemplate.columns),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_membership(
        self,
        user_id: str,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Project]:
        """Get all projects where the user is a member."""
        query = (
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id)
            .where(Project.organization_id == organization_id)
            .options(
                selectinload(Project.members),
                selectinload(Project.components),
            )
        )

        if active_only:
            query = query.where(Project.is_active == True)

        query = query.order_by(Project.name).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    """Repository for ProjectMember operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(ProjectMember, db)

    async def create(self, obj_in: Dict[str, Any]) -> ProjectMember:
        """Create a new project member with user relationship eagerly loaded."""
        db_obj = ProjectMember(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()

        # Fetch with user relationship eagerly loaded to prevent greenlet errors
        result = await self.db.execute(
            select(ProjectMember)
            .where(ProjectMember.id == db_obj.id)
            .options(selectinload(ProjectMember.user))
        )
        refreshed_obj = result.scalar_one()
        return refreshed_obj

    async def get_by_project(self, project_id: str) -> List[ProjectMember]:
        """Get all members of a project."""
        result = await self.db.execute(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .options(selectinload(ProjectMember.user))
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: str) -> List[ProjectMember]:
        """Get all project memberships for a user."""
        result = await self.db.execute(
            select(ProjectMember)
            .where(ProjectMember.user_id == user_id)
            .options(selectinload(ProjectMember.project))
        )
        return list(result.scalars().all())

    async def is_member(self, project_id: str, user_id: str) -> bool:
        """Check if user is a member of the project."""
        result = await self.db.execute(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .where(ProjectMember.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None


class ComponentRepository(BaseRepository[Component]):
    """Repository for Component operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Component, db)

    async def get_by_project(self, project_id: str) -> List[Component]:
        """Get all components in a project."""
        result = await self.db.execute(
            select(Component)
            .where(Component.project_id == project_id)
            .order_by(Component.name)
        )
        return list(result.scalars().all())


class ProjectPinRepository(BaseRepository[ProjectPin]):
    """Repository for ProjectPin operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(ProjectPin, db)

    async def get_by_user(self, user_id: str) -> List[ProjectPin]:
        """Get all projects pinned by a user."""
        result = await self.db.execute(
            select(ProjectPin)
            .where(ProjectPin.user_id == user_id)
            .options(selectinload(ProjectPin.project))
        )
        return list(result.scalars().all())

    async def get_pin(self, user_id: str, project_id: str) -> Optional[ProjectPin]:
        """Get a specific pin record."""
        result = await self.db.execute(
            select(ProjectPin)
            .where(ProjectPin.user_id == user_id)
            .where(ProjectPin.project_id == project_id)
        )
        return result.scalar_one_or_none()

