"""Team and TeamMember repositories."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team, TeamMember
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """Repository for Team operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Team, db)

    async def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Team]:
        """Get all teams in an organization."""
        result = await self.db.execute(
            select(Team)
            .where(Team.organization_id == organization_id)
            .options(selectinload(Team.members))
            .order_by(Team.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_members(self, team_id: str) -> Optional[Team]:
        """Get team with members loaded."""
        result = await self.db.execute(
            select(Team)
            .where(Team.id == team_id)
            .options(
                selectinload(Team.members).selectinload(TeamMember.user)
            )
        )
        return result.scalar_one_or_none()


class TeamMemberRepository(BaseRepository[TeamMember]):
    """Repository for TeamMember operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(TeamMember, db)

    async def get_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .options(selectinload(TeamMember.user))
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: str) -> List[TeamMember]:
        """Get all team memberships for a user."""
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.user_id == user_id)
            .options(selectinload(TeamMember.team))
        )
        return list(result.scalars().all())

    async def is_member(self, team_id: str, user_id: str) -> bool:
        """Check if user is a member of the team."""
        result = await self.db.execute(
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .where(TeamMember.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None
