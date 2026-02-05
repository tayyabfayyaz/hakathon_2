"""Task request/response schemas."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task title text",
        examples=["Buy groceries", "Complete project report"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description of the task"
    )


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT)."""

    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task title text"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description of the task"
    )
    completed: bool = Field(
        description="Whether the task is completed"
    )


class TaskPatch(BaseModel):
    """Schema for partial task update (PATCH)."""

    text: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Task title text"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description of the task"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Whether the task is completed"
    )


class TaskResponse(BaseModel):
    """Schema for task in API responses."""

    id: UUID
    task_number: int = Field(description="Short random ID for voice/chat agents (e.g., 'Task 4521')")
    user_id: str = Field(description="Owner user ID")
    text: str
    description: Optional[str] = None
    completed: bool
    deadline: Optional[datetime] = None
    order: int = Field(default=0, description="Display order for sorting")
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeadlineRequest(BaseModel):
    """Schema for setting a task deadline."""

    deadline: datetime = Field(
        description="The deadline datetime (must be in the future)"
    )


class DeadlineResponse(BaseModel):
    """Schema for deadline operation response."""

    task_id: UUID
    deadline: Optional[datetime] = None
    message: str = Field(description="Operation result message")


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""

    tasks: list[TaskResponse]
    count: int
