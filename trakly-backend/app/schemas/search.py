"""Search and saved search schemas."""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse
from app.schemas.project import ProjectResponse


class AdvancedSearchRequest(BaseModel):
    """Request schema for advanced search."""

    project_id: str = Field(..., description="Project ID to search within")
    filter_config: Dict[str, Any] = Field(
        ...,
        description="Filter configuration",
        example={
            "status": ["new", "in_progress"],
            "priority": ["high", "critical"],
            "assignee_id": ["user-uuid"],
            "text_search": "authentication bug",
        },
    )
    skip: int = Field(0, ge=0, description="Number of results to skip")
    limit: int = Field(100, ge=1, le=500, description="Maximum results to return")


class SaveSearchRequest(BaseModel):
    """Request schema for saving a search."""

    project_id: str
    name: str = Field(..., min_length=1, max_length=255, description="Name of the saved search")
    description: Optional[str] = Field(None, description="Optional description")
    filter_config: Dict[str, Any] = Field(..., description="Filter configuration to save")
    is_shared: bool = Field(False, description="Whether to share with team")


class SavedSearchUpdate(BaseModel):
    """Request schema for updating a saved search."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None
    is_shared: Optional[bool] = None


class SavedSearchResponse(BaseModel):
    """Response schema for saved search."""

    id: str
    project_id: str
    created_by: str
    name: str
    description: Optional[str]
    filter_config: Dict[str, Any]
    is_shared: bool
    created_at: datetime
    updated_at: datetime

    # Optional relationships
    creator: Optional[UserResponse] = None
    project: Optional[ProjectResponse] = None

    class Config:
        from_attributes = True


class SearchResultsResponse(BaseModel):
    """Response schema for search results with metadata."""

    total: int = Field(..., description="Total number of results (before pagination)")
    skip: int = Field(..., description="Number of results skipped")
    limit: int = Field(..., description="Maximum results returned")
    results: List[Any] = Field(..., description="Search results (issues)")
