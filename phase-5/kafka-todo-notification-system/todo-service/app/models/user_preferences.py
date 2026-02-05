from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserPreferencesBase(BaseModel):
    notification_channels: List[str]  # ['email', 'sms', 'push']
    advance_notification_minutes: int = 15
    do_not_disturb_start: Optional[str] = None  # 'HH:MM' format
    do_not_disturb_end: Optional[str] = None    # 'HH:MM' format
    timezone: str = "UTC"


class UserPreferencesCreate(UserPreferencesBase):
    user_id: str


class UserPreferencesUpdate(BaseModel):
    notification_channels: Optional[List[str]] = None
    advance_notification_minutes: Optional[int] = None
    do_not_disturb_start: Optional[str] = None
    do_not_disturb_end: Optional[str] = None
    timezone: Optional[str] = None


class UserPreferences(UserPreferencesBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True