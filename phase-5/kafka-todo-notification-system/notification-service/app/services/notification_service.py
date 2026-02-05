import logging
from typing import List
from datetime import datetime

from shared.schemas.events import NotificationRequestEvent
from .retry_manager import retry_manager, RetryStatus
from .dead_letter_queue import dead_letter_queue

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service class for handling notification operations.
    """

    def __init__(self):
        """Initialize the notification service."""
        pass

    async def send_notification(self, event: NotificationRequestEvent, attempt_number: int = 1) -> bool:
        """
        Send a notification based on the event.

        Args:
            event: The notification request event
            attempt_number: The current attempt number (for retries)

        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            success = True
            failed_channels = []

            # Send notification through each specified channel
            for channel in event.channels:
                channel_success = await self._send_via_channel(event, channel)
                if not channel_success:
                    success = False
                    failed_channels.append(channel)
                    logger.warning(f"Failed to send notification via {channel} for event {event.notification_id}")

            if not success:
                # Some channels failed, decide whether to retry or move to DLQ
                await self._handle_partial_failure(event, failed_channels, attempt_number)

            return success

        except Exception as e:
            logger.error(f"Error sending notification for event {event.notification_id}: {str(e)}")

            # Handle exception by attempting retry
            await self._handle_exception_failure(event, str(e), attempt_number)
            return False

    async def _send_via_channel(self, event: NotificationRequestEvent, channel: str) -> bool:
        """
        Send notification via a specific channel.

        Args:
            event: The notification request event
            channel: The channel to send via ('email', 'sms', 'push')

        Returns:
            True if successful, False otherwise
        """
        if channel == "email":
            from ..providers.email import send_email_notification
            return await send_email_notification(event)
        elif channel == "sms":
            from ..providers.sms import send_sms_notification
            return await send_sms_notification(event)
        elif channel == "push":
            from ..providers.push import send_push_notification
            return await send_push_notification(event)
        else:
            logger.error(f"Unknown notification channel: {channel}")
            return False

    async def _handle_partial_failure(
        self,
        event: NotificationRequestEvent,
        failed_channels: List[str],
        attempt_number: int
    ):
        """
        Handle partial failures where some channels succeeded but others failed.

        Args:
            event: The notification request event
            failed_channels: List of channels that failed
            attempt_number: Current attempt number
        """
        logger.warning(f"Partial failure for notification {event.notification_id}, failed channels: {failed_channels}")

        # Check if we should retry
        if retry_manager.should_retry(attempt_number):
            # Schedule a retry
            error_msg = f"Failed channels: {', '.join(failed_channels)}"
            await retry_manager.schedule_retry(
                event.notification_id,
                event,
                attempt_number + 1,
                error_msg
            )
        else:
            # Max retries reached, move to dead letter queue
            await dead_letter_queue.add_failed_notification(
                event.notification_id,
                event,
                f"Max retries reached. Failed channels: {', '.join(failed_channels)}",
                retry_manager.max_retries
            )

    async def _handle_exception_failure(
        self,
        event: NotificationRequestEvent,
        error_message: str,
        attempt_number: int
    ):
        """
        Handle failures due to exceptions.

        Args:
            event: The notification request event
            error_message: The error message
            attempt_number: Current attempt number
        """
        logger.error(f"Exception failure for notification {event.notification_id}: {error_message}")

        # Check if we should retry
        if retry_manager.should_retry(attempt_number):
            # Schedule a retry
            await retry_manager.schedule_retry(
                event.notification_id,
                event,
                attempt_number + 1,
                error_message
            )
        else:
            # Max retries reached, move to dead letter queue
            await dead_letter_queue.add_failed_notification(
                event.notification_id,
                event,
                error_message,
                retry_manager.max_retries
            )

    async def update_notification_status(self, notification_id: str, status: str, sent_at: datetime = None):
        """
        Update the status of a notification in the database.

        Args:
            notification_id: ID of the notification
            status: New status ('sent', 'failed', etc.)
            sent_at: Time when notification was sent (optional)
        """
        # In a real implementation, this would update the notification request in the database
        logger.info(f"Updating notification {notification_id} status to {status}")