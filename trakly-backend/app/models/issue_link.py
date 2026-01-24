"""IssueLink model for linking issues to each other."""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class IssueLinkType(str, enum.Enum):
    """Types of links between issues."""
    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"
    RELATES_TO = "relates_to"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is_duplicated_by"
    CLONES = "clones"
    IS_CLONED_FROM = "is_cloned_from"


class IssueLink(BaseModel):
    """
    Link between two issues with a relationship type.

    Examples:
    - TRAK-1 blocks TRAK-2
    - TRAK-3 duplicates TRAK-4
    - TRAK-5 relates to TRAK-6
    """

    __tablename__ = "issue_links"

    source_issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type = Column(
        SQLEnum(IssueLinkType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    created_by = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relationships
    source_issue = relationship(
        "Issue",
        foreign_keys=[source_issue_id],
        back_populates="source_links",
    )
    target_issue = relationship(
        "Issue",
        foreign_keys=[target_issue_id],
        back_populates="target_links",
    )
    creator = relationship("User")

    def __repr__(self) -> str:
        return f"<IssueLink {self.source_issue_id} {self.link_type.value} {self.target_issue_id}>"
