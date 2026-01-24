"""User, Role, and Permission models for RBAC."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel, Base


# Association table: User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        String(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("assigned_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("assigned_by", String(36), ForeignKey("users.id"), nullable=True),
)


# Association table: Role <-> Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        String(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(BaseModel):
    """
    Permission entity for granular access control.

    Format: resource.action (e.g., "issue.create", "project.delete")
    """

    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False)  # e.g., "issue", "project"
    action = Column(String(50), nullable=False)  # e.g., "create", "read", "delete"
    description = Column(String(500), nullable=True)

    # Relationships
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class Role(BaseModel):
    """
    Role entity for role-based access control.

    System roles: org_admin, project_manager, developer, reporter, viewer
    Custom roles can be created per organization.
    """

    __tablename__ = "roles"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="roles")
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class User(BaseModel):
    """
    User entity with organization membership and RBAC.
    """

    __tablename__ = "users"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        lazy="selectin",
    )
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        lazy="selectin",
    )

    @property
    def permissions(self) -> list[str]:
        """Get aggregated permissions from all roles."""
        perms = set()
        for role in self.roles:
            for permission in role.permissions:
                perms.add(permission.name)
        return list(perms)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        return permission_name in self.permissions

    def __repr__(self) -> str:
        return f"<User {self.email}>"
