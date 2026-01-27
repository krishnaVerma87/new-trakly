"""Comment model for issue and feature discussions."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Comment(BaseModel):
    """
    Comment on an issue or feature.

    Supports threading via parent_comment_id and internal notes.
    """

    __tablename__ = "comments"

    issue_id = Column(
        String(36),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    feature_id = Column(
        String(36),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    author_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False)  # Internal notes
    parent_comment_id = Column(
        String(36),
        ForeignKey("comments.id"),
        nullable=True,
    )

    # Relationships
    issue = relationship("Issue", back_populates="comments", foreign_keys=[issue_id])
    feature = relationship("Feature", back_populates="comments", foreign_keys=[feature_id])
    author = relationship("User")
    parent_comment = relationship("Comment", remote_side="Comment.id", backref="replies")
    mentions = relationship("CommentMention", back_populates="comment", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        target = f"issue={self.issue_id}" if self.issue_id else f"feature={self.feature_id}"
        return f"<Comment {target} by={self.author_id}>"
