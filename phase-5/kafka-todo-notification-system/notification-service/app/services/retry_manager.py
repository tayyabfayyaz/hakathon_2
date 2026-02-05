"""
Retry manager for handling failed notifications with exponential backoff.
Implements task T056: Implement retry mechanism for failed notifications with exponential backoff.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from shared.schemas.events import NotificationRequestEvent
from shared.database.models import NotificationRequest as NotificationRequestDB

logger = logging.getLogger(__name__)


class RetryStatus(Enum):
    PENDING = "pending"
    RETRYING = "retrying"
    FAILED = "failed"
    SUCCESS = "success"


class RetryManager:
    def __init__(self, max_retries: int = 3, base_delay_seconds: int = 60):
        """
        Initialize the retry manager.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay_seconds: Base delay in seconds for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay_seconds = base_delay_seconds
        self.pending_retries: Dict[str, dict] = {}  # notification_id -> retry info

    def calculate_next_retry_time(self, attempt_number: int) -> datetime:
        """
        Calculate the next retry time using exponential backoff.

        Args:
            attempt_number: Current attempt number (starting from 1)

        Returns:
            Next retry time as datetime
        """
        # Exponential backoff: base_delay * (2 ^ (attempt_number - 1))
        delay_seconds = self.base_delay_seconds * (2 ** (attempt_number - 1))
        return datetime.utcnow() + timedelta(seconds=delay_seconds)

    def should_retry(self, attempt_number: int) -> bool:
        """
        Determine if a notification should be retried.

        Args:
            attempt_number: Current attempt number

        Returns:
            True if should retry, False otherwise
        """
        return attempt_number <= self.max_retries

    async def schedule_retry(
        self,
        notification_id: str,
        event: NotificationRequestEvent,
        attempt_number: int,
        error_message: str = ""
    ) -> bool:
        """
        Schedule a retry for a failed notification.

        Args:
            notification_id: ID of the notification to retry
            event: Original notification event
            attempt_number: Current attempt number
            error_message: Error message from previous attempt

        Returns:
            True if retry was scheduled, False if max retries reached
        """
        if not self.should_retry(attempt_number):
            logger.info(f"Max retries reached for notification {notification_id}. Moving to dead letter queue.")
            return False

        next_retry_time = self.calculate_next_retry_time(attempt_number)

        # Store retry information
        self.pending_retries[notification_id] = {
            'event': event,
            'attempt_number': attempt_number,
            'next_retry_time': next_retry_time,
            'error_message': error_message,
            'scheduled_at': datetime.utcnow()
        }

        logger.info(f"Scheduled retry #{attempt_number} for notification {notification_id} at {next_retry_time}")
        return True

    async def process_pending_retries(self) -> List[str]:
        """
        Process all pending retries that are due.

        Returns:
            List of notification IDs that were processed
        """
        processed_ids = []
        current_time = datetime.utcnow()

        # Find all retries that are due
        due_retries = [
            nid for nid, retry_info in self.pending_retries.items()
            if retry_info['next_retry_time'] <= current_time
        ]

        for notification_id in due_retries:
            retry_info = self.pending_retries[notification_id]

            try:
                # Attempt to resend the notification
                success = await self._attempt_resend(retry_info['event'], retry_info['attempt_number'])

                if success:
                    # Remove from pending retries if successful
                    del self.pending_retries[notification_id]
                    processed_ids.append(notification_id)
                    logger.info(f"Successfully resent notification {notification_id} on attempt #{retry_info['attempt_number']}")
                else:
                    # Schedule next retry if max retries not reached
                    new_attempt = retry_info['attempt_number'] + 1
                    if self.should_retry(new_attempt):
                        await self.schedule_retry(
                            notification_id,
                            retry_info['event'],
                            new_attempt,
                            f"Previous attempt failed: {retry_info.get('error_message', 'Unknown error')}"
                        )
                        processed_ids.append(notification_id)
                    else:
                        # Max retries reached, move to dead letter queue
                        del self.pending_retries[notification_id]
                        processed_ids.append(notification_id)
                        logger.info(f"Max retries reached for notification {notification_id}. Moved to dead letter queue.")

            except Exception as e:
                logger.error(f"Error processing retry for notification {notification_id}: {str(e)}")
                processed_ids.append(notification_id)

        return processed_ids

    async def _attempt_resend(self, event: NotificationRequestEvent, attempt_number: int) -> bool:
        """
        Attempt to resend a notification.

        Args:
            event: The notification event to resend
            attempt_number: The attempt number

        Returns:
            True if successful, False otherwise
        """
        # Import the notification service here to avoid circular imports
        from notification_service.app.services.notification_service import NotificationService

        service = NotificationService()
        return await service.send_notification(event)

    def get_retry_status(self, notification_id: str) -> Optional[dict]:
        """
        Get the retry status for a specific notification.

        Args:
            notification_id: ID of the notification

        Returns:
            Retry status information or None if not found
        """
        return self.pending_retries.get(notification_id)


# Global retry manager instance
retry_manager = RetryManager(max_retries=3, base_delay_seconds=60)