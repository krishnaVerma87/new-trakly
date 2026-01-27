"""Watcher model for issue subscriptions."""
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class IssueWatcher(BaseModel):
    """
    Issue watcher - users following an issue for notifications.

    Users are automatically added as watchers when:
    - They create an issue (reporter)
    - They are assigned to an issue
    - They comment on an issue
    - They manually subscribe
    """

    __tablename__ = "issue_watchers"
    __table_args__ = (
        UniqueConstraint("issue_id", "user_id", name="uq_issue_watcher"),
    )

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

    # How they became a watcher
    subscription_type = Column(
        String(20),
        nullable=False,
        default="manual",  # manual, auto_reporter, auto_assignee, auto_commenter
    )

    # Relationships
    issue = relationship("Issue", back_populates="watchers")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<IssueWatcher {self.user_id} watching {self.issue_id}>"


class FeatureWatcher(BaseModel):
    """
    Feature watcher - users following a feature for notifications.

    Users are automatically added as watchers when:
    - They create a feature (owner)
    - They comment on a feature
    - They manually subscribe
    """

    __tablename__ = "feature_watchers"
    __table_args__ = (
        UniqueConstraint("feature_id", "user_id", name="uq_feature_watcher"),
    )

    feature_id = Column(
        String(36),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # How they became a watcher
    subscription_type = Column(
        String(20),
        nullable=False,
        default="manual",  # manual, auto_owner, auto_commenter, auto_mention
    )

    # Relationships
    feature = relationship("Feature", back_populates="watchers")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<FeatureWatcher {self.user_id} watching {self.feature_id}>"
