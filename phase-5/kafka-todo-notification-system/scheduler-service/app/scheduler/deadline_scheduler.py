"""
Deadline scheduler module to handle both reminder and deadline notifications.
"""
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from shared.database.models import ScheduledNotification as ScheduledNotificationDB
from shared.schemas.events import NotificationRequestEvent
from shared.utils import calculate_advance_time
import json


async def schedule_reminder_and_deadline_notifications(
    db: Session,
    todo_id: str,
    user_id: str,
    deadline: datetime,
    title: str,
    advance_minutes: int = 15
):
    """
    Schedule both reminder and deadline notifications for a todo.

    Args:
        db: Database session
        todo_id: ID of the todo
        user_id: ID of the user
        deadline: Deadline datetime
        title: Todo title
        advance_minutes: Minutes before deadline for reminder (default: 15)
    """
    # Calculate reminder time
    reminder_time = calculate_advance_time(deadline, advance_minutes)

    # Schedule reminder notification
    await _schedule_single_notification(
        db, todo_id, user_id, reminder_time, "reminder",
        title, f"Reminder: Your task '{title}' is due soon!"
    )

    # Schedule deadline notification
    await _schedule_single_notification(
        db, todo_id, user_id, deadline, "deadline",
        title, f"Deadline reached: Your task '{title}' is now due!"
    )


async def _schedule_single_notification(
    db: Session,
    todo_id: str,
    user_id: str,
    scheduled_time: datetime,
    notification_type: str,
    title: str,
    message: str
):
    """
    Schedule a single notification.

    Args:
        db: Database session
        todo_id: ID of the todo
        user_id: ID of the user
        scheduled_time: When to send the notification
        notification_type: Type of notification ('reminder', 'deadline', 'overdue')
        title: Todo title
        message: Notification message
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    import atexit

    # Create scheduled notification entry in database
    schedule_id = str(uuid.uuid4())

    scheduled_notification = ScheduledNotificationDB(
        id=uuid.UUID(schedule_id),
        todo_id=uuid.UUID(todo_id),
        user_id=uuid.UUID(user_id),
        scheduled_time=scheduled_time,
        notification_type=notification_type,
        status="pending"
    )

    db.add(scheduled_notification)
    db.commit()

    # In a real implementation, this would schedule the job with APScheduler
    # For now, we'll just log that it would be scheduled
    print(f"Scheduled {notification_type} notification for todo {todo_id} at {scheduled_time}")


async def update_notification_status(db: Session, schedule_id: str, status: str):
    """
    Update the status of a scheduled notification.

    Args:
        db: Database session
        schedule_id: ID of the scheduled notification
        status: New status
    """
    scheduled_notification = db.query(ScheduledNotificationDB).filter(
        ScheduledNotificationDB.id == uuid.UUID(schedule_id)
    ).first()

    if scheduled_notification:
        scheduled_notification.status = status
        db.commit()