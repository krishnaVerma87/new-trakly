"""Notification endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.services.slack_service import SlackService
from app.services.email_service import EmailService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SlackTestRequest(BaseModel):
    """Request schema for testing Slack notifications."""
    webhook_url: str


class EmailTestRequest(BaseModel):
    """Request schema for testing Email notifications."""
    to_email: str


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user notifications."""
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )
    return notifications


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    notification_service = NotificationService(db)
    count = await notification_service.get_unread_count(current_user.id)
    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark notification as read."""
    notification_service = NotificationService(db)
    try:
        notification = await notification_service.mark_as_read(
            notification_id,
            current_user.id,
        )
        return notification
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/test-slack")
async def test_slack_notification(
    request: SlackTestRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a test notification to Slack.
    Used to verify webhook URL configuration.
    """
    try:
        # Create a temporary Slack service with the provided webhook URL
        from slack_sdk.webhook.async_client import AsyncWebhookClient

        webhook = AsyncWebhookClient(request.webhook_url)

        # Send test message
        response = await webhook.send(
            text="Test notification from Trakly",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 Test Notification",
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"This is a test notification from *Trakly*.\n\nTriggered by: *{current_user.full_name}* ({current_user.email})",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "✅ Your Slack integration is configured correctly!",
                    },
                },
                {
                    "type": "divider",
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Organization: {current_user.organization_id}",
                        }
                    ]
                }
            ],
        )

        if response.status_code == 200:
            return {"success": True, "message": "Test notification sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send Slack notification: {response.body}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.post("/test-email")
async def test_email_notification(
    request: EmailTestRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a test email notification.
    Used to verify SMTP configuration.
    """
    try:
        email_service = EmailService()

        # Send test email
        success = await email_service.send_notification_email(
            to_email=request.to_email,
            subject="🔔 Test Notification from Trakly",
            body=f"This is a test notification from Trakly.\n\nTriggered by: {current_user.full_name} ({current_user.email})\n\nIf you received this email, your SMTP configuration is working correctly!",
            user={"full_name": current_user.full_name, "email": current_user.email},
        )

        if success:
            return {"success": True, "message": f"Test email sent successfully to {request.to_email}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send test email. Check SMTP configuration."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send test email: {str(e)}"
        )
