"""Kafka event schemas for the event-driven system."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from uuid6 import uuid7


class EventType(str, Enum):
    """Task event types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"


class EventSource(str, Enum):
    """Source of the event."""
    API = "api"
    CHAT = "chat"
    MCP = "mcp"


class TaskUpdateEventType(str, Enum):
    """WebSocket task update event types."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMPLETED = "task_completed"


class TaskEvent(BaseModel):
    """Event published to task-events topic for audit and recurring tasks."""

    event_id: UUID = Field(default_factory=uuid7)
    event_type: EventType
    task_id: UUID
    task_data: dict[str, Any]
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: EventSource = EventSource.API

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TaskUpdateEvent(BaseModel):
    """Event published to task-updates topic for real-time WebSocket sync."""

    event_type: TaskUpdateEventType
    user_id: str
    task_id: UUID
    task_data: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class WebSocketMessage(BaseModel):
    """Message format sent to WebSocket clients."""

    type: str = "task_update"
    payload: TaskUpdateEvent

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
