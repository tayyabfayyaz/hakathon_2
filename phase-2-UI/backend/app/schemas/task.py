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
        description="Task description text",
        examples=["Buy groceries", "Complete project report"]
    )


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT)."""

    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task description text"
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
        description="Task description text"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Whether the task is completed"
    )


class TaskResponse(BaseModel):
    """Schema for task in API responses."""

    id: UUID
    text: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""

    tasks: list[TaskResponse]
    count: int
