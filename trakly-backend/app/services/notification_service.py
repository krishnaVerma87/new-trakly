"""Notification service for creating and managing notifications."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.notification import (
    Notification,
    NotificationPreference,
    NotificationType,
    NotificationChannel,
)
from app.models.user import User
from app.repositories.notification import NotificationRepository
from app.repositories.user import UserRepository
from app.repositories.issue import IssueRepository
from app.services.email_service import EmailService
from app.services.slack_service import SlackService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)
        self.issue_repo = IssueRepository(db)
        self.email_service = EmailService()
        self.slack_service = SlackService()

    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        issue_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create a new in-app notification."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        notification_data = {
            "user_id": user_id,
            "organization_id": user.organization_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "issue_id": issue_id,
            "project_id": project_id,
            "meta_data": meta_data,
        }

        return await self.notification_repo.create(notification_data)

    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        issue_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, bool]:
        """
        Send notification through all enabled channels based on user preferences.

        Returns:
            Dict of channel -> success status
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Get user preferences
        prefs = await self.notification_repo.get_preference(
            user_id,
            notification_type,
        )

        results = {}

        # In-app notification (always create if no prefs or if enabled)
        if not prefs or prefs.in_app_enabled:
            await self.create_notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                issue_id=issue_id,
                project_id=project_id,
                meta_data=meta_data,
            )
            results[NotificationChannel.IN_APP] = True

        # Fetch issue data if issue_id provided
        issue_data = None
        if issue_id:
            issue = await self.issue_repo.get(issue_id)
            if issue:
                issue_data = {
                    "issue_key": issue.issue_key,
                    "title": issue.title,
                    "status": issue.status.value,
                    "priority": issue.priority.value,
                    "project_name": issue.project.name if issue.project else "",
                }

        # Prepare user data
        user_data = {
            "full_name": user.full_name,
            "email": user.email,
        }

        # Email notification
        if prefs and prefs.email_enabled and not prefs.email_digest:
            try:
                email_sent = await self.email_service.send_notification_email(
                    to_email=user.email,
                    subject=title,
                    body=message,
                    user=user_data,
                    issue_data=issue_data,
                )
                results[NotificationChannel.EMAIL] = email_sent
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")
                results[NotificationChannel.EMAIL] = False

        # Slack notification
        if prefs and prefs.slack_enabled:
            try:
                slack_sent = await self.slack_service.send_notification(
                    title=title,
                    message=message,
                    user=user_data,
                    issue_data=issue_data,
                )
                results[NotificationChannel.SLACK] = slack_sent
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {str(e)}")
                results[NotificationChannel.SLACK] = False

        return results

    async def mark_as_read(self, notification_id: str, user_id: str) -> Notification:
        """Mark notification as read."""
        notification = await self.notification_repo.get(notification_id)
        if not notification:
            raise NotFoundError("Notification not found")

        if notification.user_id != user_id:
            raise NotFoundError("Cannot mark other user's notification")

        return await self.notification_repo.update(notification_id, {
            "is_read": True,
            "read_at": datetime.utcnow(),
        })

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        """Get notifications for a user."""
        return await self.notification_repo.get_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        return await self.notification_repo.count_unread(user_id)
