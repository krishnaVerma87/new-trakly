"""Repository for comment mention operations."""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment_mention import CommentMention
from app.models.user import User
from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentMentionRepository(BaseRepository[CommentMention]):
    """Repository for comment mention CRUD operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(CommentMention, db)

    async def get_mentions_for_comment(self, comment_id: str) -> List[User]:
        """Get all users mentioned in a comment."""
        stmt = (
            select(User)
            .join(CommentMention, CommentMention.mentioned_user_id == User.id)
            .where(CommentMention.comment_id == comment_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_comments_mentioning_user(self, user_id: str) -> List[Comment]:
        """Get all comments that mention a specific user."""
        stmt = (
            select(Comment)
            .join(CommentMention, CommentMention.comment_id == Comment.id)
            .where(CommentMention.mentioned_user_id == user_id)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.issue),
                selectinload(Comment.feature),
            )
            .order_by(Comment.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_mentions(self, comment_id: str, user_ids: List[str]) -> List[CommentMention]:
        """Create mention records for multiple users."""
        mentions = []
        for user_id in user_ids:
            mention_data = {
                "comment_id": comment_id,
                "mentioned_user_id": user_id,
            }
            mention = await self.create(mention_data)
            mentions.append(mention)
        return mentions

    async def delete_mentions_for_comment(self, comment_id: str) -> None:
        """Delete all mention records for a comment (used when updating comment)."""
        stmt = select(CommentMention).where(CommentMention.comment_id == comment_id)
        result = await self.db.execute(stmt)
        mentions = result.scalars().all()
        for mention in mentions:
            await self.db.delete(mention)
        await self.db.commit()
