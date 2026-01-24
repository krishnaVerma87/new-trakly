"""Project management service."""
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.project import Project, ProjectMember, Component
from app.repositories.project import (
    ProjectRepository,
    ProjectMemberRepository,
    ComponentRepository,
)
from app.repositories.organization import OrganizationRepository


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.component_repo = ComponentRepository(db)
        self.org_repo = OrganizationRepository(db)

    async def create_project(
        self,
        project_data: Dict[str, Any],
    ) -> Project:
        """
        Create a new project.

        Args:
            project_data: Project creation data

        Returns:
            Created project

        Raises:
            ValidationError: If key already exists in org
        """
        org_id = project_data["organization_id"]

        # Verify organization exists
        org = await self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization not found")

        # Check key uniqueness within organization
        if await self.project_repo.key_exists(org_id, project_data["key"]):
            raise ValidationError(
                f"Project key '{project_data['key']}' is already in use in this organization"
            )

        # Initialize issue counter
        project_data["next_issue_number"] = "1"

        return await self.project_repo.create(project_data)

    async def get_project(self, project_id: str) -> Project:
        """Get project by ID with details."""
        project = await self.project_repo.get_with_details(project_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    async def list_projects(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Project]:
        """List projects in an organization."""
        return await self.project_repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )

    async def update_project(
        self,
        project_id: str,
        project_data: Dict[str, Any],
    ) -> Project:
        """Update an existing project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        updated_project = await self.project_repo.update(project_id, project_data)
        return updated_project

    async def delete_project(self, project_id: str) -> bool:
        """Soft delete a project (set is_active=False)."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        await self.project_repo.update(project_id, {"is_active": False})
        return True

    # Project Members

    async def add_member(
        self,
        project_id: str,
        user_id: str,
        role: str = "member",
        assigned_by: str = None,
    ) -> ProjectMember:
        """Add a member to a project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Check if already a member
        if await self.member_repo.is_member(project_id, user_id):
            raise ValidationError("User is already a member of this project")

        member_data = {
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
            "assigned_by": assigned_by,
        }

        return await self.member_repo.create(member_data)

    async def remove_member(
        self,
        project_id: str,
        user_id: str,
    ) -> bool:
        """Remove a member from a project."""
        members = await self.member_repo.get_by_project(project_id)
        member = next(
            (m for m in members if m.user_id == user_id),
            None,
        )

        if not member:
            raise NotFoundError("Member not found in project")

        return await self.member_repo.delete(member.id)

    async def get_members(self, project_id: str) -> List[ProjectMember]:
        """Get all members of a project."""
        return await self.member_repo.get_by_project(project_id)

    # Components

    async def create_component(
        self,
        project_id: str,
        component_data: Dict[str, Any],
    ) -> Component:
        """Create a component in a project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        component_data["project_id"] = project_id
        return await self.component_repo.create(component_data)

    async def get_components(self, project_id: str) -> List[Component]:
        """Get all components in a project."""
        return await self.component_repo.get_by_project(project_id)
