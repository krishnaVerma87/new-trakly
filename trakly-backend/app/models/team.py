"""Team and TeamMember models."""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class TeamRole(str, enum.Enum):
    """Role within a team."""
    LEAD = "lead"
    MEMBER = "member"


class Team(BaseModel):
    """
    Team entity for grouping users within an organization.
    """

    __tablename__ = "teams"

    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    team_type = Column(String(50), nullable=True)  # engineering, qa, product, etc.
    parent_team_id = Column(
        String(36),
        ForeignKey("teams.id"),
        nullable=True,
    )

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    parent_team = relationship("Team", remote_side="Team.id", backref="sub_teams")
    members = relationship("TeamMember", back_populates="team", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class TeamMember(BaseModel):
    """
    Association between Team and User with role.
    """

    __tablename__ = "team_members"

    team_id = Column(
        String(36),
        ForeignKey("teams.id", ondelete="CASCADE"),
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
        SQLEnum(TeamRole, values_callable=lambda x: [e.value for e in x]),
        default=TeamRole.MEMBER,
        nullable=False,
    )

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

    def __repr__(self) -> str:
        return f"<TeamMember team={self.team_id} user={self.user_id}>"
