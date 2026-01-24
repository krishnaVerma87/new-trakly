"""Pydantic schemas for request/response validation."""
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRolesResponse,
    RoleResponse,
)
from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.schemas.team import (
    TeamBase,
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberResponse,
)
from app.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ComponentCreate,
    ComponentResponse,
)
from app.schemas.feature import (
    FeatureBase,
    FeatureCreate,
    FeatureUpdate,
    FeatureResponse,
    FeatureWithIssuesResponse,
)
from app.schemas.issue import (
    IssueBase,
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueWithDetailsResponse,
    SimilarIssueResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
)
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithRolesResponse",
    "RoleResponse",
    # Organization
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    # Team
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    "TeamMemberCreate",
    "TeamMemberResponse",
    # Project
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectMemberCreate",
    "ProjectMemberResponse",
    "ComponentCreate",
    "ComponentResponse",
    # Feature
    "FeatureBase",
    "FeatureCreate",
    "FeatureUpdate",
    "FeatureResponse",
    "FeatureWithIssuesResponse",
    # Issue
    "IssueBase",
    "IssueCreate",
    "IssueUpdate",
    "IssueResponse",
    "IssueWithDetailsResponse",
    "SimilarIssueResponse",
    "DuplicateCheckRequest",
    "DuplicateCheckResponse",
    # Comment
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
]
