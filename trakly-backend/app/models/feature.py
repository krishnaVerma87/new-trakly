"""Feature model - first-class entity for feature tracking."""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class FeatureStatus(str, enum.Enum):
    """Feature lifecycle status."""
    BACKLOG = "backlog"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(str, enum.Enum):
    """Priority level for features and issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Feature(BaseModel):
    """
    Feature entity - first-class object for feature/roadmap tracking.

    Features can have linked issues (bugs, tasks) for tracking
    bug-per-feature metrics and feature health.
    """

    __tablename__ = "features"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        String(36),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    feature_number = Column(Integer, nullable=False)

    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Ownership
    owner_user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )
    component_id = Column(
        String(36),
        ForeignKey("components.id"),
        nullable=True,
    )

    # Status and priority
    status = Column(
        SQLEnum(FeatureStatus, values_callable=lambda x: [e.value for e in x]),
        default=FeatureStatus.BACKLOG,
        nullable=False,
        index=True,
    )
    priority = Column(
        SQLEnum(Priority, values_callable=lambda x: [e.value for e in x]),
        default=Priority.MEDIUM,
        nullable=False,
    )

    # Roadmap info
    target_release = Column(String(100), nullable=True)
    target_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)

    # Progress tracking
    progress_percentage = Column(Integer, default=0, nullable=False)

    # Created by
    created_by = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relationships
    organization = relationship("Organization")
    project = relationship("Project", back_populates="features")
    owner = relationship("User", foreign_keys=[owner_user_id])
    component = relationship("Component", back_populates="features")
    creator = relationship("User", foreign_keys=[created_by])
    issue_links = relationship(
        "FeatureIssueLink",
        back_populates="feature",
        lazy="selectin",
    )
    comments = relationship(
        "Comment",
        back_populates="feature",
        lazy="selectin",
        foreign_keys="Comment.feature_id",
    )

    @property
    def feature_key(self) -> str:
        """Generate feature key like FEAT-123."""
        return f"FEAT-{self.feature_number}"

    def __repr__(self) -> str:
        return f"<Feature {self.feature_key}: {self.title[:50]}>"
