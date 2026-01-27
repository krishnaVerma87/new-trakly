"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ValidationError
from app.db.session import get_db
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.schemas.user import UserWithRolesResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new organization and create first admin user.
    Returns JWT token for immediate login.
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.signup(
            organization_name=signup_data.organization_name,
            organization_slug=signup_data.organization_slug,
            organization_description=signup_data.organization_description,
            user_email=signup_data.user_email,
            user_password=signup_data.user_password,
            user_full_name=signup_data.user_full_name,
            user_timezone=signup_data.user_timezone,
        )
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT token.
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.login(
            email=login_data.email,
            password=login_data.password,
        )
        return result
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserWithRolesResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's information.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user.

    Note: JWT tokens are stateless, so this endpoint is mainly
    for client-side token cleanup. Server-side token invalidation
    would require a token blacklist (not implemented in MVP).
    """
    return {"message": "Successfully logged out"}
