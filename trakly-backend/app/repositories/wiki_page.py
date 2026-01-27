"""WikiPage repository for data access operations."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.wiki_page import WikiPage


class WikiPageRepository(BaseRepository[WikiPage]):
    """Repository for WikiPage model."""

    def __init__(self, db):
        super().__init__(WikiPage, db)

    async def get_by_slug(self, project_id: str, slug: str) -> Optional[WikiPage]:
        """Get wiki page by slug within a project."""
        result = await self.db.execute(
            select(WikiPage)
            .where(and_(WikiPage.project_id == project_id, WikiPage.slug == slug))
            .options(
                selectinload(WikiPage.creator),
                selectinload(WikiPage.updater),
                selectinload(WikiPage.children),
            )
        )
        return result.scalar_one_or_none()

    async def get_root_pages(self, project_id: str) -> List[WikiPage]:
        """Get all root-level pages (no parent) for a project."""
        result = await self.db.execute(
            select(WikiPage)
            .where(and_(WikiPage.project_id == project_id, WikiPage.parent_id.is_(None)))
            .order_by(WikiPage.position)
            .options(
                selectinload(WikiPage.creator),
                selectinload(WikiPage.updater),
                selectinload(WikiPage.children),
            )
        )
        return list(result.scalars().all())

    async def get_children(self, parent_id: str) -> List[WikiPage]:
        """Get all child pages of a parent page."""
        result = await self.db.execute(
            select(WikiPage)
            .where(WikiPage.parent_id == parent_id)
            .order_by(WikiPage.position)
            .options(
                selectinload(WikiPage.creator),
                selectinload(WikiPage.updater),
                selectinload(WikiPage.children),
            )
        )
        return list(result.scalars().all())

    async def get_all_pages_for_project(self, project_id: str) -> List[WikiPage]:
        """Get all wiki pages for a project (flat list)."""
        result = await self.db.execute(
            select(WikiPage)
            .where(WikiPage.project_id == project_id)
            .order_by(WikiPage.position)
            .options(
                selectinload(WikiPage.creator),
                selectinload(WikiPage.updater),
            )
        )
        return list(result.scalars().all())

    async def slug_exists(self, project_id: str, slug: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a slug already exists in the project."""
        query = select(WikiPage).where(
            and_(WikiPage.project_id == project_id, WikiPage.slug == slug)
        )
        if exclude_id:
            query = query.where(WikiPage.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
