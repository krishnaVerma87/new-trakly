"""Activity endpoints for audit logging."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.activity import Activity, EntityType
from app.repositories.activity import ActivityRepository

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_activities(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get activities for a specific entity."""
    activity_repo = ActivityRepository(db)

    # Convert string to EntityType enum
    try:
        entity_type_enum = EntityType(entity_type)
    except ValueError:
        return []

    # Fetch activities with user relationship
    from sqlalchemy import select
    result = await db.execute(
        select(Activity)
        .where(Activity.entity_type == entity_type_enum)
        .where(Activity.entity_id == entity_id)
        .where(Activity.organization_id == current_user.organization_id)
        .options(selectinload(Activity.user))
        .order_by(Activity.created_at.desc())
        .limit(limit)
    )
    activities = result.scalars().all()

    # Format activities for response
    formatted_activities = []
    for activity in activities:
        activity_dict = {
            "id": activity.id,
            "entity_type": activity.entity_type.value,
            "entity_id": activity.entity_id,
            "action_type": activity.action_type,
            "user_id": activity.user_id,
            "user": {
                "id": activity.user.id,
                "full_name": activity.user.full_name,
                "email": activity.user.email,
                "organization_id": activity.user.organization_id,
                "is_active": activity.user.is_active,
                "avatar_url": activity.user.avatar_url,
                "timezone": activity.user.timezone,
                "created_at": activity.user.created_at.isoformat(),
                "updated_at": activity.user.updated_at.isoformat(),
            } if activity.user else None,
            "old_value": json.loads(activity.old_value) if activity.old_value else None,
            "new_value": json.loads(activity.new_value) if activity.new_value else None,
            "additional_data": json.loads(activity.additional_data) if activity.additional_data else None,
            "created_at": activity.created_at.isoformat(),
        }
        formatted_activities.append(activity_dict)

    return formatted_activities


@router.get("/recent")
async def get_recent_activities(
    limit: int = Query(50, ge=1, le=200),
    entity_type: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get recent activities for the organization."""
    from sqlalchemy import select

    query = (
        select(Activity)
        .where(Activity.organization_id == current_user.organization_id)
        .options(selectinload(Activity.user))
        .order_by(Activity.created_at.desc())
        .limit(limit)
    )

    if entity_type:
        try:
            entity_type_enum = EntityType(entity_type)
            query = query.where(Activity.entity_type == entity_type_enum)
        except ValueError:
            pass

    result = await db.execute(query)
    activities = result.scalars().all()

    # Format activities for response
    formatted_activities = []
    for activity in activities:
        activity_dict = {
            "id": activity.id,
            "entity_type": activity.entity_type.value,
            "entity_id": activity.entity_id,
            "action_type": activity.action_type,
            "user_id": activity.user_id,
            "user": {
                "id": activity.user.id,
                "full_name": activity.user.full_name,
                "email": activity.user.email,
                "organization_id": activity.user.organization_id,
                "is_active": activity.user.is_active,
                "avatar_url": activity.user.avatar_url,
                "timezone": activity.user.timezone,
                "created_at": activity.user.created_at.isoformat(),
                "updated_at": activity.user.updated_at.isoformat(),
            } if activity.user else None,
            "old_value": json.loads(activity.old_value) if activity.old_value else None,
            "new_value": json.loads(activity.new_value) if activity.new_value else None,
            "additional_data": json.loads(activity.additional_data) if activity.additional_data else None,
            "created_at": activity.created_at.isoformat(),
        }
        formatted_activities.append(activity_dict)

    return formatted_activities
