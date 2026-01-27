"""WikiPage service for business logic."""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.repositories.wiki_page import WikiPageRepository
from app.core.exceptions import NotFoundError, ValidationError


class WikiPageService:
    """Service for wiki page operations."""

    def __init__(self, db):
        self.db = db
        self.wiki_page_repo = WikiPageRepository(db)

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        # Convert to lowercase and replace spaces with hyphens
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)  # Remove special characters
        text = re.sub(r'[-\s]+', '-', text)  # Replace spaces and multiple hyphens with single hyphen
        return text[:255]  # Limit to 255 characters

    async def create_page(
        self,
        project_id: str,
        title: str,
        content: str,
        created_by: str,
        parent_id: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Any:
        """Create a new wiki page."""
        # Generate slug if not provided
        if not slug:
            slug = self._slugify(title)

        # Check if slug already exists in project
        if await self.wiki_page_repo.slug_exists(project_id, slug):
            # Append counter to make it unique
            counter = 1
            base_slug = slug
            while await self.wiki_page_repo.slug_exists(project_id, slug):
                slug = f"{base_slug}-{counter}"
                counter += 1

        # If parent_id is provided, verify it exists
        if parent_id:
            parent = await self.wiki_page_repo.get(parent_id)
            if not parent or parent.project_id != project_id:
                raise NotFoundError("Parent page not found in this project")

        # Get position (last position + 1)
        if parent_id:
            siblings = await self.wiki_page_repo.get_children(parent_id)
        else:
            siblings = await self.wiki_page_repo.get_root_pages(project_id)

        position = len(siblings)

        # Create page
        page_data = {
            "project_id": project_id,
            "parent_id": parent_id,
            "title": title,
            "slug": slug,
            "content": content,
            "created_by": created_by,
            "position": position,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        page = await self.wiki_page_repo.create(page_data)
        return page

    async def get_page(self, page_id: str) -> Any:
        """Get wiki page by ID."""
        page = await self.wiki_page_repo.get(page_id)
        if not page:
            raise NotFoundError("Wiki page not found")
        return page

    async def get_page_by_slug(self, project_id: str, slug: str) -> Any:
        """Get wiki page by slug within a project."""
        page = await self.wiki_page_repo.get_by_slug(project_id, slug)
        if not page:
            raise NotFoundError(f"Wiki page '{slug}' not found")
        return page

    async def get_root_pages(self, project_id: str) -> List[Any]:
        """Get all root-level pages for a project."""
        return await self.wiki_page_repo.get_root_pages(project_id)

    async def get_page_tree(self, project_id: str) -> List[Dict[str, Any]]:
        """Get wiki pages as hierarchical tree structure."""
        root_pages = await self.wiki_page_repo.get_root_pages(project_id)

        def build_tree(page) -> Dict[str, Any]:
            return {
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "parent_id": page.parent_id,
                "position": page.position,
                "created_at": page.created_at,
                "updated_at": page.updated_at,
                "children": [build_tree(child) for child in page.children],
            }

        return [build_tree(page) for page in root_pages]

    async def update_page(
        self,
        page_id: str,
        updated_by: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Any:
        """Update wiki page."""
        page = await self.wiki_page_repo.get(page_id)
        if not page:
            raise NotFoundError("Wiki page not found")

        update_data = {"updated_by": updated_by, "updated_at": datetime.utcnow()}

        if title is not None:
            update_data["title"] = title

        if content is not None:
            update_data["content"] = content

        if slug is not None:
            # Check if new slug conflicts with existing pages (excluding current page)
            if await self.wiki_page_repo.slug_exists(page.project_id, slug, exclude_id=page_id):
                raise ValidationError(f"Slug '{slug}' already exists in this project")
            update_data["slug"] = slug

        updated_page = await self.wiki_page_repo.update(page_id, update_data)
        return updated_page

    async def delete_page(self, page_id: str) -> None:
        """Delete wiki page (cascades to children)."""
        page = await self.wiki_page_repo.get(page_id)
        if not page:
            raise NotFoundError("Wiki page not found")

        await self.wiki_page_repo.delete(page_id)

    async def move_page(
        self,
        page_id: str,
        new_parent_id: Optional[str],
        new_position: int,
    ) -> Any:
        """Move page to a new parent and/or position."""
        page = await self.wiki_page_repo.get(page_id)
        if not page:
            raise NotFoundError("Wiki page not found")

        # Verify new parent exists and is in same project
        if new_parent_id:
            new_parent = await self.wiki_page_repo.get(new_parent_id)
            if not new_parent or new_parent.project_id != page.project_id:
                raise NotFoundError("Parent page not found in this project")

            # Prevent circular references (page can't be its own ancestor)
            if new_parent_id == page_id:
                raise ValidationError("Page cannot be its own parent")

        update_data = {
            "parent_id": new_parent_id,
            "position": new_position,
            "updated_at": datetime.utcnow(),
        }

        updated_page = await self.wiki_page_repo.update(page_id, update_data)
        return updated_page
