from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    priority = Column(String(10), default="normal")  # low, normal, high
    status = Column(String(20), default="pending")  # pending, completed, deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledNotification(Base):
    __tablename__ = "scheduled_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    todo_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    notification_type = Column(String(20), nullable=False)  # reminder, deadline, overdue
    status = Column(String(20), default="pending")  # pending, triggered, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class NotificationRequest(Base):
    __tablename__ = "notification_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    todo_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    deadline = Column(DateTime, nullable=False)
    channels = Column(String, nullable=False)  # JSON string of channels
    priority = Column(String(10), default="normal")  # low, normal, high
    status = Column(String(20), default="pending")  # pending, processing, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


class TodoEvent(Base):
    __tablename__ = "todo_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    todo_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    event_type = Column(String(20), nullable=False)  # created, updated, deleted
    payload = Column(String, nullable=False)  # JSON string of event data
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    notification_channels = Column(String, nullable=False)  # JSON string of channels
    advance_notification_minutes = Column(Integer, default=15)
    do_not_disturb_start = Column(String)  # HH:MM format
    do_not_disturb_end = Column(String)    # HH:MM format
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)