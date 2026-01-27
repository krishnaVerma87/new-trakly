"""Watcher/follower service for issue and feature subscriptions."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.watcher import IssueWatcher, FeatureWatcher
from app.models.user import User
from app.repositories.watcher import WatcherRepository
from app.repositories.issue import IssueRepository
from app.repositories.feature import FeatureRepository


class WatcherService:
    """Service for managing issue and feature watchers."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.watcher_repo = WatcherRepository(db)
        self.issue_repo = IssueRepository(db)
        self.feature_repo = FeatureRepository(db)

    async def subscribe(
        self,
        issue_id: str,
        user_id: str,
        subscription_type: str = "manual",
    ) -> IssueWatcher:
        """Subscribe a user to an issue."""
        # Verify issue exists
        issue = await self.issue_repo.get(issue_id)
        if not issue:
            raise NotFoundError("Issue not found")

        # Check if already subscribed
        existing = await self.watcher_repo.get_watcher(issue_id, user_id)
        if existing:
            return existing  # Already subscribed, idempotent

        return await self.watcher_repo.create({
            "issue_id": issue_id,
            "user_id": user_id,
            "subscription_type": subscription_type,
        })

    async def unsubscribe(self, issue_id: str, user_id: str) -> bool:
        """Unsubscribe a user from an issue."""
        watcher = await self.watcher_repo.get_watcher(issue_id, user_id)
        if not watcher:
            return False

        return await self.watcher_repo.delete(watcher.id)

    async def get_watchers(self, issue_id: str) -> List[User]:
        """Get all users watching an issue."""
        return await self.watcher_repo.get_watchers_for_issue(issue_id)

    async def auto_subscribe_on_comment(
        self,
        issue_id: str,
        user_id: str,
    ) -> IssueWatcher:
        """Automatically subscribe user when they comment."""
        return await self.subscribe(
            issue_id,
            user_id,
            subscription_type="auto_commenter",
        )

    async def auto_subscribe_on_assign(
        self,
        issue_id: str,
        user_id: str,
    ) -> IssueWatcher:
        """Automatically subscribe user when assigned."""
        return await self.subscribe(
            issue_id,
            user_id,
            subscription_type="auto_assignee",
        )

    # Alias methods for clarity (used by comment_service)
    async def subscribe_to_issue(
        self,
        issue_id: str,
        user_id: str,
        subscription_type: str = "manual",
    ) -> IssueWatcher:
        """Subscribe a user to an issue (alias for subscribe)."""
        return await self.subscribe(issue_id, user_id, subscription_type)

    async def unsubscribe_from_issue(self, issue_id: str, user_id: str) -> bool:
        """Unsubscribe a user from an issue (alias for unsubscribe)."""
        return await self.unsubscribe(issue_id, user_id)

    async def get_issue_watchers(self, issue_id: str) -> List[User]:
        """Get all users watching an issue (alias for get_watchers)."""
        return await self.get_watchers(issue_id)

    # Feature watcher methods
    async def subscribe_to_feature(
        self,
        feature_id: str,
        user_id: str,
        subscription_type: str = "manual",
    ) -> FeatureWatcher:
        """Subscribe a user to a feature."""
        # Verify feature exists
        feature = await self.feature_repo.get(feature_id)
        if not feature:
            raise NotFoundError("Feature not found")

        # Check if already subscribed
        existing = await self.watcher_repo.get_feature_watcher(feature_id, user_id)
        if existing:
            return existing  # Already subscribed, idempotent

        return await self.watcher_repo.create_feature_watcher({
            "feature_id": feature_id,
            "user_id": user_id,
            "subscription_type": subscription_type,
        })

    async def unsubscribe_from_feature(self, feature_id: str, user_id: str) -> bool:
        """Unsubscribe a user from a feature."""
        watcher = await self.watcher_repo.get_feature_watcher(feature_id, user_id)
        if not watcher:
            return False

        return await self.watcher_repo.delete(watcher.id)

    async def get_feature_watchers(self, feature_id: str) -> List[User]:
        """Get all users watching a feature."""
        return await self.watcher_repo.get_watchers_for_feature(feature_id)
