"""Issue model with support for all issue types including bugs."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class IssueType(str, enum.Enum):
    """Types of issues."""
    BUG = "bug"
    TASK = "task"
    SUB_TASK = "sub_task"
    STORY = "story"
    IMPROVEMENT = "improvement"


class IssueStatus(str, enum.Enum):
    """Issue workflow status."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


class Priority(str, enum.Enum):
    """Priority level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Severity(str, enum.Enum):
    """Severity level for bugs."""
    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    TRIVIAL = "trivial"


class Issue(BaseModel):
    """
    Issue entity - supports Bug, Task, Sub-task, Story, Improvement.

    Bug-specific fields are nullable for non-bug types.
    Includes fields for duplicate detection.
    """

    __tablename__ = "issues"

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
    issue_number = Column(Integer, nullable=False)
    issue_key = Column(String(20), unique=True, nullable=False, index=True)  # e.g., "TRAK-123"

    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Type classification
    issue_type = Column(
        SQLEnum(IssueType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )

    # Bug-specific fields (nullable for non-bugs)
    repro_steps = Column(Text, nullable=True)
    environment = Column(String(255), nullable=True)  # "Chrome 120, macOS 14.2"
    stack_trace = Column(Text, nullable=True)
    error_signature = Column(String(500), nullable=True)  # For duplicate detection
    is_regression = Column(Boolean, default=False, nullable=False)
    affected_version = Column(String(100), nullable=True)

    # Status and priority
    status = Column(
        SQLEnum(IssueStatus, values_callable=lambda x: [e.value for e in x]),
        default=IssueStatus.NEW,
        nullable=False,
        index=True,
    )
    priority = Column(
        SQLEnum(Priority, values_callable=lambda x: [e.value for e in x]),
        default=Priority.MEDIUM,
        nullable=False,
    )
    severity = Column(
        SQLEnum(Severity, values_callable=lambda x: [e.value for e in x]),
        default=Severity.MAJOR,
        nullable=True,  # Only applicable for bugs
    )

    # Assignment
    reporter_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    assignee_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    component_id = Column(
        String(36),
        ForeignKey("components.id"),
        nullable=True,
    )

    # Parent issue (for sub-tasks)
    parent_issue_id = Column(
        String(36),
        ForeignKey("issues.id"),
        nullable=True,
    )

    # Estimation
    story_points = Column(Integer, nullable=True)
    time_estimate_minutes = Column(Integer, nullable=True)
    time_spent_minutes = Column(Integer, default=0, nullable=False)

    # Resolution
    resolution = Column(String(50), nullable=True)  # fixed, duplicate, wont_fix, cannot_reproduce
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Duplicate detection
    deduplication_hash = Column(String(64), nullable=True, index=True)  # SHA256
    similarity_vector = Column(Text, nullable=True)  # TF-IDF vector as JSON
    is_duplicate = Column(Boolean, default=False, nullable=False)
    duplicate_of_id = Column(
        String(36),
        ForeignKey("issues.id"),
        nullable=True,
    )

    # Relationships
    organization = relationship("Organization")
    project = relationship("Project", back_populates="issues")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    component = relationship("Component", back_populates="issues")
    parent_issue = relationship("Issue", remote_side="Issue.id", foreign_keys=[parent_issue_id], backref="sub_tasks")
    duplicate_of = relationship("Issue", remote_side="Issue.id", foreign_keys=[duplicate_of_id], backref="duplicates")
    labels = relationship(
        "Label",
        secondary="issue_labels",
        back_populates="issues",
        lazy="selectin",
    )
    feature_links = relationship(
        "FeatureIssueLink",
        back_populates="issue",
        lazy="selectin",
    )
    source_links = relationship(
        "IssueLink",
        foreign_keys="IssueLink.source_issue_id",
        back_populates="source_issue",
        lazy="selectin",
    )
    target_links = relationship(
        "IssueLink",
        foreign_keys="IssueLink.target_issue_id",
        back_populates="target_issue",
        lazy="selectin",
    )
    comments = relationship(
        "Comment",
        back_populates="issue",
        lazy="selectin",
        foreign_keys="Comment.issue_id",
    )

    def __repr__(self) -> str:
        return f"<Issue {self.issue_key}: {self.title[:50]}>"
