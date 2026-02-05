"""Task database model using SQLModel."""

import random
from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlmodel import SQLModel, Field
import uuid6


def generate_uuid7() -> UUID:
    """Generate a time-ordered UUID7."""
    return uuid6.uuid7()


def generate_task_number() -> int:
    """Generate a random 4-digit task number (1000-9999).

    This provides an easy-to-remember ID for voice agents and chatbots.
    Uniqueness per user is enforced at creation time in the route.
    """
    return random.randint(1000, 9999)


class TaskBase(SQLModel):
    """Base task fields shared by all task schemas."""

    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task title/description text"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description of the task"
    )
    completed: bool = Field(
        default=False,
        description="Whether the task is completed"
    )


class Task(TaskBase, table=True):
    """Task database model."""

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique task identifier"
    )
    task_number: int = Field(
        default_factory=generate_task_number,
        index=True,
        description="Short random ID for voice/chat agents (e.g., 'Task 4521')"
    )
    user_id: str = Field(
        index=True,
        description="Owner user ID from JWT token"
    )
    order: int = Field(
        default=0,
        description="Display order for sorting"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was last modified"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When the task was marked complete"
    )
    deadline: Optional[datetime] = Field(
        default=None,
        description="Optional deadline for the task"
    )
