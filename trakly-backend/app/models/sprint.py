"""Sprint/Iteration model for agile project management."""
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Sprint(BaseModel):
    """
    Sprint/Iteration for agile planning.

    Sprints organize issues into time-boxed iterations.
    """

    __tablename__ = "sprints"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)  # "Sprint 1", "Q1 2024"
    goal = Column(Text, nullable=True)  # Sprint goal/objective
    sprint_number = Column(Integer, nullable=False)  # Auto-increment per project

    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    is_active = Column(Boolean, default=False, nullable=False, index=True)  # Current sprint
    is_completed = Column(Boolean, default=False, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="sprints")
    issues = relationship("Issue", back_populates="sprint", lazy="selectin")

    def is_current_sprint(self) -> bool:
        """Check if sprint is current based on dates."""
        now = datetime.utcnow().date()
        return self.start_date <= now <= self.end_date and not self.is_completed

    def __repr__(self) -> str:
        return f"<Sprint {self.name} (Project {self.project_id})>"
