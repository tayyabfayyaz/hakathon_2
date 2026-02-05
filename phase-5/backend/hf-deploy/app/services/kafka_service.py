"""Kafka service for publishing todo events to the notification system."""
import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from kafka import KafkaProducer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TodoCreatedEvent(BaseModel):
    """Schema for todo created events published to Kafka"""
    todo_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "normal"
    created_at: datetime


class TodoUpdatedEvent(BaseModel):
    """Schema for todo updated events published to Kafka"""
    todo_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "normal"
    updated_at: datetime


class TodoDeletedEvent(BaseModel):
    """Schema for todo deleted events published to Kafka"""
    todo_id: str
    user_id: str
    deleted_at: datetime


class KafkaService:
    """Service class to handle Kafka communication for the notification system."""

    def __init__(self):
        """
        Initialize the Kafka service using configuration.
        """
        from app.config import get_settings
        settings = get_settings()

        self.bootstrap_servers = settings.kafka_bootstrap_servers
        self.enabled = settings.kafka_enabled
        self._producer: Optional[KafkaProducer] = None
        self._connected = False

    def connect(self):
        """Connect to Kafka broker."""
        if not self.enabled:
            logger.info("Kafka service is disabled by configuration")
            return

        try:
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                linger_ms=5,  # Small delay to batch requests
                buffer_memory=33554432,  # 32MB buffer
            )
            self._connected = True
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self._connected = False
            raise

    def disconnect(self):
        """Disconnect from Kafka broker."""
        if self._producer:
            self._producer.close()
            self._connected = False
            logger.info("Disconnected from Kafka")

    @property
    def producer(self) -> KafkaProducer:
        """Get the Kafka producer, connecting if necessary."""
        if not self.enabled:
            raise RuntimeError("Kafka service is disabled")

        if not self._connected:
            self.connect()
        if not self._producer:
            raise RuntimeError("Kafka producer not initialized")
        return self._producer

    def publish_todo_created(self, todo_id: str, user_id: str, title: str,
                           description: Optional[str] = None,
                           deadline: Optional[datetime] = None):
        """
        Publish a todo created event to Kafka.

        Args:
            todo_id: Unique identifier of the todo
            user_id: User identifier
            title: Title of the todo
            description: Description of the todo
            deadline: Deadline for the todo
        """
        if not self.enabled:
            logger.debug("Kafka service disabled, skipping event publication")
            return

        if not self._connected:
            logger.warning("Kafka not connected, skipping event publication")
            return

        try:
            event = TodoCreatedEvent(
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                description=description,
                deadline=deadline,
                priority="normal",
                created_at=datetime.utcnow()
            )

            self.producer.send(
                topic='todo.created',
                key=user_id,
                value=event.model_dump()
            )
            # Flush to ensure the message is sent
            self.producer.flush(timeout=10)

            logger.info(f"Published todo.created event for todo {todo_id}")
        except Exception as e:
            logger.error(f"Failed to publish todo.created event: {e}")

    def publish_todo_updated(self, todo_id: str, user_id: str, title: str,
                           description: Optional[str] = None,
                           deadline: Optional[datetime] = None):
        """
        Publish a todo updated event to Kafka.

        Args:
            todo_id: Unique identifier of the todo
            user_id: User identifier
            title: Title of the todo
            description: Description of the todo
            deadline: Deadline for the todo
        """
        if not self.enabled:
            logger.debug("Kafka service disabled, skipping event publication")
            return

        if not self._connected:
            logger.warning("Kafka not connected, skipping event publication")
            return

        try:
            event = TodoUpdatedEvent(
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                description=description,
                deadline=deadline,
                priority="normal",
                updated_at=datetime.utcnow()
            )

            self.producer.send(
                topic='todo.updated',
                key=user_id,
                value=event.model_dump()
            )
            # Flush to ensure the message is sent
            self.producer.flush(timeout=10)

            logger.info(f"Published todo.updated event for todo {todo_id}")
        except Exception as e:
            logger.error(f"Failed to publish todo.updated event: {e}")

    def publish_todo_deleted(self, todo_id: str, user_id: str):
        """
        Publish a todo deleted event to Kafka.

        Args:
            todo_id: Unique identifier of the todo
            user_id: User identifier
        """
        if not self.enabled:
            logger.debug("Kafka service disabled, skipping event publication")
            return

        if not self._connected:
            logger.warning("Kafka not connected, skipping event publication")
            return

        try:
            event = TodoDeletedEvent(
                todo_id=todo_id,
                user_id=user_id,
                deleted_at=datetime.utcnow()
            )

            self.producer.send(
                topic='todo.deleted',
                key=user_id,
                value=event.model_dump()
            )
            # Flush to ensure the message is sent
            self.producer.flush(timeout=10)

            logger.info(f"Published todo.deleted event for todo {todo_id}")
        except Exception as e:
            logger.error(f"Failed to publish todo.deleted event: {e}")


# Global Kafka service instance
kafka_service = KafkaService()