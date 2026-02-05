from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_app")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TodoDB(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String)
    deadline = Column(DateTime)
    priority = Column(String, default="normal")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreferenceDB(Base):
    __tablename__ = "notification_preferences"

    user_id = Column(String, primary_key=True)
    notification_channels = Column(String)  # JSON string
    advance_notification_minutes = Column(Integer, default=15)
    do_not_disturb_start = Column(String)  # HH:MM format
    do_not_disturb_end = Column(String)    # HH:MM format
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledNotificationDB(Base):
    __tablename__ = "scheduled_notifications"

    id = Column(String, primary_key=True, index=True)
    todo_id = Column(String, index=True)
    user_id = Column(String, index=True)
    scheduled_time = Column(DateTime, index=True)
    notification_type = Column(String)  # 'reminder' | 'deadline' | 'overdue'
    status = Column(String, default="pending")  # 'pending' | 'sent' | 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()