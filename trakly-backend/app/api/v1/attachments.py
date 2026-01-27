"""File attachment API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile, Path
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.user import User
from app.schemas.attachment import AttachmentResponse
from app.services.attachment_service import AttachmentService

router = APIRouter()


@router.post(
    "/issues/{issue_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file to issue",
)
async def upload_file_to_issue(
    issue_id: str = Path(..., description="Issue ID"),
    file: UploadFile = File(..., description="File to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file attachment to an issue.

    **Allowed file types:**
    - Images: jpg, jpeg, png, gif, webp, svg, bmp
    - Documents: pdf, doc, docx, txt, md, rtf
    - Spreadsheets: xls, xlsx, csv
    - Archives: zip, tar, gz, 7z, rar
    - Logs: log
    - Code: json, xml, yaml, yml

    **File size limit:** 10 MB

    **Returns:** Attachment metadata with download URL
    """
    service = AttachmentService(db)
    attachment = await service.upload_file(
        file=file,
        entity_type="issue",
        entity_id=issue_id,
        uploaded_by=current_user.id,
    )

    # Add download URL
    return AttachmentResponse(
        **attachment.__dict__,
        download_url=f"/api/v1/attachments/{attachment.id}/download",
    )


@router.post(
    "/features/{feature_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file to feature",
)
async def upload_file_to_feature(
    feature_id: str = Path(..., description="Feature ID"),
    file: UploadFile = File(..., description="File to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file attachment to a feature.

    See upload_file_to_issue for allowed file types and size limits.
    """
    service = AttachmentService(db)
    attachment = await service.upload_file(
        file=file,
        entity_type="feature",
        entity_id=feature_id,
        uploaded_by=current_user.id,
    )

    return AttachmentResponse(
        **attachment.__dict__,
        download_url=f"/api/v1/attachments/{attachment.id}/download",
    )


@router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse,
    summary="Get attachment metadata",
)
async def get_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attachment metadata (without downloading the file)."""
    service = AttachmentService(db)
    attachment = await service.get_attachment(attachment_id)
    if not attachment:
        raise NotFoundError("Attachment not found")

    return AttachmentResponse(
        **attachment.__dict__,
        download_url=f"/api/v1/attachments/{attachment.id}/download",
    )


@router.get(
    "/{attachment_id}/download",
    response_class=FileResponse,
    summary="Download file",
)
async def download_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download the file attachment.

    Returns the file as a binary download with appropriate Content-Disposition header.
    """
    service = AttachmentService(db)
    storage_path, content_type, original_filename = await service.download_file(
        attachment_id
    )

    return FileResponse(
        path=storage_path,
        media_type=content_type,
        filename=original_filename,
        headers={
            "Content-Disposition": f'attachment; filename="{original_filename}"'
        },
    )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete attachment",
)
async def delete_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a file attachment.

    Only the uploader can delete their own attachments.
    The file is removed from disk and the database record is deleted.
    """
    service = AttachmentService(db)
    await service.delete_file(
        attachment_id=attachment_id,
        user_id=current_user.id,
    )
