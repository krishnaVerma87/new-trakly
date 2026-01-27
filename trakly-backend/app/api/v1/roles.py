"""Role management endpoints."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.schemas.user import RoleResponse, RoleCreate
from app.api.dependencies import get_current_user
from app.models.user import User, Role
from app.core.exceptions import DuplicateError, NotFoundError, PermissionDeniedError

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all roles in the current user's organization.
    Returns both system roles and organization-specific roles.
    """
    # Get roles for the user's organization
    result = await db.execute(
        select(Role).where(Role.organization_id == current_user.organization_id)
    )
    roles = result.scalars().all()

    return roles


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new role for the organization.
    """
    # Check if role with same name exists in org
    result = await db.execute(
        select(Role).where(
            Role.organization_id == current_user.organization_id,
            Role.name == role_in.name,
        )
    )
    if result.scalars().first():
        raise DuplicateError(f"Role '{role_in.name}' already exists in this organization")

    new_role = Role(
        organization_id=current_user.organization_id,
        name=role_in.name,
        description=role_in.description,
        is_system_role=False,
    )
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a role.
    Cannot delete system roles or roles from other organizations.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()

    if not role:
        raise NotFoundError(f"Role with ID {role_id} not found")

    if role.organization_id != current_user.organization_id:
        raise NotFoundError(f"Role with ID {role_id} not found")

    if role.is_system_role:
        raise PermissionDeniedError("Cannot delete system roles")

    await db.delete(role)
    await db.commit()
