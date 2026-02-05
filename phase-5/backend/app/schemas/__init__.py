"""Pydantic schemas for request/response validation."""

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse,
    TaskListResponse,
    DeadlineRequest,
    DeadlineResponse,
)
from app.schemas.error import ErrorResponse
from app.schemas.health import HealthResponse
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ToolCallResult,
    HistoryMessage,
    ChatHistoryResponse,
    ChatErrorResponse,
)
from app.schemas.events import (
    EventType,
    EventSource,
    TaskUpdateEventType,
    TaskEvent,
    TaskUpdateEvent,
    WebSocketMessage,
)

__all__ = [
    "TaskCreate",
    "TaskUpdate",
    "TaskPatch",
    "TaskResponse",
    "TaskListResponse",
    "DeadlineRequest",
    "DeadlineResponse",
    "ErrorResponse",
    "HealthResponse",
    "ChatRequest",
    "ChatResponse",
    "ToolCallResult",
    "HistoryMessage",
    "ChatHistoryResponse",
    "ChatErrorResponse",
    # Event schemas
    "EventType",
    "EventSource",
    "TaskUpdateEventType",
    "TaskEvent",
    "TaskUpdateEvent",
    "WebSocketMessage",
]
