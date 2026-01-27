"""Comment API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService

router = APIRouter()


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a comment",
)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new comment on an issue or feature.

    Supports @mentions with markdown syntax: @[Display Name](user-uuid)

    - Automatically subscribes the author to the issue/feature
    - Automatically subscribes mentioned users to the issue/feature
    - Sends ISSUE_MENTIONED notifications to mentioned users
    - Sends ISSUE_COMMENTED notifications to watchers
    """
    service = CommentService(db)
    comment = await service.create_comment(
        comment_data=comment_data.model_dump(),
        author_id=current_user.id,
    )
    return comment


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Get a comment",
)
async def get_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single comment by ID."""
    service = CommentService(db)
    comment = await service.get_comment(comment_id)
    if not comment:
        raise NotFoundError("Comment not found")
    return comment


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment",
)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a comment's content.

    Only the comment author can edit their own comments.

    - Re-parses @mentions and creates new mention records
    - Sends notifications to newly mentioned users
    """
    if not comment_data.content:
        raise ValidationError("Content is required")

    service = CommentService(db)
    comment = await service.update_comment(
        comment_id=comment_id,
        content=comment_data.content,
        user_id=current_user.id,
    )
    return comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a comment.

    Only the comment author can delete their own comments.
    Mention records are automatically deleted via cascade.
    """
    service = CommentService(db)
    await service.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
    )
