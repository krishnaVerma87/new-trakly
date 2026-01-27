"""Reminder rule model for project-level notification automation."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, JSON, DateTime
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class ReminderRule(BaseModel):
    """
    Project-level reminder rule configuration.

    Defines conditions that trigger automated notifications.
    """

    __tablename__ = "reminder_rules"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)  # "Stale high-priority issues"
    description = Column(String(1000), nullable=True)

    is_enabled = Column(Boolean, default=True, nullable=False, index=True)

    # Condition criteria (JSON schema)
    conditions = Column(JSON, nullable=False)
    """
    Example:
    {
        "sprint": "current",  # current, next, specific_id, any
        "status": ["new", "in_progress"],  # List of statuses
        "priority": ["high", "critical"],  # List of priorities
        "assignee_exists": true,  # Must have assignee
        "days_without_update": 3,  # No update in last X days
        "issue_type": ["bug", "task"]  # Optional: filter by type
    }
    """

    # Notification config
    notification_title = Column(String(500), nullable=False)
    notification_message = Column(String(2000), nullable=False)

    # Who to notify
    notify_assignee = Column(Boolean, default=True, nullable=False)
    notify_watchers = Column(Boolean, default=True, nullable=False)
    notify_project_managers = Column(Boolean, default=False, nullable=False)

    # Execution schedule
    check_frequency_minutes = Column(Integer, default=60, nullable=False)  # How often to check
    last_executed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="reminder_rules")

    def __repr__(self) -> str:
        return f"<ReminderRule {self.name} (Project {self.project_id})>"
