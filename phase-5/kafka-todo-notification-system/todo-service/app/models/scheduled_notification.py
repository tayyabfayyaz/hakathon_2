from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ScheduledNotificationBase(BaseModel):
    todo_id: str
    user_id: str
    scheduled_time: datetime
    notification_type: str  # 'reminder', 'deadline', 'overdue'
    status: str = "pending"


class ScheduledNotificationCreate(ScheduledNotificationBase):
    pass


class ScheduledNotificationUpdate(BaseModel):
    status: Optional[str] = None
    processed_at: Optional[datetime] = None


class ScheduledNotification(ScheduledNotificationBase):
    id: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True