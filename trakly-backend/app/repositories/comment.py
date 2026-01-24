"""Comment repository."""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)

    async def get_by_issue(
        self,
        issue_id: str,
        include_internal: bool = False,
    ) -> List[Comment]:
        """Get all comments for an issue."""
        query = (
            select(Comment)
            .where(Comment.issue_id == issue_id)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies),
            )
        )

        if not include_internal:
            query = query.where(Comment.is_internal == False)

        query = query.order_by(Comment.created_at.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_feature(
        self,
        feature_id: str,
        include_internal: bool = False,
    ) -> List[Comment]:
        """Get all comments for a feature."""
        query = (
            select(Comment)
            .where(Comment.feature_id == feature_id)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies),
            )
        )

        if not include_internal:
            query = query.where(Comment.is_internal == False)

        query = query.order_by(Comment.created_at.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_level_comments(
        self,
        issue_id: str = None,
        feature_id: str = None,
    ) -> List[Comment]:
        """Get only top-level comments (not replies)."""
        query = (
            select(Comment)
            .where(Comment.parent_comment_id == None)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies),
            )
        )

        if issue_id:
            query = query.where(Comment.issue_id == issue_id)
        if feature_id:
            query = query.where(Comment.feature_id == feature_id)

        query = query.order_by(Comment.created_at.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())
