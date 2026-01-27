"""Service for file attachment operations."""
import os
import uuid
import logging
from typing import Optional, List, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError, PermissionDeniedError
from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository
from app.repositories.issue import IssueRepository
from app.repositories.feature import FeatureRepository

logger = logging.getLogger(__name__)


class AttachmentService:
    """Service for file attachment operations."""

    # Configuration
    UPLOAD_DIR = "/app/uploads"  # Local storage (use S3 in production)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {
        # Images
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp",
        # Documents
        ".pdf", ".doc", ".docx", ".txt", ".md", ".rtf",
        # Spreadsheets
        ".xls", ".xlsx", ".csv",
        # Archives
        ".zip", ".tar", ".gz", ".7z", ".rar",
        # Logs
        ".log",
        # Code
        ".json", ".xml", ".yaml", ".yml",
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.attachment_repo = AttachmentRepository(db)
        self.issue_repo = IssueRepository(db)
        self.feature_repo = FeatureRepository(db)

    async def upload_file(
        self,
        file: UploadFile,
        entity_type: str,  # "issue" or "feature"
        entity_id: str,
        uploaded_by: str,
    ) -> Attachment:
        """
        Upload a file attachment.

        Steps:
        1. Validate file size and type
        2. Verify entity exists
        3. Generate unique filename
        4. Save to disk
        5. Create Attachment record
        """
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > self.MAX_FILE_SIZE:
            raise ValidationError(f"File too large. Maximum size is {self.MAX_FILE_SIZE / (1024*1024):.0f} MB")

        if file_size == 0:
            raise ValidationError("File is empty")

        # Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File type '{ext}' not allowed. "
                f"Allowed types: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )

        # Verify entity exists
        if entity_type == "issue":
            entity = await self.issue_repo.get(entity_id)
            if not entity:
                raise NotFoundError("Issue not found")
        elif entity_type == "feature":
            entity = await self.feature_repo.get(entity_id)
            if not entity:
                raise NotFoundError("Feature not found")
        else:
            raise ValidationError("Invalid entity type. Must be 'issue' or 'feature'")

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{ext}"
        storage_path = os.path.join(
            self.UPLOAD_DIR,
            entity_type,
            entity_id,
            unique_filename
        )

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)

        # Save file to disk
        try:
            with open(storage_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise ValidationError(f"Failed to save file: {str(e)}")

        # Create attachment record
        attachment_data = {
            f"{entity_type}_id": entity_id,
            "uploaded_by": uploaded_by,
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_size": file_size,
            "content_type": file.content_type or "application/octet-stream",
            "storage_path": storage_path,
        }

        attachment = await self.attachment_repo.create(attachment_data)

        logger.info(
            f"File uploaded: {file.filename} ({file_size} bytes) "
            f"to {entity_type} {entity_id} by {uploaded_by}"
        )

        return attachment

    async def download_file(self, attachment_id: str) -> Tuple[str, str, str]:
        """
        Get file path and metadata for download.

        Returns: (storage_path, content_type, original_filename)
        """
        attachment = await self.attachment_repo.get(attachment_id)
        if not attachment:
            raise NotFoundError("Attachment not found")

        # Verify file exists
        if not os.path.exists(attachment.storage_path):
            logger.error(f"File not found on disk: {attachment.storage_path}")
            raise NotFoundError("File not found on disk")

        return (
            attachment.storage_path,
            attachment.content_type,
            attachment.original_filename,
        )

    async def delete_file(
        self,
        attachment_id: str,
        user_id: str,
    ) -> None:
        """
        Delete a file attachment.

        Only the uploader or admins can delete attachments.
        """
        attachment = await self.attachment_repo.get(attachment_id)
        if not attachment:
            raise NotFoundError("Attachment not found")

        # Verify permission (only uploader can delete)
        # TODO: Add admin/PM permission check
        if attachment.uploaded_by != user_id:
            raise PermissionDeniedError("You can only delete your own attachments")

        # Delete file from disk
        try:
            if os.path.exists(attachment.storage_path):
                os.remove(attachment.storage_path)
                logger.info(f"Deleted file from disk: {attachment.storage_path}")
        except Exception as e:
            logger.error(f"Failed to delete file from disk: {str(e)}")
            # Continue with database deletion even if file deletion fails

        # Delete attachment record
        await self.attachment_repo.delete(attachment_id)

        logger.info(f"Attachment deleted: {attachment_id} by {user_id}")

    async def get_attachments_for_issue(self, issue_id: str) -> List[Attachment]:
        """Get all attachments for an issue."""
        return await self.attachment_repo.get_for_issue(issue_id)

    async def get_attachments_for_feature(self, feature_id: str) -> List[Attachment]:
        """Get all attachments for a feature."""
        return await self.attachment_repo.get_for_feature(feature_id)

    async def get_attachment(self, attachment_id: str) -> Optional[Attachment]:
        """Get a single attachment by ID."""
        return await self.attachment_repo.get_with_uploader(attachment_id)
