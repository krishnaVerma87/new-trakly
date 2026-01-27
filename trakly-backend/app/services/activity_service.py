"""Activity logging service."""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.activity import Activity, EntityType
from app.repositories.activity import ActivityRepository


class ActivityService:
    """Service for logging activities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.activity_repo = ActivityRepository(db)

    async def log_activity(
        self,
        entity_type: EntityType,
        entity_id: str,
        action_type: str,
        organization_id: str,
        user_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> Activity:
        """Log an activity."""
        activity_data = {
            "organization_id": organization_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action_type": action_type,
            "user_id": user_id,
            "old_value": json.dumps(old_value) if old_value else None,
            "new_value": json.dumps(new_value) if new_value else None,
            "additional_data": json.dumps(additional_data) if additional_data else None,
        }

        return await self.activity_repo.create(activity_data)

    async def log_issue_created(
        self,
        issue_id: str,
        organization_id: str,
        user_id: str,
        issue_data: Dict[str, Any],
    ) -> Activity:
        """Log issue creation."""
        return await self.log_activity(
            entity_type=EntityType.ISSUE,
            entity_id=issue_id,
            action_type="created",
            organization_id=organization_id,
            user_id=user_id,
            new_value=issue_data,
        )

    async def log_issue_updated(
        self,
        issue_id: str,
        organization_id: str,
        user_id: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> Activity:
        """Log issue update."""
        return await self.log_activity(
            entity_type=EntityType.ISSUE,
            entity_id=issue_id,
            action_type="updated",
            organization_id=organization_id,
            user_id=user_id,
            old_value=old_values,
            new_value=new_values,
        )
