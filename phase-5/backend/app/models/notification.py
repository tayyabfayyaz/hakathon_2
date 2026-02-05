"""Notification database model using SQLModel."""

from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
import uuid6


def generate_uuid7() -> UUID:
    """Generate a time-ordered UUID7."""
    return uuid6.uuid7()


class NotificationType(str, Enum):
    """Types of notifications."""

    DEADLINE_REMINDER = "deadline_reminder"  # Reminder before deadline
    DEADLINE_REACHED = "deadline_reached"    # Deadline has arrived
    TASK_OVERDUE = "task_overdue"            # Task is past deadline
    SYSTEM = "system"                        # System notification


class NotificationStatus(str, Enum):
    """Status of a notification."""

    PENDING = "pending"      # Created but not yet sent
    SENT = "sent"            # Successfully delivered
    READ = "read"            # User has read it
    DISMISSED = "dismissed"  # User dismissed it


class NotificationBase(SQLModel):
    """Base notification fields shared by all notification schemas."""

    type: str = Field(
        sa_column=Column(String(30)),
        description="Type of notification"
    )
    title: str = Field(
        max_length=200,
        description="Notification title"
    )
    message: str = Field(
        max_length=1000,
        description="Notification message body"
    )


class Notification(NotificationBase, table=True):
    """Notification database model."""

    __tablename__ = "notifications"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique notification identifier"
    )
    user_id: str = Field(
        index=True,
        description="Owner user ID from JWT token"
    )
    task_id: Optional[UUID] = Field(
        default=None,
        index=True,
        description="Related task ID (if applicable)"
    )
    status: str = Field(
        default="sent",
        sa_column=Column(String(20)),
        description="Current notification status"
    )
    read_at: Optional[datetime] = Field(
        default=None,
        description="When the notification was read"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the notification was created"
    )
