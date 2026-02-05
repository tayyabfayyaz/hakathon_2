"""Chat request/response schemas."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat message request."""

    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User message to send to the AI assistant"
    )


class ToolCallResult(BaseModel):
    """Schema for a single tool call result."""

    tool_name: str = Field(description="Name of the tool that was called")
    result: dict = Field(description="Result returned by the tool")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    message: str = Field(description="AI assistant response message")
    tool_calls: Optional[list[ToolCallResult]] = Field(
        default=None,
        description="List of tool calls made during response generation"
    )


class HistoryMessage(BaseModel):
    """Schema for a single message in history."""

    id: UUID = Field(description="Message ID")
    role: str = Field(description="Message role (user or assistant)")
    content: str = Field(description="Message content")
    created_at: datetime = Field(description="When the message was created")

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""

    messages: list[HistoryMessage] = Field(
        default_factory=list,
        description="List of messages in chronological order"
    )
    count: int = Field(description="Total number of messages")


class ChatErrorResponse(BaseModel):
    """Schema for chat error responses."""

    error: str = Field(description="Error message")
    code: Optional[str] = Field(
        default=None,
        description="Error code for client handling"
    )
