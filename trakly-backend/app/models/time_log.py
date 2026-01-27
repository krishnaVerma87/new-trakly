"""Time log model for detailed time tracking."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class TimeLog(BaseModel):
    """
    Time log entry for tracking work on issues.

    Allows detailed time tracking with start/end times and descriptions.
    """

    __tablename__ = "time_logs"

    issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)  # Null if still running
    duration_minutes = Column(Integer, nullable=True)  # Auto-calculated when ended

    description = Column(Text, nullable=True)  # What was done

    # Relationships
    issue = relationship("Issue", back_populates="time_logs")
    user = relationship("User", foreign_keys=[user_id])

    def calculate_duration(self):
        """Calculate duration in minutes."""
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        return self.duration_minutes

    def __repr__(self) -> str:
        return f"<TimeLog {self.id} - Issue {self.issue_id}>"
