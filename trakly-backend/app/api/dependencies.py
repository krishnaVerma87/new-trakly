"""API dependencies for authentication and authorization."""
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user.

    Extracts JWT token from Authorization header and validates it.
    """
    token = credentials.credentials
    auth_service = AuthService(db)

    try:
        user = await auth_service.get_current_user(token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def require_permission(permission: str) -> Callable:
    """
    Dependency factory for permission checking.

    Usage:
        @router.post("/", dependencies=[Depends(require_permission("issue.create"))])
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required",
            )
        return current_user

    return permission_checker


def require_organization_access(organization_id: str) -> Callable:
    """
    Dependency factory for organization access verification.
    """
    async def org_access_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization",
            )
        return current_user

    return org_access_checker
