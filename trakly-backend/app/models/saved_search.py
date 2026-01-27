"""Saved search model for reusable issue filters."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class SavedSearch(BaseModel):
    """
    Saved search configuration for reusable issue filters.

    Allows users to save complex search criteria for quick access.
    Can be private (personal) or shared with the entire project team.
    """

    __tablename__ = "saved_searches"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # JSON configuration of filter criteria
    filter_config = Column(JSON, nullable=False)
    """
    Example filter_config:
    {
        "status": ["new", "in_progress"],
        "priority": ["high", "critical"],
        "severity": ["blocker", "critical"],
        "assignee_id": ["user-uuid"],
        "reporter_id": ["user-uuid"],
        "component_id": ["component-uuid"],
        "sprint_id": "current",
        "labels": ["label-uuid-1", "label-uuid-2"],
        "issue_type": ["bug", "task"],
        "is_regression": true,
        "is_duplicate": false,
        "created_after": "2024-01-01T00:00:00Z",
        "created_before": "2024-12-31T23:59:59Z",
        "updated_after": "2024-06-01T00:00:00Z",
        "story_points_min": 3,
        "story_points_max": 8,
        "text_search": "authentication bug"
    }
    """

    is_shared = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )  # Team-wide vs personal

    # Relationships
    project = relationship("Project")
    creator = relationship("User")

    def __repr__(self) -> str:
        shared_str = "shared" if self.is_shared else "private"
        return f"<SavedSearch {self.name} ({shared_str})>"
