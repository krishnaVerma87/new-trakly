"""User management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRolesResponse,
    BulkUserInviteRequest,
    BulkUserInviteResponse,
)
from app.services.user_service import UserService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserWithRolesResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user in the organization.
    """
    # Verify user is creating in their own organization
    if current_user.organization_id != user_data.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create user in another organization",
        )

    user_service = UserService(db)

    try:
        user = await user_service.create_user(user_data.model_dump())
        return user
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/bulk-invite", response_model=BulkUserInviteResponse, status_code=status.HTTP_200_OK)
async def bulk_invite_users(
    request: BulkUserInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk invite multiple users to the organization.

    Creates user accounts with auto-generated temporary passwords and sends welcome emails.

    **Features:**
    - Creates up to 50 users at once
    - Generates secure temporary passwords
    - Sends welcome emails with credentials
    - Assigns specified roles to each user
    - Returns detailed results for each user

    **Permissions:** Admin or Project Manager

    **Example Request:**
    ```json
    {
      "users": [
        {
          "email": "john@example.com",
          "full_name": "John Doe",
          "role_id": "developer-role-uuid"
        },
        {
          "email": "jane@example.com",
          "full_name": "Jane Smith",
          "role_id": "developer-role-uuid"
        }
      ]
    }
    ```

    **Example Response:**
    ```json
    {
      "total": 2,
      "successful": 2,
      "failed": 0,
      "results": [
        {
          "email": "john@example.com",
          "full_name": "John Doe",
          "success": true,
          "user_id": "user-uuid",
          "temp_password": "Abc123!@#Xyz",
          "error": null
        }
      ]
    }
    ```
    """
    # TODO: Add RBAC check - only Admin or Project Manager can bulk invite users

    user_service = UserService(db)

    try:
        result = await user_service.bulk_invite_users(
            users_data=[user.model_dump() for user in request.users],
            organization_id=current_user.organization_id,
            send_emails=True,
        )

        return BulkUserInviteResponse(**result)

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[UserWithRolesResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List users in the current user's organization.
    """
    user_service = UserService(db)

    users = await user_service.list_users(
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )
    return users


@router.get("/{user_id}", response_model=UserWithRolesResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.
    """
    user_service = UserService(db)

    try:
        user = await user_service.get_user(user_id)

        # Verify access to same organization
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{user_id}", response_model=UserWithRolesResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a user.
    """
    user_service = UserService(db)

    try:
        # Verify user exists and is in same organization
        user = await user_service.get_user(user_id)
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        updated_user = await user_service.update_user(
            user_id,
            user_data.model_dump(exclude_unset=True),
        )
        return updated_user
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a user (set is_active=False).
    """
    user_service = UserService(db)

    try:
        user = await user_service.get_user(user_id)
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        await user_service.delete_user(user_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
