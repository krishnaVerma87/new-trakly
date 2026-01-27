"""Repository for attachment operations."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    """Repository for Attachment operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Attachment, db)

    async def get_for_issue(self, issue_id: str) -> List[Attachment]:
        """Get all attachments for an issue."""
        result = await self.db.execute(
            select(Attachment)
            .where(Attachment.issue_id == issue_id)
            .options(selectinload(Attachment.uploader))
            .order_by(Attachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_feature(self, feature_id: str) -> List[Attachment]:
        """Get all attachments for a feature."""
        result = await self.db.execute(
            select(Attachment)
            .where(Attachment.feature_id == feature_id)
            .options(selectinload(Attachment.uploader))
            .order_by(Attachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_uploader(self, attachment_id: str) -> Optional[Attachment]:
        """Get attachment with uploader information loaded."""
        result = await self.db.execute(
            select(Attachment)
            .where(Attachment.id == attachment_id)
            .options(selectinload(Attachment.uploader))
        )
        return result.scalar_one_or_none()
