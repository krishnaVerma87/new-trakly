"""Time log repository."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.time_log import TimeLog
from app.repositories.base import BaseRepository


class TimeLogRepository(BaseRepository[TimeLog]):
    """Repository for TimeLog operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(TimeLog, db)

    async def get_by_issue(self, issue_id: str) -> List[TimeLog]:
        """Get all time logs for an issue."""
        result = await self.db.execute(
            select(TimeLog)
            .where(TimeLog.issue_id == issue_id)
            .order_by(TimeLog.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TimeLog]:
        """Get all time logs for a user, optionally filtered by date range."""
        query = select(TimeLog).where(TimeLog.user_id == user_id)

        if start_date:
            query = query.where(TimeLog.started_at >= start_date)
        if end_date:
            query = query.where(TimeLog.started_at <= end_date)

        query = query.order_by(TimeLog.started_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_log(self, user_id: str) -> Optional[TimeLog]:
        """Get currently active (running) time log for a user."""
        result = await self.db.execute(
            select(TimeLog)
            .where(TimeLog.user_id == user_id)
            .where(TimeLog.ended_at == None)
            .order_by(TimeLog.started_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_total_time_by_issue(self, issue_id: str) -> int:
        """Get total logged time in minutes for an issue."""
        result = await self.db.execute(
            select(func.sum(TimeLog.duration_minutes))
            .where(TimeLog.issue_id == issue_id)
            .where(TimeLog.duration_minutes != None)
        )
        total = result.scalar_one_or_none()
        return total or 0
