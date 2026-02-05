import asyncio
import logging
from typing import Optional
import json
from kafka import KafkaConsumer

from shared.kafka_config.config import KafkaConfig
from shared.schemas.events import NotificationRequestEvent, NotificationSentEvent, NotificationFailedEvent
from shared.utils import validate_email, is_in_do_not_disturb
from .providers.email import send_email_notification
from .providers.sms import send_sms_notification
from .providers.push import send_push_notification
from .services.retry_manager import retry_manager
from .services.dead_letter_queue import dead_letter_queue


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.consumer = None
        self.running = False

    async def start(self):
        """Start the notification service."""
        logger.info("Starting Notification Service...")

        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            KafkaConfig.TOPIC_NOTIFICATION_REQUEST,
            bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
            group_id=KafkaConfig.CONSUMER_GROUP_NOTIFICATION,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )

        self.running = True

        # Schedule periodic retry processing (every 2 minutes)
        import threading
        self.retry_thread = threading.Thread(target=self._start_retry_processing, daemon=True)
        self.retry_thread.start()

        # Start consuming messages
        await self.consume_messages()

    async def consume_messages(self):
        """Consume Kafka messages and process them."""
        logger.info("Notification service started consuming messages")

        try:
            for message in self.consumer:
                if not self.running:
                    break

                topic = message.topic
                event_data = message.value

                try:
                    if topic == KafkaConfig.TOPIC_NOTIFICATION_REQUEST:
                        await self.handle_notification_request(event_data)

                    # Commit the offset after successful processing
                    self.consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {str(e)}")
                    # In a production system, you might want to send to a dead letter topic
                    self.consumer.commit()  # Still commit to avoid getting stuck

        except Exception as e:
            logger.error(f"Error in message consumption loop: {str(e)}")

    async def handle_notification_request(self, event_data):
        """Handle notification request event."""
        try:
            event = NotificationRequestEvent(**event_data)
            logger.info(f"Handling notification request: {event.notification_id}")

            success = True
            error_message = ""

            try:
                # Get user's preferred channels if not provided in event
                channels_to_use = event.channels
                if not channels_to_use:
                    from .services.channel_selector import get_user_notification_channels
                    channels_to_use = get_user_notification_channels(event.user_id)

                # Check if user is in do-not-disturb window
                from .services.channel_selector import is_in_do_not_disturb_window
                if is_in_do_not_disturb_window(event.user_id):
                    logger.info(f"User {event.user_id} is in do-not-disturb window, skipping notification")
                    # Still mark as successful since it's intentional
                    await self.update_notification_status(event.notification_id, "sent")
                    return

                # Send notification based on channels specified
                for channel in channels_to_use:
                    if channel == "email":
                        channel_success = await send_email_notification(event)
                        if not channel_success:
                            success = False
                    elif channel == "sms":
                        channel_success = await send_sms_notification(event)
                        if not channel_success:
                            success = False
                    elif channel == "push":
                        channel_success = await send_push_notification(event)
                        if not channel_success:
                            success = False
                    else:
                        logger.warning(f"Unknown notification channel: {channel}")

                # Update notification status in the database if needed
                await self.update_notification_status(event.notification_id, "sent" if success else "failed")

            except Exception as e:
                success = False
                error_message = str(e)
                logger.error(f"Failed to send notification {event.notification_id}: {str(e)}")

            # Publish notification result event to Kafka
            if success:
                await self.publish_notification_sent_event(event)
            else:
                await self.publish_notification_failed_event(event, error_message)

        except Exception as e:
            logger.error(f"Error handling notification request: {str(e)}")

    async def update_notification_status(self, notification_id: str, status: str):
        """
        Update the status of a notification in the database.

        Args:
            notification_id: ID of the notification
            status: New status ('sent', 'failed', etc.)
        """
        # In a real implementation, this would update the notification request in the database
        logger.info(f"Updating notification {notification_id} status to {status}")

    async def publish_notification_sent_event(self, event: NotificationRequestEvent):
        """Publish notification sent event to Kafka."""
        try:
            from shared.kafka.producer import get_kafka_producer
            kafka_producer = get_kafka_producer()

            sent_event = NotificationSentEvent(
                notification_id=event.notification_id,
                todo_id=event.todo_id,
                user_id=event.user_id
            )

            kafka_producer.send_event(
                topic="notification.sent",
                key=event.user_id,
                value=sent_event.dict()
            )

            logger.info(f"Published notification sent event for notification {event.notification_id}")
        except Exception as e:
            logger.error(f"Failed to publish notification sent event: {str(e)}")

    async def publish_notification_failed_event(self, event: NotificationRequestEvent, error_message: str):
        """Publish notification failed event to Kafka."""
        try:
            from shared.kafka.producer import get_kafka_producer
            kafka_producer = get_kafka_producer()

            failed_event = NotificationFailedEvent(
                notification_id=event.notification_id,
                todo_id=event.todo_id,
                user_id=event.user_id,
                error_message=error_message
            )

            kafka_producer.send_event(
                topic="notification.failed",
                key=event.user_id,
                value=failed_event.dict()
            )

            logger.info(f"Published notification failed event for notification {event.notification_id}")
        except Exception as e:
            logger.error(f"Failed to publish notification failed event: {str(e)}")

    def _start_retry_processing(self):
        """Start the retry processing loop in a separate thread."""
        import time
        while self.running:
            try:
                # Process pending retries (using asyncio.run to run async function from sync thread)
                import asyncio
                processed = asyncio.run(self._process_pending_retries())

                # Sleep for 2 minutes before next check
                time.sleep(120)
            except Exception as e:
                logger.error(f"Error in retry processing loop: {str(e)}")
                time.sleep(120)  # Wait before trying again

    async def _process_pending_retries(self):
        """Process pending retries that are due."""
        try:
            processed_ids = await retry_manager.process_pending_retries()
            if processed_ids:
                logger.info(f"Processed {len(processed_ids)} retry attempts")
            return processed_ids
        except Exception as e:
            logger.error(f"Error processing pending retries: {str(e)}")
            return []

    async def stop(self):
        """Stop the notification service."""
        logger.info("Stopping Notification Service...")
        self.running = False

        if self.consumer:
            self.consumer.close()

        logger.info("Notification Service stopped")


async def main():
    """Main function to run the notification service."""
    notification_service = NotificationService()

    try:
        await notification_service.start()
    except KeyboardInterrupt:
        print("Received interrupt signal")
    finally:
        await notification_service.stop()


if __name__ == "__main__":
    asyncio.run(main())