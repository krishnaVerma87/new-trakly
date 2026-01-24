"""Issue schemas with duplicate detection support."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class LabelResponse(BaseModel):
    """Label response schema."""
    id: str
    name: str
    color: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class IssueBase(BaseModel):
    """Base issue schema."""
    title: str = Field(..., min_length=1, max_length=500)
    issue_type: str  # bug, task, sub_task, story, improvement


class IssueCreate(IssueBase):
    """Schema for creating an issue."""
    project_id: str
    description: Optional[str] = None
    priority: str = "medium"  # critical, high, medium, low
    severity: Optional[str] = "major"  # blocker, critical, major, minor, trivial (bugs only)
    component_id: Optional[str] = None
    assignee_id: Optional[str] = None
    parent_issue_id: Optional[str] = None  # for sub-tasks
    label_ids: List[str] = []

    # Bug-specific fields
    repro_steps: Optional[str] = None
    environment: Optional[str] = None
    stack_trace: Optional[str] = None
    is_regression: bool = False
    affected_version: Optional[str] = None

    # Feature linking
    feature_id: Optional[str] = None  # Auto-link to feature
    feature_link_type: Optional[str] = "implements"  # implements, blocks, relates_to, caused_by


class IssueUpdate(BaseModel):
    """Schema for updating an issue."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None  # new, in_progress, review, done, closed, wont_fix
    priority: Optional[str] = None
    severity: Optional[str] = None
    assignee_id: Optional[str] = None
    component_id: Optional[str] = None
    label_ids: Optional[List[str]] = None

    # Bug-specific
    repro_steps: Optional[str] = None
    environment: Optional[str] = None
    stack_trace: Optional[str] = None
    is_regression: Optional[bool] = None
    affected_version: Optional[str] = None

    # Resolution
    resolution: Optional[str] = None  # fixed, duplicate, wont_fix, cannot_reproduce

    # Estimation
    story_points: Optional[int] = Field(None, ge=0)
    time_estimate_minutes: Optional[int] = Field(None, ge=0)
    time_spent_minutes: Optional[int] = Field(None, ge=0)


class IssueResponse(IssueBase):
    """Issue response schema."""
    id: str
    organization_id: str
    project_id: str
    issue_number: int
    issue_key: str  # TRAK-123
    description: Optional[str] = None
    status: str
    priority: str
    severity: Optional[str] = None
    reporter_id: str
    assignee_id: Optional[str] = None
    component_id: Optional[str] = None
    parent_issue_id: Optional[str] = None

    # Bug fields
    repro_steps: Optional[str] = None
    environment: Optional[str] = None
    is_regression: bool
    affected_version: Optional[str] = None

    # Estimation
    story_points: Optional[int] = None
    time_estimate_minutes: Optional[int] = None
    time_spent_minutes: int

    # Resolution
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # Duplicate info
    is_duplicate: bool
    duplicate_of_id: Optional[str] = None

    # Labels
    labels: List[LabelResponse] = []

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IssueWithDetailsResponse(IssueResponse):
    """Issue response with full details."""
    reporter: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    # Additional relations can be added here

    class Config:
        from_attributes = True


class SimilarIssueResponse(BaseModel):
    """Similar issue for duplicate detection."""
    id: str
    issue_key: str
    title: str
    status: str
    issue_type: str
    similarity_score: int  # 0-100
    created_at: datetime


class DuplicateCheckRequest(BaseModel):
    """Request for checking duplicate issues."""
    project_id: str
    title: str
    description: Optional[str] = None


class DuplicateCheckResponse(BaseModel):
    """Response for duplicate check."""
    similar_issues: List[SimilarIssueResponse]
    suggested_deduplication_hash: str
    is_likely_duplicate: bool
