"""Project management service."""
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.project import Project, ProjectMember, Component, ProjectPin

from app.models.label import Label
from app.repositories.project import (
    ProjectRepository,
    ProjectMemberRepository,
    ComponentRepository,
    ProjectPinRepository,
)
from app.repositories.organization import OrganizationRepository
from app.repositories.label import LabelRepository
from app.services.workflow_service import WorkflowService


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.component_repo = ComponentRepository(db)
        self.label_repo = LabelRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.pin_repo = ProjectPinRepository(db)


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

        # Assign default workflow template if not specified
        if "workflow_template_id" not in project_data or not project_data.get("workflow_template_id"):
            workflow_service = WorkflowService(self.db)
            default_template = await workflow_service.get_default_template(org_id)
            if default_template:
                project_data["workflow_template_id"] = default_template.id

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
        user_id: str = None,
    ) -> List[Project]:
        """List projects in an organization, optionally filtered by user membership."""
        if user_id:
            # Filter by user membership
            return await self.project_repo.get_by_user_membership(
                user_id=user_id,
                organization_id=organization_id,
                skip=skip,
                limit=limit,
                active_only=active_only,
            )
        else:
            # Show all projects in organization
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

    # Labels

    async def create_label(
        self,
        project_id: str,
        label_data: Dict[str, Any],
    ) -> Label:
        """Create a label in a project."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Check if label with same name already exists
        existing = await self.label_repo.get_by_name(project_id, label_data["name"])
        if existing:
            raise ValidationError(f"Label '{label_data['name']}' already exists in this project")

        label_data["project_id"] = project_id
        return await self.label_repo.create(label_data)

    async def get_labels(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Label]:
        """Get all labels in a project."""
        return await self.label_repo.get_by_project(project_id, skip, limit)

    async def update_label(
        self,
        label_id: str,
        label_data: Dict[str, Any],
    ) -> Label:
        """Update a label."""
        label = await self.label_repo.get(label_id)
        if not label:
            raise NotFoundError("Label not found")

        # Check name uniqueness if name is being updated
        if "name" in label_data:
            existing = await self.label_repo.get_by_name(label.project_id, label_data["name"])
            if existing and existing.id != label_id:
                raise ValidationError(f"Label '{label_data['name']}' already exists in this project")

        return await self.label_repo.update(label_id, label_data)

    async def delete_label(self, label_id: str) -> bool:
        """Delete a label."""
        label = await self.label_repo.get(label_id)
        if not label:
            raise NotFoundError("Label not found")

        return await self.label_repo.delete(label_id)

    # Project Pins (Favorites)

    async def pin_project(self, project_id: str, user_id: str) -> ProjectPin:
        """Pin a project for a user."""
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Check if already pinned
        existing = await self.pin_repo.get_pin(user_id, project_id)
        if existing:
            return existing

        return await self.pin_repo.create({
            "project_id": project_id,
            "user_id": user_id,
        })

    async def unpin_project(self, project_id: str, user_id: str) -> bool:
        """Unpin a project for a user."""
        pin = await self.pin_repo.get_pin(user_id, project_id)
        if not pin:
            return True

        return await self.pin_repo.delete(pin.id)

    async def get_pinned_projects(self, user_id: str) -> List[Project]:
        """Get all projects pinned by a user."""
        pins = await self.pin_repo.get_by_user(user_id)
        return [p.project for p in pins if p.project]

