"""Notification repository."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationPreference, NotificationType
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )

        if unread_only:
            query = query.where(Notification.is_read == False)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_unread(self, user_id: str) -> int:
        """Count unread notifications."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        return result.scalar_one()

    async def get_preference(
        self,
        user_id: str,
        notification_type: NotificationType,
    ) -> Optional[NotificationPreference]:
        """Get user notification preference."""
        result = await self.db.execute(
            select(NotificationPreference)
            .where(NotificationPreference.user_id == user_id)
            .where(NotificationPreference.notification_type == notification_type)
        )
        return result.scalar_one_or_none()
