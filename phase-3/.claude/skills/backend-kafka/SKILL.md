---
name: backend-kafka
description: Kafka event streaming with aiokafka for producers and consumers. Use when implementing event-driven architecture, message queues, or async processing.
argument-hint: "[producer|consumer]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Kafka Event Streaming

Implement Kafka producers and consumers using aiokafka.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   Kafka     │────▶│  Consumers  │
│  (Producer) │     │   Broker    │     │  (Workers)  │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                    Topics:
                    - task-events
                    - task-updates
                    - notification.request
```

## Configuration

```python
# app/config.py
class Settings(BaseSettings):
    # Kafka connection
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""

    # Topics
    kafka_topic_task_events: str = "task-events"
    kafka_topic_task_updates: str = "task-updates"
    kafka_topic_notification_request: str = "notification.request"

    # Consumer groups
    kafka_consumer_group_audit: str = "audit-service"
    kafka_consumer_group_websocket: str = "websocket-service"
    kafka_consumer_group_notification: str = "notification-service"

    # Feature flag
    kafka_enabled: bool = True
```

## Producer Service

```python
# app/services/kafka_producer.py
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Any
from aiokafka import AIOKafkaProducer

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_producer: Optional[AIOKafkaProducer] = None


async def get_producer() -> AIOKafkaProducer:
    """Get or create Kafka producer."""
    global _producer

    if _producer is None:
        config = {
            "bootstrap_servers": settings.kafka_bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v, default=str).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
        }

        # Add SASL config if enabled
        if settings.kafka_sasl_mechanism:
            config.update({
                "security_protocol": settings.kafka_security_protocol,
                "sasl_mechanism": settings.kafka_sasl_mechanism,
                "sasl_plain_username": settings.kafka_sasl_username,
                "sasl_plain_password": settings.kafka_sasl_password,
            })

        _producer = AIOKafkaProducer(**config)
        await _producer.start()
        logger.info("Kafka producer started")

    return _producer


async def stop_producer() -> None:
    """Stop Kafka producer gracefully."""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_event(
    topic: str,
    event: dict,
    key: Optional[str] = None
) -> bool:
    """
    Publish event to Kafka topic.

    Args:
        topic: Kafka topic name
        event: Event data (will be JSON serialized)
        key: Optional partition key (usually user_id)

    Returns:
        True if published successfully, False if Kafka disabled
    """
    if not settings.kafka_enabled:
        logger.debug(f"Kafka disabled, skipping publish to {topic}")
        return False

    try:
        producer = await get_producer()
        await producer.send_and_wait(topic, value=event, key=key)
        logger.debug(f"Published to {topic}: {event.get('type', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to {topic}: {e}")
        return False
```

## Event Schemas

```python
# app/schemas/events.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from uuid import UUID


class BaseEvent(BaseModel):
    type: str
    timestamp: datetime
    user_id: str


class TaskEvent(BaseEvent):
    """Event for task changes (audit trail)."""
    task_id: UUID
    task_data: dict
    action: str  # "created", "updated", "deleted", "completed"


class TaskUpdateEvent(BaseEvent):
    """Event for real-time task updates (WebSocket sync)."""
    task_id: UUID
    changes: dict


class NotificationRequestEvent(BaseModel):
    """Request to create and send a notification."""
    user_id: str
    task_id: Optional[UUID] = None
    type: str  # "deadline_reminder", "task_overdue", etc.
    title: str
    message: str
    channels: list[str] = ["in_app"]  # "in_app", "email", "sms"
```

## Publishing Events

```python
# In route handlers
from app.services.kafka_producer import publish_event
from app.config import get_settings

settings = get_settings()


