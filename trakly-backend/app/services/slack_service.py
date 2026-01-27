"""Slack service for sending notifications to Slack."""
import logging
from typing import Dict, Any, Optional

from slack_sdk.webhook.async_client import AsyncWebhookClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Service for sending notifications to Slack via webhooks."""

    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.enabled = settings.SLACK_ENABLED and self.webhook_url is not None

    async def send_notification(
        self,
        title: str,
        message: str,
        user: Optional[Dict[str, Any]] = None,
        issue_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a notification to Slack.

        Args:
            title: Notification title
            message: Notification message
            user: User data for context
            issue_data: Issue data for notification

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Slack integration not enabled, skipping notification")
            return False

        try:
            webhook = AsyncWebhookClient(self.webhook_url)

            # Build Slack message blocks
            blocks = self._build_slack_blocks(
                title=title,
                message=message,
                issue_data=issue_data,
            )

            response = await webhook.send(
                text=title,  # Fallback text
                blocks=blocks,
            )

            if response.status_code == 200:
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}", exc_info=True)
            return False

    def _build_slack_blocks(
        self,
        title: str,
        message: str,
        issue_data: Optional[Dict[str, Any]] = None,
    ) -> list:
        """
        Build Slack message blocks.

        Args:
            title: Notification title
            message: Notification message
            issue_data: Issue data for rich formatting

        Returns:
            List of Slack message blocks
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title,
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            },
        ]

        # Add issue details if provided
        if issue_data:
            issue_key = issue_data.get("issue_key", "")
            issue_title = issue_data.get("title", "")
            issue_status = issue_data.get("status", "")
            issue_priority = issue_data.get("priority", "")

            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Issue:*\n{issue_key}: {issue_title}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{issue_status}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{issue_priority}",
                    },
                ],
            })

        blocks.append({
            "type": "divider",
        })

        return blocks
