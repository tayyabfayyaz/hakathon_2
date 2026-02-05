"""Async Kafka producer singleton for publishing events."""

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

# Global producer instance
_producer: Optional["KafkaProducer"] = None


class KafkaProducer:
    """Async Kafka producer wrapper."""

    def __init__(self):
        self._producer = None
        self._started = False
        self.settings = get_settings()

    async def start(self) -> None:
        """Start the Kafka producer."""
        if not self.settings.kafka_enabled:
            logger.info("Kafka is disabled, skipping producer initialization")
            return

        try:
            from aiokafka import AIOKafkaProducer

            kafka_config = self.settings.kafka_config
            self._producer = AIOKafkaProducer(
                **kafka_config,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            self._started = True
            logger.info(
                f"Kafka producer started, connected to {self.settings.kafka_bootstrap_servers}"
            )
        except ImportError:
            logger.warning("aiokafka not installed, Kafka producer disabled")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self._started = False

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer and self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")

    async def send(
        self,
        topic: str,
        value: dict[str, Any] | BaseModel,
        key: Optional[str] = None,
    ) -> bool:
        """
        Send a message to a Kafka topic.

        Args:
            topic: The Kafka topic to send to
            value: The message value (dict or Pydantic model)
            key: Optional message key for partitioning

        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self._started or not self._producer:
            logger.debug(f"Kafka producer not started, skipping message to {topic}")
            return False

        try:
            # Convert Pydantic model to dict if needed
            if isinstance(value, BaseModel):
                value = value.model_dump(mode="json")

            await self._producer.send_and_wait(topic, value=value, key=key)
            logger.debug(f"Message sent to topic '{topic}' with key '{key}'")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {topic}: {e}")
            return False

    async def send_task_event(
        self,
        event: "TaskEvent",
    ) -> bool:
        """Send a task event to the task-events topic."""
        from app.schemas.events import TaskEvent

        return await self.send(
            topic=self.settings.kafka_topic_task_events,
            value=event,
            key=event.user_id,
        )

    async def send_task_update_event(
        self,
        event: "TaskUpdateEvent",
    ) -> bool:
        """Send a task update event for real-time WebSocket sync."""
        from app.schemas.events import TaskUpdateEvent

        return await self.send(
            topic=self.settings.kafka_topic_task_updates,
            value=event,
            key=event.user_id,
        )

    @property
    def is_ready(self) -> bool:
        """Check if producer is ready to send messages."""
        return self._started and self._producer is not None


async def get_producer() -> KafkaProducer:
    """Get the global Kafka producer instance."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer()
    return _producer


async def start_producer() -> KafkaProducer:
    """Start and return the global Kafka producer."""
    producer = await get_producer()
    await producer.start()
    return producer


async def stop_producer() -> None:
    """Stop the global Kafka producer."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
