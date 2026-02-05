from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NotificationPreference(BaseModel):
    """Schema for user notification preferences"""
    user_id: str
    notification_channels: List[str] = Field(default=["email"])
    advance_notification_minutes: int = 15
    do_not_disturb_start: Optional[str] = None  # HH:MM format
    do_not_disturb_end: Optional[str] = None    # HH:MM format
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoItem(BaseModel):
    """Schema for todo item"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "normal"
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScheduledNotification(BaseModel):
    """Schema for scheduled notifications"""
    id: str
    todo_id: str
    user_id: str
    scheduled_time: datetime
    notification_type: str  # 'reminder' | 'deadline' | 'overdue'
    status: str = "pending"  # 'pending' | 'sent' | 'failed'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None