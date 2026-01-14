"""Pydantic schemas for request/response validation."""

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse,
    TaskListResponse,
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

__all__ = [
    "TaskCreate",
    "TaskUpdate",
    "TaskPatch",
    "TaskResponse",
    "TaskListResponse",
    "ErrorResponse",
    "HealthResponse",
    "ChatRequest",
    "ChatResponse",
    "ToolCallResult",
    "HistoryMessage",
    "ChatHistoryResponse",
    "ChatErrorResponse",
]
