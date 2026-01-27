"""Sprint management service."""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.sprint import Sprint
from app.repositories.sprint import SprintRepository
from app.repositories.project import ProjectRepository


class SprintService:
    """Service for sprint operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sprint_repo = SprintRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_sprint(
        self,
        sprint_data: Dict[str, Any],
        created_by: str,
    ) -> Sprint:
        """Create a new sprint."""
        project_id = sprint_data["project_id"]

        # Verify project exists
        project = await self.project_repo.get(project_id)
        if not project:
            raise NotFoundError("Project not found")

        # Validate dates
        start_date = sprint_data["start_date"]
        end_date = sprint_data["end_date"]
        if end_date <= start_date:
            raise ValidationError("End date must be after start date")

        # Get next sprint number
        sprint_number = await self.sprint_repo.get_next_sprint_number(project_id)
        sprint_data["sprint_number"] = sprint_number

        # If marked as active, deactivate other sprints
        if sprint_data.get("is_active", False):
            await self.sprint_repo.deactivate_all(project_id)

        return await self.sprint_repo.create(sprint_data)

    async def get_current_sprint(self, project_id: str) -> Optional[Sprint]:
        """Get the current active sprint for a project."""
        return await self.sprint_repo.get_current_sprint(project_id)

    async def list_sprints(
        self,
        project_id: str,
        include_completed: bool = False,
    ) -> List[Sprint]:
        """List sprints in a project."""
        return await self.sprint_repo.get_by_project(
            project_id,
            include_completed=include_completed,
        )

    async def update_sprint(
        self,
        sprint_id: str,
        sprint_data: Dict[str, Any],
    ) -> Sprint:
        """Update an existing sprint."""
        sprint = await self.sprint_repo.get(sprint_id)
        if not sprint:
            raise NotFoundError("Sprint not found")

        # Prevent updates to completed sprints
        if sprint.is_completed:
            raise ValidationError("Cannot modify a closed/completed sprint")

        # If activating, deactivate others
        if sprint_data.get("is_active") and not sprint.is_active:
            await self.sprint_repo.deactivate_all(sprint.project_id)

        return await self.sprint_repo.update(sprint_id, sprint_data)

    async def start_sprint(
        self,
        sprint_id: str,
        start_date: date,
        end_date: date,
    ) -> Sprint:
        """
        Start a sprint.
        Checks if there is already an active sprint.
        """
        sprint = await self.sprint_repo.get(sprint_id)
        if not sprint:
            raise NotFoundError("Sprint not found")

        if sprint.is_completed:
            raise ValidationError("Cannot start a completed sprint")

        # Check for other active sprints
        current = await self.sprint_repo.get_current_sprint(sprint.project_id)
        if current and current.id != sprint_id:
            raise ValidationError(f"Sprint '{current.name}' is already active. Complete it first.")

        return await self.sprint_repo.update(sprint_id, {
            "start_date": start_date,
            "end_date": end_date,
            "is_active": True,
        })

    async def complete_sprint(
        self,
        sprint_id: str,
        move_issues_to: str = 'backlog', # 'backlog' or 'new_sprint_id'
        new_sprint_id: Optional[str] = None,
    ) -> Sprint:
        """
        Complete a sprint. All tasks must be in DONE/CLOSED/WONT_FIX status before completion.
        """
        sprint = await self.sprint_repo.get(sprint_id)
        if not sprint:
            raise NotFoundError("Sprint not found")

        if not sprint.is_active:
            raise ValidationError("Sprint is not active")

        # Find incomplete issues
        from app.models.issue import IssueStatus

        incomplete_issues = [
            issue for issue in sprint.issues
            if issue.status not in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]
        ]

        # VALIDATION: Prevent completion if there are incomplete issues
        if incomplete_issues:
            incomplete_keys = [issue.issue_key for issue in incomplete_issues]
            raise ValidationError(
                f"Cannot complete sprint. {len(incomplete_issues)} task(s) are not in Done/Closed status: "
                f"{', '.join(incomplete_keys[:5])}"
                f"{' and more...' if len(incomplete_keys) > 5 else ''}"
            )

        # Mark sprint as completed (all tasks are done)
        return await self.sprint_repo.update(sprint_id, {
            "is_completed": True,
            "is_active": False,
            "status": "completed",
        })

    async def get_sprint_stats(self, sprint_id: str) -> Dict[str, Any]:
        """Get statistics for a sprint."""
        sprint = await self.sprint_repo.get(sprint_id)
        if not sprint:
            raise NotFoundError("Sprint not found")

        from app.models.issue import IssueStatus

        stats = {
            "total_issues": len(sprint.issues),
            "completed_issues": 0,
            "incomplete_issues": 0,
            "by_status": {},
            "by_priority": {},
            "by_assignee": {},
        }

        for issue in sprint.issues:
            # Status counts
            status_val = issue.status.value
            stats["by_status"][status_val] = stats["by_status"].get(status_val, 0) + 1

            # Priority counts
            priority_val = issue.priority.value
            stats["by_priority"][priority_val] = stats["by_priority"].get(priority_val, 0) + 1

            # Assignee counts
            assignee_name = issue.assignee.full_name if issue.assignee else "Unassigned"
            stats["by_assignee"][assignee_name] = stats["by_assignee"].get(assignee_name, 0) + 1

            # Completion status
            if issue.status in [IssueStatus.DONE, IssueStatus.CLOSED, IssueStatus.WONT_FIX]:
                stats["completed_issues"] += 1
            else:
                stats["incomplete_issues"] += 1

        return stats
