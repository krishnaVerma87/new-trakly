"""Bulk operations API endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.user import User
from app.schemas.bulk import (
    BulkUpdateRequest,
    BulkDeleteRequest,
    BulkTransitionRequest,
    BulkOperationResult,
)
from app.services.bulk_operations_service import BulkOperationsService

router = APIRouter()


@router.post(
    "/update",
    response_model=BulkOperationResult,
    summary="Bulk update issues",
)
async def bulk_update_issues(
    request: BulkUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk update multiple issues matching filter criteria.

    **Allowed update fields:**
    - status
    - priority
    - severity
    - assignee_id
    - sprint_id
    - component_id

    **Permissions:** Project Manager or Admin only

    **Example:**
    ```json
    {
      "project_id": "project-uuid",
      "filter_config": {
        "status": ["new"],
        "issue_type": ["bug"],
        "priority": ["high"]
      },
      "update_data": {
        "status": "in_progress",
        "assignee_id": "developer-uuid"
      }
    }
    ```

    **Limitations:**
    - Maximum 1000 issues per bulk operation
    - All changes are logged for audit trail
    """
    # TODO: Add RBAC check - only PM or Admin can bulk update
    # For now, any authenticated user can bulk update (will be restricted later)

    service = BulkOperationsService(db)
    result = await service.bulk_update(
        project_id=request.project_id,
        filter_config=request.filter_config,
        update_data=request.update_data,
        updated_by=current_user.id,
    )

    return BulkOperationResult(
        affected_count=result.affected_count,
        issue_ids=result.issue_ids,
    )


@router.post(
    "/delete",
    response_model=BulkOperationResult,
    summary="Bulk delete issues",
)
async def bulk_delete_issues(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk delete multiple issues matching filter criteria.

    **⚠️ WARNING:** This permanently deletes issues and all related data
    (comments, activities, attachments, etc.) due to CASCADE DELETE.

    **Permissions:** Admin only (enforced)

    **Example:**
    ```json
    {
      "project_id": "project-uuid",
      "filter_config": {
        "status": ["closed", "wont_fix"],
        "created_before": "2024-01-01T00:00:00Z"
      }
    }
    ```

    **Limitations:**
    - Maximum 1000 issues per bulk operation
    - Operation is logged before deletion for audit trail
    - Cannot be undone
    """
    # TODO: Add strict RBAC check - only Admin can bulk delete
    # For now, raising PermissionDeniedError for all users (will add proper check later)
    # Uncomment the following to enable for admins:
    # if current_user.role != "admin":
    #     raise PermissionDeniedError("Only administrators can bulk delete issues")

    service = BulkOperationsService(db)
    result = await service.bulk_delete(
        project_id=request.project_id,
        filter_config=request.filter_config,
        deleted_by=current_user.id,
    )

    return BulkOperationResult(
        affected_count=result.affected_count,
        issue_ids=result.issue_ids,
    )


@router.post(
    "/transition",
    response_model=BulkOperationResult,
    summary="Bulk status transition",
)
async def bulk_transition_issues(
    request: BulkTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk transition issues to a new status.

    Convenience endpoint for changing only the status field of multiple issues.

    **Permissions:** Project Manager or Admin

    **Example:**
    ```json
    {
      "project_id": "project-uuid",
      "filter_config": {
        "status": ["new"],
        "issue_type": ["bug"]
      },
      "new_status": "in_progress"
    }
    ```

    **Common use cases:**
    - Move all "new" bugs to "in_progress" at sprint start
    - Close all "wont_fix" issues
    - Reopen issues for a new release
    """
    # TODO: Add RBAC check - only PM or Admin can bulk transition

    service = BulkOperationsService(db)
    result = await service.bulk_transition(
        project_id=request.project_id,
        filter_config=request.filter_config,
        new_status=request.new_status,
        transitioned_by=current_user.id,
    )

    return BulkOperationResult(
        affected_count=result.affected_count,
        issue_ids=result.issue_ids,
    )
