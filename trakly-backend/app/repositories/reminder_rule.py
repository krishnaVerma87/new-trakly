"""Reminder rule repository."""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.reminder_rule import ReminderRule
from app.repositories.base import BaseRepository


class ReminderRuleRepository(BaseRepository[ReminderRule]):
    """Repository for ReminderRule operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(ReminderRule, db)

    async def get_by_project(self, project_id: str) -> List[ReminderRule]:
        """Get all reminder rules for a project."""
        result = await self.db.execute(
            select(ReminderRule)
            .where(ReminderRule.project_id == project_id)
            .order_by(ReminderRule.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_enabled_rules(self) -> List[ReminderRule]:
        """Get all enabled reminder rules across all projects."""
        result = await self.db.execute(
            select(ReminderRule)
            .where(ReminderRule.is_enabled == True)
        )
        return list(result.scalars().all())

    async def get_rules_to_execute(self) -> List[ReminderRule]:
        """Get rules that need to be executed based on their schedule."""
        result = await self.db.execute(
            select(ReminderRule)
            .where(ReminderRule.is_enabled == True)
        )
        rules = list(result.scalars().all())

        # Filter rules that haven't been executed recently
        now = datetime.utcnow()
        rules_to_execute = []
        for rule in rules:
            if rule.last_executed_at is None:
                rules_to_execute.append(rule)
            else:
                time_since_last = now - rule.last_executed_at
                if time_since_last >= timedelta(minutes=rule.check_frequency_minutes):
                    rules_to_execute.append(rule)

        return rules_to_execute
