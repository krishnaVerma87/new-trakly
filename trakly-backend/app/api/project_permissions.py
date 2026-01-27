"""Project-level permission checks for role-based access control."""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import ProjectMember, ProjectRole
from app.models.user import User


async def get_user_project_role(
    db: AsyncSession,
    user_id: str,
    project_id: str,
) -> Optional[ProjectRole]:
    """Get user's role in a project."""
    result = await db.execute(
        select(ProjectMember)
        .where(
            ProjectMember.user_id == user_id,
            ProjectMember.project_id == project_id,
        )
    )
    member = result.scalar_one_or_none()
    return member.role if member else None


async def check_project_permission(
    db: AsyncSession,
    user: User,
    project_id: str,
    required_role: ProjectRole,
    allow_org_admin: bool = True,
) -> None:
    """
    Check if user has required project role.

    Args:
        db: Database session
        user: Current user
        project_id: Project ID
        required_role: Minimum required role (admin, member, or viewer)
        allow_org_admin: If True, organization admins bypass project role checks

    Raises:
        HTTPException: If user doesn't have required permissions
    """
    # Organization admins bypass project role checks (optional)
    if allow_org_admin:
        # Check if user is org admin
        from app.lib.utils.roles import is_admin
        if is_admin(user):
            return

    # Get user's project role
    user_role = await get_user_project_role(db, user.id, project_id)

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    # Role hierarchy: admin > member > viewer
    role_hierarchy = {
        ProjectRole.ADMIN: 3,
        ProjectRole.MEMBER: 2,
        ProjectRole.VIEWER: 1,
    }

    if role_hierarchy[user_role] < role_hierarchy[required_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires '{required_role.value}' role or higher",
        )


async def require_project_admin(
    db: AsyncSession,
    user: User,
    project_id: str,
) -> None:
    """Require user to be project admin."""
    await check_project_permission(db, user, project_id, ProjectRole.ADMIN)


async def require_project_member(
    db: AsyncSession,
    user: User,
    project_id: str,
) -> None:
    """Require user to be project member or higher."""
    await check_project_permission(db, user, project_id, ProjectRole.MEMBER)


async def require_project_viewer(
    db: AsyncSession,
    user: User,
    project_id: str,
) -> None:
    """Require user to be project viewer or higher (any project member)."""
    await check_project_permission(db, user, project_id, ProjectRole.VIEWER)


async def is_project_admin(
    db: AsyncSession,
    user_id: str,
    project_id: str,
) -> bool:
    """Check if user is project admin."""
    role = await get_user_project_role(db, user_id, project_id)
    return role == ProjectRole.ADMIN


async def is_project_member_or_higher(
    db: AsyncSession,
    user_id: str,
    project_id: str,
) -> bool:
    """Check if user is project member or admin."""
    role = await get_user_project_role(db, user_id, project_id)
    return role in [ProjectRole.ADMIN, ProjectRole.MEMBER]
