"""Comment mention model for tracking @mentions in comments."""
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class CommentMention(BaseModel):
    """
    Track @mentions in comments.

    When a user mentions another user in a comment using @[Name](user-uuid),
    a CommentMention record is created to track the mention and trigger notifications.
    """

    __tablename__ = "comment_mentions"
    __table_args__ = (
        UniqueConstraint("comment_id", "mentioned_user_id", name="uq_comment_mention"),
    )

    comment_id = Column(
        String(36),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mentioned_user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    comment = relationship("Comment", back_populates="mentions")
    mentioned_user = relationship("User")

    def __repr__(self) -> str:
        return f"<CommentMention comment={self.comment_id} user={self.mentioned_user_id}>"
