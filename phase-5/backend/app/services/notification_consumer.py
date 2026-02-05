"""Kafka consumer for notification requests."""

import asyncio
import json
import logging
from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import get_settings
from app.database import async_session_factory
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.api.routes.websocket import send_notification_to_user
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

# Global consumer instance
_consumer: Optional["NotificationConsumer"] = None


class NotificationConsumer:
    """Async Kafka consumer for processing notification requests."""

    def __init__(self):
        self._consumer = None
        self._started = False
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.settings = get_settings()

    async def start(self) -> None:
        """Start the Kafka consumer."""
        if not self.settings.kafka_enabled:
            logger.info("Kafka is disabled, skipping notification consumer initialization")
            return

        try:
            from aiokafka import AIOKafkaConsumer

            kafka_config = self.settings.kafka_config
            self._consumer = AIOKafkaConsumer(
                self.settings.kafka_topic_notification_request,
                **kafka_config,
                group_id=self.settings.kafka_consumer_group_notification,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True,
            )
            await self._consumer.start()
            self._started = True
            self._running = True
            logger.info(
                f"Notification consumer started, subscribed to {self.settings.kafka_topic_notification_request}"
            )

            # Start consuming in background
            self._task = asyncio.create_task(self._consume_loop())

        except ImportError:
            logger.warning("aiokafka not installed, notification consumer disabled")
        except Exception as e:
            logger.error(f"Failed to start notification consumer: {e}")
            self._started = False

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._consumer and self._started:
            await self._consumer.stop()
            self._started = False
            logger.info("Notification consumer stopped")

    async def _consume_loop(self) -> None:
        """Main consumption loop."""
        while self._running and self._consumer:
            try:
                async for message in self._consumer:
                    if not self._running:
                        break
                    await self._process_message(message.value)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in notification consumer loop: {e}")
                if self._running:
                    await asyncio.sleep(5)  # Wait before retrying

    async def _process_message(self, data: dict) -> None:
        """Process a notification request message.

        Expected message format:
        {
            "user_id": "string",
            "task_id": "uuid-string" (optional),
            "type": "deadline_reminder|deadline_reached|task_overdue|system",
            "title": "string",
            "message": "string",
            "channels": ["websocket", "email"],
            "user_email": "string" (required if email in channels)
        }
        """
        try:
            user_id = data.get("user_id")
            if not user_id:
                logger.warning("Notification request missing user_id")
                return

            notification_type = data.get("type", "system")
            title = data.get("title", "Notification")
            message = data.get("message", "")
            task_id = data.get("task_id")
            channels = data.get("channels", ["websocket"])
            user_email = data.get("user_email")
            task_text = data.get("task_text")

            # Map string type to enum
            type_mapping = {
                "deadline_reminder": NotificationType.DEADLINE_REMINDER,
                "deadline_reached": NotificationType.DEADLINE_REACHED,
                "task_overdue": NotificationType.TASK_OVERDUE,
                "system": NotificationType.SYSTEM,
            }
            notification_type_enum = type_mapping.get(notification_type, NotificationType.SYSTEM)

            # Create notification in database
            async with async_session_factory() as session:
                notification = Notification(
                    user_id=user_id,
                    task_id=UUID(task_id) if task_id else None,
                    type=notification_type_enum,
                    title=title,
                    message=message,
                    status=NotificationStatus.SENT,
                )
                session.add(notification)
                await session.commit()
                await session.refresh(notification)

                logger.info(f"Created notification {notification.id} for user {user_id}")

                # Send via WebSocket
                if "websocket" in channels:
                    notification_dict = {
                        "id": str(notification.id),
                        "user_id": notification.user_id,
                        "task_id": str(notification.task_id) if notification.task_id else None,
                        "type": notification.type.value,
                        "title": notification.title,
                        "message": notification.message,
                        "status": notification.status.value,
                        "read_at": None,
                        "created_at": notification.created_at.isoformat(),
                    }
                    sent = await send_notification_to_user(user_id, notification_dict)
                    if sent:
                        logger.info(f"Sent notification via WebSocket to user {user_id}")
                    else:
                        logger.debug(f"User {user_id} not connected via WebSocket")

                # Send via email
                if "email" in channels and user_email:
                    email_service = get_email_service()
                    sent = email_service.send_notification_email(
                        to_email=user_email,
                        title=title,
                        message=message,
                        task_text=task_text,
                    )
                    if sent:
                        logger.info(f"Sent notification email to {user_email}")
                    else:
                        logger.debug(f"Email notification not sent (disabled or failed)")

        except Exception as e:
            logger.error(f"Error processing notification request: {e}")

    @property
    def is_ready(self) -> bool:
        """Check if consumer is running."""
        return self._started and self._running


async def get_consumer() -> NotificationConsumer:
    """Get the global notification consumer instance."""
    global _consumer
    if _consumer is None:
        _consumer = NotificationConsumer()
    return _consumer


async def start_consumer() -> NotificationConsumer:
    """Start and return the global notification consumer."""
    consumer = await get_consumer()
    await consumer.start()
    return consumer


async def stop_consumer() -> None:
    """Stop the global notification consumer."""
    global _consumer
    if _consumer:
        await _consumer.stop()
        _consumer = None
