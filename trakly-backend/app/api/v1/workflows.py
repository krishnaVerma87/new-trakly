"""API endpoints for workflow template management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.workflow_service import WorkflowService
from app.schemas.workflow import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
    WorkflowColumnBatchUpdate,
    WorkflowMigrationPreview,
)

router = APIRouter()


@router.post("", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_template(
    data: WorkflowTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new workflow template.

    Requires organization admin permissions.
    """
    workflow_service = WorkflowService(db)

    try:
        template = await workflow_service.create_template(
            data=data,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
        )

        # Get issue counts for response
        counts = await workflow_service.get_column_issue_counts(template.id)

        # Build response
        response_data = WorkflowTemplateResponse.model_validate(template)
        response_data.project_count = 0  # New template has no projects yet

        # Add issue counts to columns
        for col in response_data.columns:
            col.issue_count = counts.get(col.id, 0)

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    include_system: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all workflow templates for the organization.

    Query params:
    - include_system: Include system templates (default: true)
    """
    workflow_service = WorkflowService(db)

    templates = await workflow_service.list_templates(
        organization_id=current_user.organization_id,
        include_system=include_system,
    )

    # Build responses with counts
    responses = []
    for template in templates:
        # Get counts
        counts = await workflow_service.get_column_issue_counts(template.id)

        # Get project count
        project_count = len([p for p in template.projects]) if hasattr(template, 'projects') else 0

        response_data = WorkflowTemplateResponse.model_validate(template)
        response_data.project_count = project_count

        # Add issue counts to columns
        for col in response_data.columns:
            col.issue_count = counts.get(col.id, 0)

        responses.append(response_data)

    return responses


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific workflow template by ID."""
    workflow_service = WorkflowService(db)

    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )

    # Verify organization access
    if template.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get counts
    counts = await workflow_service.get_column_issue_counts(template.id)
    project_count = len([p for p in template.projects]) if hasattr(template, 'projects') else 0

    response_data = WorkflowTemplateResponse.model_validate(template)
    response_data.project_count = project_count

    # Add issue counts to columns
    for col in response_data.columns:
        col.issue_count = counts.get(col.id, 0)

    return response_data


@router.patch("/{template_id}", response_model=WorkflowTemplateResponse)
async def update_workflow_template(
    template_id: str,
    data: WorkflowTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update workflow template metadata (name, description, is_default).

    Does not update columns. Use PUT /{template_id}/columns to update columns.
    """
    workflow_service = WorkflowService(db)

    # Verify template exists and belongs to organization
    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )

    if template.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_template = await workflow_service.update_template(template_id, data)

        # Get counts
        counts = await workflow_service.get_column_issue_counts(updated_template.id)
        project_count = len([p for p in updated_template.projects]) if hasattr(updated_template, 'projects') else 0

        response_data = WorkflowTemplateResponse.model_validate(updated_template)
        response_data.project_count = project_count

        # Add issue counts to columns
        for col in response_data.columns:
            col.issue_count = counts.get(col.id, 0)

        return response_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a workflow template.

    Cannot delete:
    - System templates
    - Templates in use by projects
    """
    workflow_service = WorkflowService(db)

    # Verify template exists and belongs to organization
    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )

    if template.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        await workflow_service.delete_template(template_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{template_id}/columns/preview", response_model=WorkflowMigrationPreview)
async def preview_column_changes(
    template_id: str,
    data: WorkflowColumnBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Preview column changes and get migration warnings.

    Use this before updating columns to understand what issues will be affected.
    Returns warnings for columns being removed that contain issues.
    """
    workflow_service = WorkflowService(db)

    # Verify template exists and belongs to organization
    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )

    if template.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        preview = await workflow_service.preview_column_changes(
            template_id,
            [col.model_dump() for col in data.columns]
        )
        return preview

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{template_id}/columns", response_model=WorkflowTemplateResponse)
async def update_workflow_columns(
    template_id: str,
    data: WorkflowColumnBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update workflow columns with optional issue migration.

    If columns are removed that contain issues, you must provide migration_actions
    to specify where to move those issues.

    Use POST /{template_id}/columns/preview first to see what migrations are needed.
    """
    workflow_service = WorkflowService(db)

    # Verify template exists and belongs to organization
    template = await workflow_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )

    if template.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_template = await workflow_service.update_columns(template_id, data)

        # Get counts
        counts = await workflow_service.get_column_issue_counts(updated_template.id)
        project_count = len([p for p in updated_template.projects]) if hasattr(updated_template, 'projects') else 0

        response_data = WorkflowTemplateResponse.model_validate(updated_template)
        response_data.project_count = project_count

        # Add issue counts to columns
        for col in response_data.columns:
            col.issue_count = counts.get(col.id, 0)

        return response_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/default", response_model=WorkflowTemplateResponse)
async def get_default_template(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the default workflow template for the organization."""
    workflow_service = WorkflowService(db)

    template = await workflow_service.get_default_template(current_user.organization_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default template found"
        )

    # Get counts
    counts = await workflow_service.get_column_issue_counts(template.id)
    project_count = len([p for p in template.projects]) if hasattr(template, 'projects') else 0

    response_data = WorkflowTemplateResponse.model_validate(template)
    response_data.project_count = project_count

    # Add issue counts to columns
    for col in response_data.columns:
        col.issue_count = counts.get(col.id, 0)

    return response_data