@router.post("/tasks")
async def create_task(
    data: TaskCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    task = Task(user_id=current_user.id, **data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Publish event to Kafka
    await publish_event(
        topic=settings.kafka_topic_task_events,
        event={
            "type": "task_created",
            "task_id": str(task.id),
            "task_data": task.model_dump(),
            "user_id": current_user.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        key=current_user.id  # Partition by user
    )

    return task
```

## Consumer Service

```python
# app/services/notification_consumer.py
import json
import logging
import asyncio
from typing import Optional
from aiokafka import AIOKafkaConsumer

from app.config import get_settings
from app.database import async_session_factory
from app.models.notification import Notification
from app.services.email_service import send_email

logger = logging.getLogger(__name__)
settings = get_settings()

_consumer: Optional[AIOKafkaConsumer] = None
_task: Optional[asyncio.Task] = None


async def start_consumer() -> None:
    """Start Kafka consumer."""
    global _consumer, _task

    if not settings.kafka_enabled:
        logger.info("Kafka disabled, skipping consumer")
        return

    config = {
        "bootstrap_servers": settings.kafka_bootstrap_servers,
        "group_id": settings.kafka_consumer_group_notification,
        "value_deserializer": lambda v: json.loads(v.decode("utf-8")),
        "auto_offset_reset": "earliest",
    }

    if settings.kafka_sasl_mechanism:
        config.update({
            "security_protocol": settings.kafka_security_protocol,
            "sasl_mechanism": settings.kafka_sasl_mechanism,
            "sasl_plain_username": settings.kafka_sasl_username,
            "sasl_plain_password": settings.kafka_sasl_password,
        })

    _consumer = AIOKafkaConsumer(
        settings.kafka_topic_notification_request,
        **config
    )
    await _consumer.start()
    _task = asyncio.create_task(_consume_loop())
    logger.info("Notification consumer started")


async def stop_consumer() -> None:
    """Stop Kafka consumer gracefully."""
    global _consumer, _task

    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None

    if _consumer:
        await _consumer.stop()
        _consumer = None

    logger.info("Notification consumer stopped")


async def _consume_loop() -> None:
    """Main consumer loop."""
    try:
        async for message in _consumer:
            try:
                await _process_message(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    except asyncio.CancelledError:
        logger.info("Consumer loop cancelled")
        raise


async def _process_message(data: dict) -> None:
    """Process a notification request message."""
    logger.info(f"Processing notification: {data.get('type')}")

    async with async_session_factory() as session:
        # Create notification in database
        notification = Notification(
            user_id=data["user_id"],
            task_id=data.get("task_id"),
            type=data["type"],
            title=data["title"],
            message=data["message"],
            status="pending"
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        # Send via requested channels
        channels = data.get("channels", ["in_app"])

        if "email" in channels and settings.email_notifications_enabled:
            try:
                await send_email(
                    to=data.get("email"),
                    subject=data["title"],
                    body=data["message"]
                )
                notification.status = "sent"
            except Exception as e:
                logger.error(f"Email send failed: {e}")

        await session.commit()
        logger.info(f"Created notification {notification.id}")
```

## Multiple Consumers

```python
# app/services/consumers/__init__.py
from .notification_consumer import start as start_notification
from .audit_consumer import start as start_audit
from .websocket_consumer import start as start_websocket


async def start_all_consumers():
    await start_notification()
    await start_audit()
    await start_websocket()


async def stop_all_consumers():
    # Stop in reverse order
    await stop_websocket()
    await stop_audit()
    await stop_notification()
```

## Testing Kafka

```python
# tests/test_kafka.py
import pytest
from unittest.mock import AsyncMock, patch

from app.services.kafka_producer import publish_event


@pytest.fixture
def mock_producer():
    with patch("app.services.kafka_producer.get_producer") as mock:
        producer = AsyncMock()
        mock.return_value = producer
        yield producer


async def test_publish_event(mock_producer):
    await publish_event(
        topic="test-topic",
        event={"type": "test", "data": "value"},
        key="user-123"
    )

    mock_producer.send_and_wait.assert_called_once()


async def test_publish_disabled():
    with patch("app.services.kafka_producer.settings") as mock_settings:
        mock_settings.kafka_enabled = False

        result = await publish_event("topic", {"data": "test"})
        assert result is False
```

## Environment Variables

```env
# Kafka connection
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# For Confluent Cloud or secured clusters
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your-api-key
KAFKA_SASL_PASSWORD=your-api-secret

# Topics
KAFKA_TOPIC_TASK_EVENTS=task-events
KAFKA_TOPIC_TASK_UPDATES=task-updates
KAFKA_TOPIC_NOTIFICATION_REQUEST=notification.request

# Consumer groups
KAFKA_CONSUMER_GROUP_NOTIFICATION=notification-service

# Feature flag
KAFKA_ENABLED=true
```

## Best Practices

1. **Use partition keys**: Route by `user_id` for ordering
2. **Idempotent consumers**: Handle duplicate messages
3. **Error handling**: Don't crash on bad messages
4. **Graceful shutdown**: Stop consumers before app exit
5. **Feature flag**: Allow disabling Kafka for local dev
6. **JSON serialization**: Use `default=str` for dates/UUIDs
