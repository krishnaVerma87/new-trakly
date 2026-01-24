"""Label model for categorizing issues."""
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base import BaseModel, Base


# Association table: Issue <-> Label
issue_labels = Table(
    "issue_labels",
    Base.metadata,
    Column(
        "issue_id",
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "label_id",
        String(36),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Label(BaseModel):
    """
    Label entity for categorizing and filtering issues.

    Labels are project-scoped and have a color for visual distinction.
    """

    __tablename__ = "labels"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6B7280", nullable=False)  # Hex color
    description = Column(String(255), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="labels")
    issues = relationship(
        "Issue",
        secondary=issue_labels,
        back_populates="labels",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Label {self.name}>"
