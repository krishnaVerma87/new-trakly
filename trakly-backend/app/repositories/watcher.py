"""Watcher repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watcher import IssueWatcher, FeatureWatcher
from app.models.user import User
from app.repositories.base import BaseRepository


class WatcherRepository(BaseRepository[IssueWatcher]):
    """Repository for IssueWatcher operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(IssueWatcher, db)

    async def get_watcher(
        self,
        issue_id: str,
        user_id: str,
    ) -> Optional[IssueWatcher]:
        """Get specific watcher record."""
        result = await self.db.execute(
            select(IssueWatcher)
            .where(IssueWatcher.issue_id == issue_id)
            .where(IssueWatcher.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_watchers_for_issue(self, issue_id: str) -> List[User]:
        """Get all users watching an issue."""
        result = await self.db.execute(
            select(User)
            .join(IssueWatcher, IssueWatcher.user_id == User.id)
            .where(IssueWatcher.issue_id == issue_id)
        )
        return list(result.scalars().all())

    async def get_watched_issues(self, user_id: str) -> List[str]:
        """Get issue IDs watched by a user."""
        result = await self.db.execute(
            select(IssueWatcher.issue_id)
            .where(IssueWatcher.user_id == user_id)
        )
        return [row[0] for row in result.all()]

    # Feature watcher methods
    async def get_feature_watcher(
        self,
        feature_id: str,
        user_id: str,
    ) -> Optional[FeatureWatcher]:
        """Get specific feature watcher record."""
        result = await self.db.execute(
            select(FeatureWatcher)
            .where(FeatureWatcher.feature_id == feature_id)
            .where(FeatureWatcher.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_feature_watcher(self, data: dict) -> FeatureWatcher:
        """Create a new feature watcher."""
        from app.models.watcher import FeatureWatcher
        from uuid import uuid4
        from datetime import datetime

        watcher = FeatureWatcher(
            id=str(uuid4()),
            feature_id=data["feature_id"],
            user_id=data["user_id"],
            subscription_type=data.get("subscription_type", "manual"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(watcher)
        await self.db.commit()
        await self.db.refresh(watcher)
        return watcher

    async def get_watchers_for_feature(self, feature_id: str) -> List[User]:
        """Get all users watching a feature."""
        result = await self.db.execute(
            select(User)
            .join(FeatureWatcher, FeatureWatcher.user_id == User.id)
            .where(FeatureWatcher.feature_id == feature_id)
        )
        return list(result.scalars().all())

    async def get_watched_features(self, user_id: str) -> List[str]:
        """Get feature IDs watched by a user."""
        result = await self.db.execute(
            select(FeatureWatcher.feature_id)
            .where(FeatureWatcher.user_id == user_id)
        )
        return [row[0] for row in result.all()]
