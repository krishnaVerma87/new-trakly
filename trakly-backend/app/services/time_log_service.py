"""Time log service."""
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.time_log import TimeLog
from app.repositories.time_log import TimeLogRepository
from app.repositories.issue import IssueRepository


class TimeLogService:
    """Service for time log operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.time_log_repo = TimeLogRepository(db)
        self.issue_repo = IssueRepository(db)

    async def start_timer(
        self,
        issue_id: str,
        user_id: str,
        description: str = None
    ) -> TimeLog:
        """Start a new time log (timer)."""
        # Verify issue exists
        issue = await self.issue_repo.get(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")

        # Check if user already has an active timer
        active_log = await self.time_log_repo.get_active_log(user_id)
        if active_log:
            raise ValidationError("You already have an active timer running. Stop it first.")

        # Create new time log
        time_log_data = {
            "issue_id": issue_id,
            "user_id": user_id,
            "started_at": datetime.utcnow(),
            "description": description,
        }

        return await self.time_log_repo.create(time_log_data)

    async def stop_timer(
        self,
        time_log_id: str,
        user_id: str
    ) -> TimeLog:
        """Stop a running timer."""
        time_log = await self.time_log_repo.get(time_log_id)
        if not time_log:
            raise NotFoundError("Time log not found")

        if time_log.user_id != user_id:
            raise ValidationError("You can only stop your own timers")

        if time_log.ended_at:
            raise ValidationError("Timer already stopped")

        # Update with end time and calculate duration
        ended_at = datetime.utcnow()
        time_log.ended_at = ended_at
        time_log.calculate_duration()

        await self.time_log_repo.update(time_log_id, {
            "ended_at": ended_at,
            "duration_minutes": time_log.duration_minutes
        })

        return await self.time_log_repo.get(time_log_id)

    async def log_time(
        self,
        issue_id: str,
        user_id: str,
        duration_minutes: int,
        description: str = None,
        started_at: datetime = None
    ) -> TimeLog:
        """Log time manually (without timer)."""
        # Verify issue exists
        issue = await self.issue_repo.get(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")

        if duration_minutes <= 0:
            raise ValidationError("Duration must be positive")

        # Create time log with manual duration
        started = started_at or datetime.utcnow()
        time_log_data = {
            "issue_id": issue_id,
            "user_id": user_id,
            "started_at": started,
            "ended_at": started,  # Same as started for manual logs
            "duration_minutes": duration_minutes,
            "description": description,
        }

        return await self.time_log_repo.create(time_log_data)

    async def get_time_logs(
        self,
        issue_id: str = None,
        user_id: str = None
    ) -> List[TimeLog]:
        """Get time logs by issue or user."""
        if issue_id:
            return await self.time_log_repo.get_by_issue(issue_id)
        elif user_id:
            return await self.time_log_repo.get_by_user(user_id)
        else:
            raise ValidationError("Either issue_id or user_id must be provided")

    async def get_time_summary(self, issue_id: str) -> Dict[str, Any]:
        """Get time tracking summary for an issue."""
        time_logs = await self.time_log_repo.get_by_issue(issue_id)

        total_minutes = sum(
            log.duration_minutes for log in time_logs if log.duration_minutes
        )

        # Group by user
        by_user = {}
        for log in time_logs:
            if log.duration_minutes:
                user_name = log.user.full_name if log.user else "Unknown"
                by_user[user_name] = by_user.get(user_name, 0) + log.duration_minutes

        return {
            "total_time_minutes": total_minutes,
            "total_time_hours": round(total_minutes / 60, 2),
            "log_count": len(time_logs),
            "by_user": by_user,
        }

    async def update_time_log(
        self,
        time_log_id: str,
        user_id: str,
        description: str = None
    ) -> TimeLog:
        """Update a time log."""
        time_log = await self.time_log_repo.get(time_log_id)
        if not time_log:
            raise NotFoundError("Time log not found")

        if time_log.user_id != user_id:
            raise ValidationError("You can only update your own time logs")

        update_data = {}
        if description is not None:
            update_data["description"] = description

        if update_data:
            await self.time_log_repo.update(time_log_id, update_data)

        return await self.time_log_repo.get(time_log_id)

    async def delete_time_log(
        self,
        time_log_id: str,
        user_id: str
    ) -> None:
        """Delete a time log."""
        time_log = await self.time_log_repo.get(time_log_id)
        if not time_log:
            raise NotFoundError("Time log not found")

        if time_log.user_id != user_id:
            raise ValidationError("You can only delete your own time logs")

        await self.time_log_repo.delete(time_log_id)
