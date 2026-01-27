"""Attachment model for file uploads on issues and features."""
from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Attachment(BaseModel):
    """
    File attachment for issues or features.

    Supports various file types including images, documents, logs, and archives.
    Files are stored on disk (or S3 in production) with metadata in the database.
    """

    __tablename__ = "attachments"
    __table_args__ = (
        CheckConstraint(
            "issue_id IS NOT NULL OR feature_id IS NOT NULL",
            name="chk_attachment_entity",
        ),
    )

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
    uploaded_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File metadata
    filename = Column(String(500), nullable=False)  # Sanitized/unique filename
    original_filename = Column(String(500), nullable=False)  # User's original filename
    file_size = Column(Integer, nullable=False)  # Size in bytes
    content_type = Column(String(100), nullable=False)  # MIME type
    storage_path = Column(String(1000), nullable=False)  # Local path or S3 key

    # Relationships
    issue = relationship("Issue", back_populates="attachments")
    feature = relationship("Feature", back_populates="attachments")
    uploader = relationship("User")

    def __repr__(self) -> str:
        entity = f"issue={self.issue_id}" if self.issue_id else f"feature={self.feature_id}"
        return f"<Attachment {self.original_filename} on {entity}>"
