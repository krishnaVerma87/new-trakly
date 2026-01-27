"""WikiPage model for project documentation."""
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class WikiPage(BaseModel):
    """Wiki page model for project documentation with tree structure support."""

    __tablename__ = "wiki_pages"

    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(36), ForeignKey("wiki_pages.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="wiki_pages")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    parent = relationship("WikiPage", remote_side="WikiPage.id", back_populates="children")
    children = relationship(
        "WikiPage",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="WikiPage.position",
    )
