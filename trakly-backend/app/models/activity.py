"""Activity model for audit logging."""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class EntityType(str, enum.Enum):
    """Types of entities that can have activities."""
    ISSUE = "issue"
    FEATURE = "feature"
    PROJECT = "project"
    COMMENT = "comment"
    SPRINT = "sprint"
    NOTIFICATION = "notification"


class Activity(BaseModel):
    """
    Activity log entry for audit trail.

    Tracks all changes to issues, features, and projects.
    """

    __tablename__ = "activities"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    entity_type = Column(
        SQLEnum(EntityType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    entity_id = Column(String(36), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # created, status_changed, assigned, etc.
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,  # System actions may not have a user
    )
    old_value = Column(Text, nullable=True)  # JSON string
    new_value = Column(Text, nullable=True)  # JSON string
    additional_data = Column(Text, nullable=True)  # Additional context as JSON

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Activity {self.entity_type.value}:{self.entity_id} {self.action_type}>"
