"""Organization model for multi-tenant support."""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Organization(BaseModel):
    """
    Organization entity - root of multi-tenant hierarchy.

    Each organization has its own users, teams, projects, and issues.
    """

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    settings = Column(Text, nullable=True)  # JSON string for org-level settings
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", lazy="selectin")
    teams = relationship("Team", back_populates="organization", lazy="selectin")
    projects = relationship("Project", back_populates="organization", lazy="selectin")
    roles = relationship("Role", back_populates="organization", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Organization {self.name} ({self.slug})>"
