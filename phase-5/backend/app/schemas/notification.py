"""Notification request/response schemas."""

from datetime import datetime
from uuid import UUID
from typing import Optional, Literal

from pydantic import BaseModel, Field


# Type aliases for notification type and status
NotificationTypeStr = Literal["deadline_reminder", "deadline_reached", "task_overdue", "system"]
NotificationStatusStr = Literal["pending", "sent", "read", "dismissed"]


class NotificationResponse(BaseModel):
    """Schema for notification in API responses."""

    id: UUID
    user_id: str
    task_id: Optional[UUID] = None
    type: str
    title: str
    message: str
    status: str
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for list of notifications response."""

    notifications: list[NotificationResponse]
    count: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Schema for unread count response."""

    unread_count: int


class MarkAsReadRequest(BaseModel):
    """Schema for marking notifications as read."""

    notification_ids: list[UUID] = Field(
        description="List of notification IDs to mark as read"
    )


class MarkAsReadResponse(BaseModel):
    """Schema for mark as read response."""

    marked_count: int
    message: str


class NotificationCreate(BaseModel):
    """Schema for creating a notification (internal use)."""

    user_id: str
    task_id: Optional[UUID] = None
    type: NotificationTypeStr
    title: str
    message: str
