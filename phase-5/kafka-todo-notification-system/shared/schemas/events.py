from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class TodoCreatedEvent(BaseModel):
    """Schema for todo created events published to Kafka"""
    todo_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    deadline: datetime
    priority: str = "normal"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class TodoUpdatedEvent(BaseModel):
    """Schema for todo updated events published to Kafka"""
    todo_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    deadline: datetime
    priority: str = "normal"
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class TodoDeletedEvent(BaseModel):
    """Schema for todo deleted events published to Kafka"""
    todo_id: str
    user_id: str
    deleted_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeadlineScheduledEvent(BaseModel):
    """Schema for deadline scheduled events published to Kafka"""
    schedule_id: str
    todo_id: str
    user_id: str
    deadline: datetime
    scheduled_time: datetime
    notification_type: str  # 'reminder' | 'deadline' | 'overdue'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class DeadlineTriggeredEvent(BaseModel):
    """Schema for deadline triggered events published to Kafka"""
    schedule_id: str
    todo_id: str
    user_id: str
    deadline: datetime
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationRequestEvent(BaseModel):
    """Schema for notification request events published to Kafka"""
    notification_id: str
    todo_id: str
    user_id: str
    title: str
    message: str
    deadline: datetime
    channels: List[str]  # ['email', 'sms', 'push']
    priority: str = "normal"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationSentEvent(BaseModel):
    """Schema for notification sent events published to Kafka"""
    notification_id: str
    todo_id: str
    user_id: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationFailedEvent(BaseModel):
    """Schema for notification failed events published to Kafka"""
    notification_id: str
    todo_id: str
    user_id: str
    error_message: str
    failed_at: datetime = Field(default_factory=datetime.utcnow)
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)