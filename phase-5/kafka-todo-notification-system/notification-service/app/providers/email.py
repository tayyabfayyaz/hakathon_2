import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Optional

from shared.schemas.events import NotificationRequestEvent

logger = logging.getLogger(__name__)


async def send_email_notification(event: NotificationRequestEvent) -> bool:
    """
    Send an email notification.

    Args:
        event: The notification request event containing details

    Returns:
        True if the email was sent successfully, False otherwise
    """
    try:
        # Get SMTP configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "noreply@example.com")
        sender_password = os.getenv("SENDER_PASSWORD", "")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = f"user_{event.user_id}@example.com"  # In a real system, get actual email from user service
        msg['Subject'] = f"Todo Reminder: {event.title}"

        # Add body to email
        body = f"""
        Hello,

        This is a reminder about your todo: {event.title}

        {event.message}

        Thank you!
        Todo Notification System
        """

        msg.attach(MIMEText(body, 'plain'))

        # Connect to server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable encryption
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, f"user_{event.user_id}@example.com", text)

        logger.info(f"Email notification sent successfully for event {event.notification_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email notification for event {event.notification_id}: {str(e)}")
        return False


def validate_email_address(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None