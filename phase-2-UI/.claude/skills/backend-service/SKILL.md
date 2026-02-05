---
name: backend-service
description: Create service layer components for business logic, background tasks, and external integrations. Use when implementing schedulers, producers, consumers, or complex business logic.
argument-hint: "[service-name]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Service Layer Architecture

Create services following the TodoList Pro patterns for business logic separation.

## Service Structure

```
backend/app/services/
├── agent.py              # AI agent with MCP tools
├── kafka_producer.py     # Async Kafka producer
├── notification_consumer.py  # Kafka notification consumer
├── deadline_scheduler.py # Background deadline monitor
├── email_service.py      # SMTP email sending
└── mcp_client.py         # MCP client wrapper
```

## Service Template

```python
# app/services/{service_name}.py
import asyncio
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class {Service}Service:
    """
    {Description of service purpose}
    """

    _instance: Optional["{Service}Service"] = None
    _started: bool = False

    def __init__(self):
        self._client = None
        self._task: Optional[asyncio.Task] = None

    @classmethod
    def get_instance(cls) -> "{Service}Service":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self) -> None:
        """Start the service."""
        if self._started:
            logger.warning("{Service} already started")
            return

        logger.info("Starting {Service}...")
        # Initialize resources
        self._started = True
        logger.info("{Service} started successfully")

    async def stop(self) -> None:
        """Stop the service gracefully."""
        if not self._started:
            return

        logger.info("Stopping {Service}...")
        # Cleanup resources
        self._started = False
        logger.info("{Service} stopped")

    async def process(self, data: dict) -> dict:
        """Process data."""
        if not self._started:
            raise RuntimeError("{Service} not started")

        # Business logic here
        return {"status": "success"}


# Module-level functions for easy access
_service: Optional[{Service}Service] = None


def get_{service}() -> {Service}Service:
    global _service
    if _service is None:
        _service = {Service}Service()
    return _service


async def start_{service}() -> None:
    service = get_{service}()
    await service.start()


async def stop_{service}() -> None:
    global _service
    if _service:
        await _service.stop()
        _service = None
```

## Background Task Service

```python
# app/services/deadline_scheduler.py
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import async_session_factory
from app.models.task import Task
from app.models.notification import Notification

logger = logging.getLogger(__name__)

REMINDER_THRESHOLD = timedelta(minutes=30)
CHECK_INTERVAL = 60  # seconds


class DeadlineScheduler:
    """Background service that monitors task deadlines."""

    _instance: Optional["DeadlineScheduler"] = None

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False

    @classmethod
    def get_instance(cls) -> "DeadlineScheduler":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def start(self) -> None:
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Deadline scheduler started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Deadline scheduler stopped")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self._check_deadlines()
            except Exception as e:
                logger.error(f"Error checking deadlines: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

    async def _check_deadlines(self) -> None:
        now = datetime.now(timezone.utc)

        async with async_session_factory() as session:
            # Find tasks with upcoming/passed deadlines
            result = await session.exec(
                select(Task)
                .where(Task.deadline.isnot(None))
                .where(Task.completed == False)
                .where(Task.deadline <= now + REMINDER_THRESHOLD)
            )
            tasks = result.all()

            for task in tasks:
                await self._process_deadline(session, task, now)

            await session.commit()

    async def _process_deadline(
        self,
        session: AsyncSession,
        task: Task,
        now: datetime
    ) -> None:
        # Determine notification type
        if task.deadline <= now - timedelta(hours=1):
            notification_type = "task_overdue"
        elif task.deadline <= now:
            notification_type = "deadline_reached"
        else:
            notification_type = "deadline_reminder"

        # Check for recent duplicate
        existing = await self._has_recent_notification(
            session, task.id, notification_type
        )
        if existing:
            return

        # Create notification
        notification = Notification(
            user_id=task.user_id,
            task_id=task.id,
            type=notification_type,
            title=self._get_title(notification_type),
            message=f"Task: {task.text}",
            status="pending"
        )
        session.add(notification)
        logger.info(f"Created {notification_type} for task {task.id}")
```

## Kafka Producer Service

```python
# app/services/kafka_producer.py
import json
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_producer: Optional[AIOKafkaProducer] = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await _producer.start()
        logger.info("Kafka producer started")
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_event(
    topic: str,
    event: dict,
    key: Optional[str] = None
) -> None:
    """Publish event to Kafka topic."""
    if not settings.kafka_enabled:
        logger.debug(f"Kafka disabled, skipping: {topic}")
        return

    producer = await get_producer()
    await producer.send_and_wait(topic, value=event, key=key)
    logger.debug(f"Published to {topic}: {event}")


# Convenience functions
async def publish_task_event(event_type: str, task: dict, user_id: str) -> None:
    await publish_event(
        topic=settings.kafka_topic_task_events,
        event={
            "type": event_type,
            "task": task,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        key=user_id
    )
```

## Kafka Consumer Service

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

logger = logging.getLogger(__name__)
settings = get_settings()

_consumer: Optional[AIOKafkaConsumer] = None
_task: Optional[asyncio.Task] = None


async def start_consumer() -> None:
    global _consumer, _task

    if not settings.kafka_enabled:
        logger.info("Kafka disabled, skipping consumer")
        return

    _consumer = AIOKafkaConsumer(
        settings.kafka_topic_notification_request,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group_notification,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await _consumer.start()
    _task = asyncio.create_task(_consume_loop())
    logger.info("Notification consumer started")


async def stop_consumer() -> None:
    global _consumer, _task

    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass

    if _consumer:
        await _consumer.stop()
        _consumer = None

    logger.info("Notification consumer stopped")


async def _consume_loop() -> None:
    async for message in _consumer:
        try:
            await _process_message(message.value)
        except Exception as e:
            logger.error(f"Error processing message: {e}")


async def _process_message(data: dict) -> None:
    async with async_session_factory() as session:
        notification = Notification(
            user_id=data["user_id"],
            task_id=data.get("task_id"),
            type=data["type"],
            title=data["title"],
            message=data["message"],
        )
        session.add(notification)
        await session.commit()
        logger.info(f"Created notification for user {data['user_id']}")
```

## Application Lifespan

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db, close_db
from app.services.kafka_producer import start_producer, stop_producer
from app.services.notification_consumer import start_consumer, stop_consumer
from app.services.deadline_scheduler import DeadlineScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    if settings.kafka_enabled:
        await start_producer()
        await start_consumer()

    scheduler = DeadlineScheduler.get_instance()
    await scheduler.start()

    yield

    # Shutdown (reverse order)
    await scheduler.stop()

    if settings.kafka_enabled:
        await stop_consumer()
        await stop_producer()

    await close_db()


app = FastAPI(lifespan=lifespan)
```

## Best Practices

1. **Singleton pattern**: Use `_instance` for stateful services
2. **Graceful shutdown**: Always implement `stop()` methods
3. **Error handling**: Catch and log errors in background loops
4. **Configurability**: Use settings for intervals, thresholds
5. **Async-first**: All I/O operations should be async
6. **Logging**: Log lifecycle events and errors
