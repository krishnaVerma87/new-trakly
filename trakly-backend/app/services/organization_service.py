"""Organization management service."""
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository


class OrganizationService:
    """Service for organization operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)

    async def create_organization(
        self,
        org_data: Dict[str, Any],
    ) -> Organization:
        """
        Create a new organization.

        Args:
            org_data: Organization creation data

        Returns:
            Created organization

        Raises:
            ValidationError: If slug already exists
        """
        # Check slug uniqueness
        if await self.org_repo.slug_exists(org_data["slug"]):
            raise ValidationError(f"Organization slug '{org_data['slug']}' is already in use")

        return await self.org_repo.create(org_data)

    async def get_organization(self, org_id: str) -> Organization:
        """Get organization by ID."""
        org = await self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization not found")
        return org

    async def get_by_slug(self, slug: str) -> Organization:
        """Get organization by slug."""
        org = await self.org_repo.get_by_slug(slug)
        if not org:
            raise NotFoundError("Organization not found")
        return org

    async def list_organizations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Organization]:
        """List all organizations."""
        return await self.org_repo.get_multi(
            skip=skip,
            limit=limit,
            filters={"is_active": True},
        )

    async def update_organization(
        self,
        org_id: str,
        org_data: Dict[str, Any],
    ) -> Organization:
        """Update an existing organization."""
        org = await self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization not found")

        updated_org = await self.org_repo.update(org_id, org_data)
        return updated_org

    async def delete_organization(self, org_id: str) -> bool:
        """Soft delete an organization (set is_active=False)."""
        org = await self.org_repo.get(org_id)
        if not org:
            raise NotFoundError("Organization not found")

        await self.org_repo.update(org_id, {"is_active": False})
        return True
