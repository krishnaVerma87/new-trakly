"""FeatureIssueLink model for linking issues to features."""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class FeatureIssueLinkType(str, enum.Enum):
    """Types of links between features and issues."""
    IMPLEMENTS = "implements"  # Issue implements part of the feature
    BLOCKS = "blocks"  # Issue blocks the feature
    RELATES_TO = "relates_to"  # Issue is related to the feature
    CAUSED_BY = "caused_by"  # Bug was caused by the feature


class FeatureIssueLink(BaseModel):
    """
    Link between a feature and an issue.

    Enables bug-per-feature tracking and feature health metrics.
    """

    __tablename__ = "feature_issue_links"

    feature_id = Column(
        String(36),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type = Column(
        SQLEnum(FeatureIssueLinkType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    created_by = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relationships
    feature = relationship("Feature", back_populates="issue_links")
    issue = relationship("Issue", back_populates="feature_links")
    creator = relationship("User")

    def __repr__(self) -> str:
        return f"<FeatureIssueLink feature={self.feature_id} {self.link_type.value} issue={self.issue_id}>"
