"""Service for bulk operations on issues."""
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.issue import Issue, IssueStatus, Priority, Severity
from app.repositories.issue import IssueRepository
from app.repositories.project import ProjectRepository
from app.repositories.activity import ActivityRepository

logger = logging.getLogger(__name__)


class BulkOperationResult:
    """Result of a bulk operation."""

    def __init__(self, affected_count: int, issue_ids: List[str]):
        self.affected_count = affected_count
        self.issue_ids = issue_ids


class BulkOperationsService:
    """Service for bulk operations on multiple issues."""

    # Fields that can be bulk updated
    ALLOWED_UPDATE_FIELDS = {
        "status",
        "priority",
        "severity",
        "assignee_id",
        "sprint_id",
        "component_id",
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.issue_repo = IssueRepository(db)
        self.project_repo = ProjectRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def bulk_update(
        self,
        project_id: str,
        filter_config: Dict[str, Any],
        update_data: Dict[str, Any],
        updated_by: str,
    ) -> BulkOperationResult:
        """
        Bulk update issues matching filter criteria.

        Steps:
        1. Validate update_data (only allowed fields)
        2. Find matching issue IDs via filter_config
        3. Execute bulk UPDATE statement
        4. Log bulk activity
        5. Return result with affected count and IDs
        """
        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Validate update data contains only allowed fields
        invalid_fields = set(update_data.keys()) - self.ALLOWED_UPDATE_FIELDS
        if invalid_fields:
            raise ValidationError(
                f"Cannot bulk update fields: {', '.join(invalid_fields)}. "
                f"Allowed fields: {', '.join(self.ALLOWED_UPDATE_FIELDS)}"
            )

        if not update_data:
            raise ValidationError("No update data provided")

        # Convert enum string values to enum types
        update_values = self._convert_enum_values(update_data)

        # Find matching issues
        issues = await self.issue_repo.filter_by_criteria(
            project_id=project_id,
            filter_config=filter_config,
            skip=0,
            limit=1000,  # Limit bulk operations to 1000 issues at a time
        )

        if not issues:
            return BulkOperationResult(affected_count=0, issue_ids=[])

        issue_ids = [issue.id for issue in issues]

        # Add updated_at timestamp
        update_values["updated_at"] = datetime.utcnow()

        # Execute bulk UPDATE
        stmt = (
            update(Issue)
            .where(Issue.id.in_(issue_ids))
            .values(**update_values)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        # Log bulk activity for audit trail
        await self._log_bulk_activity(
            issue_ids=issue_ids,
            action="bulk_update",
            changes=update_data,
            performed_by=updated_by,
            project_id=project_id,
        )

        logger.info(
            f"Bulk update: {result.rowcount} issues updated by {updated_by}. "
            f"Changes: {update_data}"
        )

        return BulkOperationResult(
            affected_count=result.rowcount,
            issue_ids=issue_ids,
        )

    async def bulk_delete(
        self,
        project_id: str,
        filter_config: Dict[str, Any],
        deleted_by: str,
    ) -> BulkOperationResult:
        """
        Bulk delete issues matching filter criteria.

        CAUTION: This permanently deletes issues and all related data.
        Only admins/PMs should have permission to bulk delete.
        """
        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Find matching issues
        issues = await self.issue_repo.filter_by_criteria(
            project_id=project_id,
            filter_config=filter_config,
            skip=0,
            limit=1000,  # Limit bulk operations
        )

        if not issues:
            return BulkOperationResult(affected_count=0, issue_ids=[])

        issue_ids = [issue.id for issue in issues]

        # Log before deletion (for audit)
        await self._log_bulk_activity(
            issue_ids=issue_ids,
            action="bulk_delete",
            changes={"deleted": True},
            performed_by=deleted_by,
            project_id=project_id,
        )

        # Execute bulk DELETE
        stmt = delete(Issue).where(Issue.id.in_(issue_ids))
        result = await self.db.execute(stmt)
        await self.db.commit()

        logger.warning(
            f"Bulk delete: {result.rowcount} issues deleted by {deleted_by} "
            f"from project {project_id}"
        )

        return BulkOperationResult(
            affected_count=result.rowcount,
            issue_ids=issue_ids,
        )

    async def bulk_transition(
        self,
        project_id: str,
        filter_config: Dict[str, Any],
        new_status: str,
        transitioned_by: str,
    ) -> BulkOperationResult:
        """
        Convenience method for bulk status transitions.

        Common use case: Move all "new" bugs to "in_progress".
        """
        return await self.bulk_update(
            project_id=project_id,
            filter_config=filter_config,
            update_data={"status": new_status},
            updated_by=transitioned_by,
        )

    def _convert_enum_values(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string enum values to enum types."""
        converted = {}

        for key, value in update_data.items():
            if key == "status" and isinstance(value, str):
                converted[key] = IssueStatus(value)
            elif key == "priority" and isinstance(value, str):
                converted[key] = Priority(value)
            elif key == "severity" and isinstance(value, str):
                converted[key] = Severity(value)
            else:
                converted[key] = value

        return converted

    async def _log_bulk_activity(
        self,
        issue_ids: List[str],
        action: str,
        changes: Dict[str, Any],
        performed_by: str,
        project_id: str,
    ) -> None:
        """Log bulk operation to activity table for audit trail."""
        try:
            # Create a single activity log entry for the bulk operation
            activity_data = {
                "project_id": project_id,
                "user_id": performed_by,
                "entity_type": "bulk_operation",
                "entity_id": None,  # No single entity for bulk ops
                "action": action,
                "changes": {
                    "affected_issues": len(issue_ids),
                    "issue_ids": issue_ids[:100],  # Limit to first 100 for storage
                    "updates": changes,
                },
            }
            await self.activity_repo.create(activity_data)
        except Exception as e:
            logger.error(f"Failed to log bulk activity: {str(e)}")
            # Don't fail the bulk operation if activity logging fails
