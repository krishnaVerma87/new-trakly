"""Bulk operations schemas."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class BulkUpdateRequest(BaseModel):
    """Request schema for bulk update operation."""

    project_id: str = Field(..., description="Project ID")
    filter_config: Dict[str, Any] = Field(
        ...,
        description="Filter criteria to select issues",
        example={
            "status": ["new"],
            "issue_type": ["bug"],
            "priority": ["high"],
        },
    )
    update_data: Dict[str, Any] = Field(
        ...,
        description="Fields to update",
        example={
            "status": "in_progress",
            "assignee_id": "user-uuid",
        },
    )

    @field_validator("update_data")
    @classmethod
    def validate_allowed_fields(cls, v):
        """Validate that only allowed fields are being updated."""
        allowed = {"status", "priority", "severity", "assignee_id", "sprint_id", "component_id"}
        invalid = set(v.keys()) - allowed
        if invalid:
            raise ValueError(
                f"Cannot bulk update fields: {', '.join(invalid)}. "
                f"Allowed fields: {', '.join(allowed)}"
            )
        return v


class BulkDeleteRequest(BaseModel):
    """Request schema for bulk delete operation."""

    project_id: str = Field(..., description="Project ID")
    filter_config: Dict[str, Any] = Field(
        ...,
        description="Filter criteria to select issues for deletion",
        example={
            "status": ["closed"],
            "created_before": "2024-01-01T00:00:00Z",
        },
    )


class BulkTransitionRequest(BaseModel):
    """Request schema for bulk status transition."""

    project_id: str = Field(..., description="Project ID")
    filter_config: Dict[str, Any] = Field(
        ...,
        description="Filter criteria to select issues",
        example={
            "status": ["new"],
            "issue_type": ["bug"],
        },
    )
    new_status: str = Field(
        ...,
        description="New status to transition to",
        example="in_progress",
    )


class BulkOperationResult(BaseModel):
    """Response schema for bulk operation result."""

    affected_count: int = Field(..., description="Number of issues affected")
    issue_ids: List[str] = Field(..., description="IDs of affected issues")

    class Config:
        from_attributes = True
