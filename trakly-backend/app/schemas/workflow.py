"""Pydantic schemas for workflow templates and columns."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ===== WorkflowColumn Schemas =====

class WorkflowColumnBase(BaseModel):
    """Base schema for workflow column."""
    name: str = Field(..., min_length=1, max_length=50, description="Column name")
    position: int = Field(..., ge=0, description="Position in the workflow (0-based)")
    wip_limit: Optional[int] = Field(None, ge=1, description="Work In Progress limit")
    color: Optional[str] = Field(None, max_length=20, description="Color code or name")


class WorkflowColumnCreate(WorkflowColumnBase):
    """Schema for creating a workflow column."""
    pass


class WorkflowColumnUpdate(BaseModel):
    """Schema for updating a workflow column."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    position: Optional[int] = Field(None, ge=0)
    wip_limit: Optional[int] = Field(None, ge=1)
    color: Optional[str] = Field(None, max_length=20)


class WorkflowColumnResponse(WorkflowColumnBase):
    """Response schema for workflow column."""
    id: str
    template_id: str
    created_at: datetime
    updated_at: datetime
    issue_count: Optional[int] = Field(None, description="Number of issues in this column")

    class Config:
        from_attributes = True


# ===== WorkflowTemplate Schemas =====

class WorkflowTemplateBase(BaseModel):
    """Base schema for workflow template."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, description="Template description")


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating a workflow template."""
    columns: List[WorkflowColumnCreate] = Field(..., min_items=1, max_items=20, description="Workflow columns")
    is_default: bool = Field(False, description="Set as default template for new projects")


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating a workflow template."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Response schema for workflow template."""
    id: str
    organization_id: str
    is_default: bool
    is_system: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    columns: List[WorkflowColumnResponse]
    project_count: Optional[int] = Field(None, description="Number of projects using this template")

    class Config:
        from_attributes = True


# ===== Column Update with Migration =====

class ColumnChange(BaseModel):
    """Schema for column change detection."""
    column_id: str
    old_name: str
    new_name: str
    action: str = Field(..., description="added, removed, renamed, repositioned")


class ColumnMigrationAction(BaseModel):
    """Action to take for issues in a removed/changed column."""
    old_column_id: str
    new_column_id: str = Field(..., description="Target column ID to move issues to")
    issue_ids: List[str] = Field(default_factory=list, description="Specific issue IDs to move (empty = all)")


class WorkflowColumnBatchUpdate(BaseModel):
    """Schema for batch updating workflow columns with migration."""
    columns: List[WorkflowColumnCreate] = Field(..., min_items=1, max_items=20)
    migration_actions: Optional[List[ColumnMigrationAction]] = Field(
        None,
        description="Actions for migrating issues from removed/changed columns"
    )


class ColumnMigrationWarning(BaseModel):
    """Warning about column changes that affect existing issues."""
    column_id: str
    column_name: str
    issue_count: int
    action: str = Field(..., description="removed, renamed")
    suggested_target_columns: List[WorkflowColumnResponse] = Field(
        default_factory=list,
        description="Suggested columns to migrate issues to"
    )


class WorkflowMigrationPreview(BaseModel):
    """Preview of workflow changes and required migrations."""
    template_id: str
    template_name: str
    changes: List[ColumnChange]
    warnings: List[ColumnMigrationWarning]
    safe_to_apply: bool = Field(..., description="True if no issues will be affected")
