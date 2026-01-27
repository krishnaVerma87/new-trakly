"""Email service for sending notification emails."""
import logging
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        user: Optional[Dict[str, Any]] = None,
        issue_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a notification email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            user: User data for personalization
            issue_data: Issue data for email content

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create HTML email content
            html_content = self._create_html_email(
                subject=subject,
                body=body,
                user=user,
                issue_data=issue_data,
            )

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add plain text and HTML parts
            text_part = MIMEText(body, "plain")
            html_part = MIMEText(html_content, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send email
            await self._send_email(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            return False

    async def _send_email(self, message: MIMEMultipart) -> None:
        """Send email via SMTP."""
        # For port 587 with AWS SES, use start_tls parameter
        if self.smtp_port == 587 and self.smtp_use_tls:
            smtp_params = {
                "hostname": self.smtp_host,
                "port": self.smtp_port,
                "start_tls": True,  # Automatically call STARTTLS after connection
            }

            if self.smtp_user and self.smtp_password:
                smtp_params["username"] = self.smtp_user
                smtp_params["password"] = self.smtp_password

            async with aiosmtplib.SMTP(**smtp_params) as smtp:
                await smtp.send_message(message)
        else:
            # For port 465 (direct TLS) or non-TLS connections
            smtp_params = {
                "hostname": self.smtp_host,
                "port": self.smtp_port,
            }

            if self.smtp_port == 465 and self.smtp_use_tls:
                smtp_params["use_tls"] = True

            if self.smtp_user and self.smtp_password:
                smtp_params["username"] = self.smtp_user
                smtp_params["password"] = self.smtp_password

            async with aiosmtplib.SMTP(**smtp_params) as smtp:
                await smtp.send_message(message)

    def _create_html_email(
        self,
        subject: str,
        body: str,
        user: Optional[Dict[str, Any]] = None,
        issue_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create HTML email template.

        Args:
            subject: Email subject
            body: Email body text
            user: User data for personalization
            issue_data: Issue data for content

        Returns:
            HTML email content
        """
        user_name = user.get("full_name", "User") if user else "User"

        # Build issue details section if issue data provided
        issue_section = ""
        if issue_data:
            issue_key = issue_data.get("issue_key", "")
            issue_title = issue_data.get("title", "")
            issue_status = issue_data.get("status", "")
            issue_priority = issue_data.get("priority", "")
            project_name = issue_data.get("project_name", "")

            issue_section = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">{issue_key}: {issue_title}</h3>
                <p style="margin: 5px 0;"><strong>Project:</strong> {project_name}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> {issue_status}</p>
                <p style="margin: 5px 0;"><strong>Priority:</strong> {issue_priority}</p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{settings.APP_NAME}</h1>
            </div>

            <div style="background-color: white; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 5px 5px;">
                <p style="margin-top: 0;">Hi {user_name},</p>

                <p>{body}</p>

                {issue_section}

                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>{settings.APP_NAME} Team</strong>
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                <p>This is an automated notification from {settings.APP_NAME}.</p>
                <p>© 2026 {settings.APP_NAME}. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return html

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        temp_password: str,
        organization_name: str,
        login_url: str = None,
    ) -> bool:
        """
        Send a welcome email to a new user with their temporary password.

        Args:
            to_email: User's email address
            user_name: User's full name
            temp_password: Temporary password for first login
            organization_name: Name of the organization
            login_url: Optional custom login URL

        Returns:
            True if email sent successfully, False otherwise
        """
        if not login_url:
            login_url = f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else "your Trakly instance"

        subject = f"Welcome to {organization_name} on {settings.APP_NAME}"

        body = f"""
Welcome to {organization_name}!

Your account has been created on {settings.APP_NAME}. Here are your login credentials:

Email: {to_email}
Temporary Password: {temp_password}

Please log in and change your password as soon as possible for security reasons.

Login at: {login_url}
"""

        html_content = self._create_welcome_html_email(
            user_name=user_name,
            organization_name=organization_name,
            to_email=to_email,
            temp_password=temp_password,
            login_url=login_url,
        )

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add plain text and HTML parts
            text_part = MIMEText(body, "plain")
            html_part = MIMEText(html_content, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send email
            await self._send_email(message)

            logger.info(f"Welcome email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {to_email}: {str(e)}", exc_info=True)
            return False

    def _create_welcome_html_email(
        self,
        user_name: str,
        organization_name: str,
        to_email: str,
        temp_password: str,
        login_url: str,
    ) -> str:
        """Create HTML welcome email template."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to {settings.APP_NAME}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{settings.APP_NAME}</h1>
            </div>

            <div style="background-color: white; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 5px 5px;">
                <h2 style="color: #4f46e5; margin-top: 0;">Welcome to {organization_name}!</h2>

                <p>Hi {user_name},</p>

                <p>Your account has been created on {settings.APP_NAME}. You can now access all features and collaborate with your team.</p>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 25px 0;">
                    <h3 style="margin-top: 0; color: #333;">Your Login Credentials</h3>
                    <p style="margin: 10px 0;"><strong>Email:</strong> {to_email}</p>
                    <p style="margin: 10px 0;"><strong>Temporary Password:</strong> <code style="background-color: #e5e7eb; padding: 4px 8px; border-radius: 3px; font-size: 14px;">{temp_password}</code></p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background-color: #4f46e5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Log In Now</a>
                </div>

                <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400e;"><strong>⚠️ Security Notice:</strong> Please change your password immediately after your first login for security reasons.</p>
                </div>

                <p style="margin-bottom: 0;">
                    If you have any questions, please don't hesitate to reach out to your administrator.
                </p>

                <p style="margin-bottom: 0;">
                    Best regards,<br>
                    <strong>{settings.APP_NAME} Team</strong>
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                <p>This is an automated notification from {settings.APP_NAME}.</p>
                <p>© 2026 {settings.APP_NAME}. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return html
