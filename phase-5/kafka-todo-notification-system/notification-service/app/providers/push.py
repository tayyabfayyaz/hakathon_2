import logging
import firebase_admin
from firebase_admin import messaging
from typing import Optional

from shared.schemas.events import NotificationRequestEvent

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
try:
    firebase_admin.get_app()
except ValueError:
    # Initialize with default credentials if available
    try:
        firebase_admin.initialize_app()
    except:
        logger.warning("Firebase not initialized. Push notifications will be skipped.")


async def send_push_notification(event: NotificationRequestEvent) -> bool:
    """
    Send a push notification.

    Args:
        event: The notification request event containing details

    Returns:
        True if the push notification was sent successfully, False otherwise
    """
    try:
        # In a real system, get user's device token from user service
        device_token = "device_token_placeholder"  # Placeholder

        # Create a message
        message = messaging.Message(
            notification=messaging.Notification(
                title=f"Todo Reminder: {event.title}",
                body=event.message,
            ),
            token=device_token,
        )

        # Send the message
        response = messaging.send(message)

        logger.info(f"Push notification sent successfully for event {event.notification_id}. Response: {response}")
        return True

    except Exception as e:
        logger.error(f"Failed to send push notification for event {event.notification_id}: {str(e)}")
        return False