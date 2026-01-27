"""Service for comment operations with @mention support."""
import re
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.comment import Comment
from app.models.notification import NotificationType
from app.repositories.comment import CommentRepository
from app.repositories.comment_mention import CommentMentionRepository
from app.repositories.user import UserRepository
from app.repositories.issue import IssueRepository
from app.repositories.feature import FeatureRepository
from app.services.watcher_service import WatcherService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class CommentService:
    """Service for comment operations with @mention support."""

    # Regex pattern to extract @mentions: @[Display Name](user-uuid)
    MENTION_PATTERN = re.compile(r'@\[([^\]]+)\]\(([a-f0-9\-]+)\)')

    def __init__(self, db: AsyncSession):
        self.db = db
        self.comment_repo = CommentRepository(db)
        self.mention_repo = CommentMentionRepository(db)
        self.user_repo = UserRepository(db)
        self.issue_repo = IssueRepository(db)
        self.feature_repo = FeatureRepository(db)
        self.watcher_service = WatcherService(db)
        self.notification_service = NotificationService(db)

    def _extract_mentions(self, content: str) -> List[str]:
        """
        Extract user IDs from @mention syntax in content.

        Pattern: @[Display Name](user-uuid)
        Returns list of unique user IDs.
        """
        matches = self.MENTION_PATTERN.findall(content)
        # matches is list of tuples: [(display_name, user_id), ...]
        user_ids = [user_id for _, user_id in matches]
        return list(set(user_ids))  # Remove duplicates

    async def create_comment(
        self,
        comment_data: Dict[str, Any],
        author_id: str,
    ) -> Comment:
        """
        Create a new comment with @mention support.

        Steps:
        1. Validate issue/feature exists
        2. Create comment
        3. Extract @mentions from content
        4. Create CommentMention records
        5. Auto-subscribe author to issue/feature
        6. Auto-subscribe mentioned users to issue/feature
        7. Send ISSUE_MENTIONED notifications to mentioned users
        8. Send ISSUE_COMMENTED notifications to watchers (except author)
        """
        # Validate author exists
        author = await self.user_repo.get(author_id)
        if not author:
            raise NotFoundError("Author not found")

        # Ensure author_id is set
        comment_data["author_id"] = author_id

        # Validate issue or feature exists
        issue_id = comment_data.get("issue_id")
        feature_id = comment_data.get("feature_id")

        if not issue_id and not feature_id:
            raise ValidationError("Either issue_id or feature_id must be provided")

        if issue_id and feature_id:
            raise ValidationError("Cannot comment on both issue and feature")

        entity = None
        entity_type = None

        if issue_id:
            entity = await self.issue_repo.get(issue_id)
            if not entity:
                raise NotFoundError("Issue not found")
            entity_type = "issue"
        else:
            entity = await self.feature_repo.get(feature_id)
            if not entity:
                raise NotFoundError("Feature not found")
            entity_type = "feature"

        # Create the comment
        comment = await self.comment_repo.create(comment_data)

        # Extract @mentions from content
        mentioned_user_ids = self._extract_mentions(comment_data.get("content", ""))

        # Validate mentioned users exist
        valid_mentioned_ids = []
        for user_id in mentioned_user_ids:
            user = await self.user_repo.get(user_id)
            if user:
                valid_mentioned_ids.append(user_id)
            else:
                logger.warning(f"Mentioned user {user_id} not found, skipping")

        # Create CommentMention records
        if valid_mentioned_ids:
            await self.mention_repo.create_mentions(comment.id, valid_mentioned_ids)

        # Auto-subscribe author to issue/feature
        try:
            if entity_type == "issue":
                await self.watcher_service.subscribe_to_issue(
                    issue_id=issue_id,
                    user_id=author_id,
                    subscription_type="auto_comment",
                )
            else:
                await self.watcher_service.subscribe_to_feature(
                    feature_id=feature_id,
                    user_id=author_id,
                    subscription_type="auto_comment",
                )
        except Exception as e:
            logger.error(f"Failed to auto-subscribe author: {str(e)}")

        # Auto-subscribe mentioned users
        for user_id in valid_mentioned_ids:
            try:
                if entity_type == "issue":
                    await self.watcher_service.subscribe_to_issue(
                        issue_id=issue_id,
                        user_id=user_id,
                        subscription_type="auto_mention",
                    )
                else:
                    await self.watcher_service.subscribe_to_feature(
                        feature_id=feature_id,
                        user_id=user_id,
                        subscription_type="auto_mention",
                    )
            except Exception as e:
                logger.error(f"Failed to auto-subscribe mentioned user {user_id}: {str(e)}")

        # Send ISSUE_MENTIONED notifications to mentioned users
        for user_id in valid_mentioned_ids:
            try:
                await self.notification_service.send_notification(
                    user_id=user_id,
                    notification_type=NotificationType.ISSUE_MENTIONED,
                    title=f"{author.full_name} mentioned you in a comment",
                    message=f"You were mentioned in a comment on {entity_type} {entity.issue_key if entity_type == 'issue' else entity.name}",
                    issue_id=issue_id,
                    project_id=entity.project_id,
                    meta_data={
                        "comment_id": comment.id,
                        "author_id": author_id,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to send mention notification to {user_id}: {str(e)}")

        # Get all watchers for issue/feature
        try:
            if entity_type == "issue":
                watchers = await self.watcher_service.get_issue_watchers(issue_id)
            else:
                watchers = await self.watcher_service.get_feature_watchers(feature_id)

            # Send ISSUE_COMMENTED notifications to watchers (except author)
            for watcher in watchers:
                if watcher.id != author_id:
                    try:
                        await self.notification_service.send_notification(
                            user_id=watcher.id,
                            notification_type=NotificationType.ISSUE_COMMENTED,
                            title=f"{author.full_name} commented on {entity_type}",
                            message=f"New comment on {entity_type} {entity.issue_key if entity_type == 'issue' else entity.name}",
                            issue_id=issue_id,
                            project_id=entity.project_id,
                            meta_data={
                                "comment_id": comment.id,
                                "author_id": author_id,
                            },
                        )
                    except Exception as e:
                        logger.error(f"Failed to send comment notification to {watcher.id}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to get watchers or send notifications: {str(e)}")

        return comment

    async def update_comment(
        self,
        comment_id: str,
        content: str,
        user_id: str,
    ) -> Comment:
        """
        Update a comment's content and re-parse @mentions.

        Steps:
        1. Verify ownership or permission
        2. Update comment content
        3. Delete old mention records
        4. Re-parse @mentions
        5. Create new mention records
        6. Send notifications for newly mentioned users
        """
        comment = await self.comment_repo.get(comment_id)
        if not comment:
            raise NotFoundError("Comment not found")

        # Verify ownership (only author can edit their comments)
        if comment.author_id != user_id:
            raise PermissionDeniedError("You can only edit your own comments")

        # Get old mentions
        old_mentioned_users = await self.mention_repo.get_mentions_for_comment(comment_id)
        old_mentioned_ids = {user.id for user in old_mentioned_users}

        # Update comment content
        updated_comment = await self.comment_repo.update(
            comment_id,
            {"content": content}
        )

        # Delete old mention records
        await self.mention_repo.delete_mentions_for_comment(comment_id)

        # Extract new @mentions
        new_mentioned_ids = self._extract_mentions(content)

        # Validate mentioned users exist
        valid_mentioned_ids = []
        for mentioned_id in new_mentioned_ids:
            user = await self.user_repo.get(mentioned_id)
            if user:
                valid_mentioned_ids.append(mentioned_id)
            else:
                logger.warning(f"Mentioned user {mentioned_id} not found, skipping")

        # Create new mention records
        if valid_mentioned_ids:
            await self.mention_repo.create_mentions(comment_id, valid_mentioned_ids)

        # Find newly mentioned users (not in old mentions)
        newly_mentioned_ids = set(valid_mentioned_ids) - old_mentioned_ids

        # Get entity info for notifications
        issue_id = comment.issue_id
        feature_id = comment.feature_id
        entity_type = "issue" if issue_id else "feature"

        if issue_id:
            entity = await self.issue_repo.get(issue_id)
        else:
            entity = await self.feature_repo.get(feature_id)

        # Auto-subscribe newly mentioned users
        for mentioned_id in newly_mentioned_ids:
            try:
                if entity_type == "issue":
                    await self.watcher_service.subscribe_to_issue(
                        issue_id=issue_id,
                        user_id=mentioned_id,
                        subscription_type="auto_mention",
                    )
                else:
                    await self.watcher_service.subscribe_to_feature(
                        feature_id=feature_id,
                        user_id=mentioned_id,
                        subscription_type="auto_mention",
                    )
            except Exception as e:
                logger.error(f"Failed to auto-subscribe mentioned user {mentioned_id}: {str(e)}")

        # Send notifications to newly mentioned users
        author = await self.user_repo.get(comment.author_id)
        for mentioned_id in newly_mentioned_ids:
            try:
                await self.notification_service.send_notification(
                    user_id=mentioned_id,
                    notification_type=NotificationType.ISSUE_MENTIONED,
                    title=f"{author.full_name} mentioned you in a comment",
                    message=f"You were mentioned in an updated comment on {entity_type} {entity.issue_key if entity_type == 'issue' else entity.name}",
                    issue_id=issue_id,
                    project_id=entity.project_id,
                    meta_data={
                        "comment_id": comment_id,
                        "author_id": comment.author_id,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to send mention notification to {mentioned_id}: {str(e)}")

        return updated_comment

    async def delete_comment(
        self,
        comment_id: str,
        user_id: str,
    ) -> None:
        """
        Delete a comment.

        Steps:
        1. Verify ownership or permission
        2. Cascade delete comment_mentions (automatic via DB)
        3. Delete comment
        """
        comment = await self.comment_repo.get(comment_id)
        if not comment:
            raise NotFoundError("Comment not found")

        # Verify ownership (only author can delete their comments)
        # TODO: Add admin/PM permission check here
        if comment.author_id != user_id:
            raise PermissionDeniedError("You can only delete your own comments")

        # Delete comment (mentions will cascade delete)
        await self.comment_repo.delete(comment_id)

    async def get_comment(self, comment_id: str) -> Optional[Comment]:
        """Get a single comment by ID."""
        return await self.comment_repo.get(comment_id)

    async def get_comments_for_issue(
        self,
        issue_id: str,
        include_internal: bool = False,
    ) -> List[Comment]:
        """Get all comments for an issue."""
        return await self.comment_repo.get_by_issue(issue_id, include_internal)

    async def get_comments_for_feature(
        self,
        feature_id: str,
        include_internal: bool = False,
    ) -> List[Comment]:
        """Get all comments for a feature."""
        return await self.comment_repo.get_by_feature(feature_id, include_internal)
