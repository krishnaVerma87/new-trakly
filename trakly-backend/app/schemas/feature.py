"""Feature schemas."""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FeatureBase(BaseModel):
    """Base feature schema."""
    title: str = Field(..., min_length=1, max_length=500)


class FeatureCreate(FeatureBase):
    """Schema for creating a feature."""
    project_id: str
    description: Optional[str] = None
    owner_user_id: Optional[str] = None
    component_id: Optional[str] = None
    priority: str = "medium"  # critical, high, medium, low
    target_release: Optional[str] = None
    target_date: Optional[date] = None


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    owner_user_id: Optional[str] = None
    component_id: Optional[str] = None
    status: Optional[str] = None  # backlog, planning, in_progress, testing, completed, cancelled
    priority: Optional[str] = None
    target_release: Optional[str] = None
    target_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class FeatureResponse(FeatureBase):
    """Feature response schema."""
    id: str
    organization_id: str
    project_id: str
    feature_number: int
    feature_key: str  # FEAT-123
    description: Optional[str] = None
    owner_user_id: Optional[str] = None
    component_id: Optional[str] = None
    status: str
    priority: str
    target_release: Optional[str] = None
    target_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    progress_percentage: int
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LinkedIssueInfo(BaseModel):
    """Brief issue info for feature response."""
    id: str
    issue_key: str
    title: str
    issue_type: str
    status: str
    severity: Optional[str] = None
    link_type: str


class FeatureWithIssuesResponse(FeatureResponse):
    """Feature response with linked issues."""
    linked_issues: List[LinkedIssueInfo] = []
    bug_count: int = 0
    open_bug_count: int = 0

    class Config:
        from_attributes = True
