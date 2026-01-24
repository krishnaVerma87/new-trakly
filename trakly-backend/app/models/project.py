"""Project, ProjectMember, and Component models."""
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class ProjectRole(str, enum.Enum):
    """Role within a project."""
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Project(BaseModel):
    """
    Project entity - container for features and issues.
    """

    __tablename__ = "projects"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    key = Column(String(10), nullable=False)  # e.g., "TRAK" for issue keys like TRAK-123
    description = Column(String(2000), nullable=True)
    lead_user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )
    default_assignee_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Issue number counter (auto-increment handled in service)
    next_issue_number = Column(String(36), default="1", nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    lead_user = relationship("User", foreign_keys=[lead_user_id])
    default_assignee = relationship("User", foreign_keys=[default_assignee_id])
    members = relationship("ProjectMember", back_populates="project", lazy="selectin")
    components = relationship("Component", back_populates="project", lazy="selectin")
    features = relationship("Feature", back_populates="project", lazy="selectin")
    issues = relationship("Issue", back_populates="project", lazy="selectin")
    labels = relationship("Label", back_populates="project", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Project {self.name} ({self.key})>"


class ProjectMember(BaseModel):
    """
    Association between Project and User with role.
    """

    __tablename__ = "project_members"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(
        SQLEnum(ProjectRole, values_callable=lambda x: [e.value for e in x]),
        default=ProjectRole.MEMBER,
        nullable=False,
    )
    assigned_by = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<ProjectMember project={self.project_id} user={self.user_id}>"


class Component(BaseModel):
    """
    Component - sub-module within a project for organizing issues.
    """

    __tablename__ = "components"

    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    lead_user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relationships
    project = relationship("Project", back_populates="components")
    lead_user = relationship("User")
    features = relationship("Feature", back_populates="component", lazy="selectin")
    issues = relationship("Issue", back_populates="component", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Component {self.name}>"
