"""Email service for sending notification emails via SMTP."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP-based email service for sending notifications."""

    def __init__(self):
        self.settings = get_settings()

    def _create_message(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> MIMEMultipart:
        """Create an email message with both text and optional HTML parts."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.settings.smtp_sender_email
        message["To"] = to_email

        # Add plain text part
        text_part = MIMEText(body_text, "plain")
        message.attach(text_part)

        # Add HTML part if provided
        if body_html:
            html_part = MIMEText(body_html, "html")
            message.attach(html_part)

        return message

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> bool:
        """Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.settings.email_notifications_enabled:
            logger.debug("Email notifications disabled, skipping email send")
            return False

        if not self.settings.smtp_sender_email or not self.settings.smtp_sender_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            return False

        try:
            message = self._create_message(to_email, subject, body_text, body_html)

            with smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port) as server:
                if self.settings.smtp_use_tls:
                    server.starttls()
                server.login(
                    self.settings.smtp_sender_email,
                    self.settings.smtp_sender_password,
                )
                server.sendmail(
                    self.settings.smtp_sender_email,
                    to_email,
                    message.as_string(),
                )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_notification_email(
        self,
        to_email: str,
        title: str,
        message: str,
        task_text: Optional[str] = None,
    ) -> bool:
        """Send a notification email.

        Args:
            to_email: Recipient email address
            title: Notification title (used as subject)
            message: Notification message body
            task_text: Optional task text for context

        Returns:
            True if email was sent successfully
        """
        subject = f"Todo Reminder: {title}"

        # Plain text body
        body_text = f"{title}\n\n{message}"
        if task_text:
            body_text += f"\n\nTask: {task_text}"

        # HTML body
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333; margin-bottom: 16px;">{title}</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5;">{message}</p>
                {f'<div style="margin-top: 16px; padding: 12px; background-color: #fff; border-left: 4px solid #4f46e5; border-radius: 4px;"><strong>Task:</strong> {task_text}</div>' if task_text else ''}
            </div>
            <p style="color: #999; font-size: 12px; margin-top: 20px; text-align: center;">
                This is an automated reminder from your Todo app.
            </p>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body_text, body_html)


# Global service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the global email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
