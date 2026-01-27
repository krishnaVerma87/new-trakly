"""Wiki pages endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.schemas.wiki_page import (
    WikiPageCreate,
    WikiPageUpdate,
    WikiPageMove,
    WikiPageResponse,
    WikiPageTreeNode,
)
from app.services.wiki_page_service import WikiPageService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects/{project_id}/wiki", tags=["Wiki Pages"])


@router.post("", response_model=WikiPageResponse, status_code=status.HTTP_201_CREATED)
async def create_wiki_page(
    project_id: str,
    page_data: WikiPageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new wiki page in the project.
    """
    wiki_service = WikiPageService(db)

    try:
        page = await wiki_service.create_page(
            project_id=project_id,
            title=page_data.title,
            content=page_data.content,
            created_by=current_user.id,
            parent_id=page_data.parent_id,
            slug=page_data.slug,
        )
        return page
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tree", response_model=List[WikiPageTreeNode])
async def get_wiki_tree(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get wiki pages as hierarchical tree structure for navigation.
    """
    wiki_service = WikiPageService(db)
    tree = await wiki_service.get_page_tree(project_id)
    return tree


@router.get("/slug/{slug}", response_model=WikiPageResponse)
async def get_wiki_page_by_slug(
    project_id: str,
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get wiki page by slug within a project.
    """
    wiki_service = WikiPageService(db)

    try:
        page = await wiki_service.get_page_by_slug(project_id, slug)
        return page
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{page_id}", response_model=WikiPageResponse)
async def get_wiki_page(
    project_id: str,
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get wiki page by ID.
    """
    wiki_service = WikiPageService(db)

    try:
        page = await wiki_service.get_page(page_id)

        # Verify page belongs to project
        if page.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wiki page not found in this project",
            )

        return page
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{page_id}", response_model=WikiPageResponse)
async def update_wiki_page(
    project_id: str,
    page_id: str,
    page_data: WikiPageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update wiki page.
    """
    wiki_service = WikiPageService(db)

    try:
        # Verify page exists and belongs to project
        page = await wiki_service.get_page(page_id)
        if page.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wiki page not found in this project",
            )

        updated_page = await wiki_service.update_page(
            page_id=page_id,
            updated_by=current_user.id,
            title=page_data.title,
            content=page_data.content,
            slug=page_data.slug,
        )
        return updated_page
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wiki_page(
    project_id: str,
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete wiki page (cascades to children).
    """
    wiki_service = WikiPageService(db)

    try:
        # Verify page exists and belongs to project
        page = await wiki_service.get_page(page_id)
        if page.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wiki page not found in this project",
            )

        await wiki_service.delete_page(page_id)
        return None
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{page_id}/move", response_model=WikiPageResponse)
async def move_wiki_page(
    project_id: str,
    page_id: str,
    move_data: WikiPageMove,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Move wiki page to a new parent and/or position.
    """
    wiki_service = WikiPageService(db)

    try:
        # Verify page exists and belongs to project
        page = await wiki_service.get_page(page_id)
        if page.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wiki page not found in this project",
            )

        moved_page = await wiki_service.move_page(
            page_id=page_id,
            new_parent_id=move_data.parent_id,
            new_position=move_data.position,
        )
        return moved_page
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
