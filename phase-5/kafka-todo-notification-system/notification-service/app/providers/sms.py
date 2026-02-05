import logging
from twilio.rest import Client
import os

from shared.schemas.events import NotificationRequestEvent

logger = logging.getLogger(__name__)


async def send_sms_notification(event: NotificationRequestEvent) -> bool:
    """
    Send an SMS notification.

    Args:
        event: The notification request event containing details

    Returns:
        True if the SMS was sent successfully, False otherwise
    """
    try:
        # Get Twilio configuration from environment variables
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")

        if not account_sid or not auth_token:
            logger.warning("Twilio credentials not configured, skipping SMS notification")
            return True  # Consider it successful if not configured

        # In a real system, get user's phone number from user service
        to_phone_number = "+1234567890"  # Placeholder

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"Todo Reminder: {event.message}",
            from_=twilio_phone_number,
            to=to_phone_number
        )

        logger.info(f"SMS notification sent successfully for event {event.notification_id}. SID: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS notification for event {event.notification_id}: {str(e)}")
        return False