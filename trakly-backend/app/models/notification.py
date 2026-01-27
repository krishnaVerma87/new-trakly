"""Notification models for in-app notifications and notification preferences."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum, Text, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_STATUS_CHANGED = "issue_status_changed"
    ISSUE_COMMENTED = "issue_commented"
    ISSUE_MENTIONED = "issue_mentioned"
    REMINDER_STALE = "reminder_stale"  # No updates in X days
    REMINDER_DUE = "reminder_due"  # Sprint ending soon
    REMINDER_CUSTOM = "reminder_custom"  # Custom rule triggered


class NotificationChannel(str, enum.Enum):
    """Notification delivery channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"


class Notification(BaseModel):
    """
    In-app notification for users.

    Stores notification history and read status.
    """

    __tablename__ = "notifications"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    notification_type = Column(
        SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )

    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)

    # Context linking
    issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Additional metadata (JSON)
    meta_data = Column(JSON, nullable=True)  # {"reminder_rule_id": "...", "days_stale": 5}

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    issue = relationship("Issue")
    project = relationship("Project")

    def __repr__(self) -> str:
        return f"<Notification {self.notification_type.value} for user {self.user_id}>"


class NotificationPreference(BaseModel):
    """
    User notification preferences per channel and type.

    Defines how users want to receive notifications.
    """

    __tablename__ = "notification_preferences"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    notification_type = Column(
        SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    # Channel enablement
    in_app_enabled = Column(Boolean, default=True, nullable=False)
    email_enabled = Column(Boolean, default=True, nullable=False)
    slack_enabled = Column(Boolean, default=False, nullable=False)

    # Email digest settings
    email_digest = Column(Boolean, default=False, nullable=False)  # Batch emails
    digest_frequency = Column(String(20), default="daily")  # daily, weekly

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<NotificationPreference {self.user_id}:{self.notification_type.value}>"
