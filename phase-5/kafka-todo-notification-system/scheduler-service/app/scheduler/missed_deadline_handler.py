"""
Missed deadline handler module to detect and handle missed deadlines.
This module implements the functionality for tasks T047-T054.
"""
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy.orm import Session
from typing import List, Optional

from shared.database.models import (
    ScheduledNotification as ScheduledNotificationDB,
    Todo as TodoDB
)
from shared.schemas.events import NotificationRequestEvent
from shared.utils import calculate_advance_time

logger = logging.getLogger(__name__)


async def detect_and_handle_missed_deadlines(db: Session):
    """
    Detect and handle missed deadlines by creating overdue notifications.

    Args:
        db: Database session
    """
    # Find all scheduled notifications that are pending but whose scheduled time
    # has passed (indicating a missed deadline)
    current_time = datetime.utcnow()

    # Look for scheduled notifications that were supposed to be processed but weren't
    # (e.g., reminder notifications for deadlines that have already passed)
    missed_notifications = db.query(ScheduledNotificationDB).filter(
        ScheduledNotificationDB.status == "pending",
        ScheduledNotificationDB.scheduled_time < current_time,
        ScheduledNotificationDB.notification_type.in_(["reminder", "deadline"])
    ).all()

    for scheduled_notification in missed_notifications:
        # Get the associated todo to check if the deadline has actually passed
        todo = db.query(TodoDB).filter(TodoDB.id == scheduled_notification.todo_id).first()

        if todo and todo.deadline < current_time:
            # This is indeed a missed deadline, create an overdue notification
            await create_overdue_notification(db, scheduled_notification)


async def create_overdue_notification(
    db: Session,
    original_scheduled_notification: ScheduledNotificationDB
):
    """
    Create an overdue notification for a missed deadline.

    Args:
        db: Database session
        original_scheduled_notification: The original scheduled notification that was missed
    """
    # Create a new overdue notification
    schedule_id = str(uuid.uuid4())

    # Calculate when to send the overdue notification (immediately or after a delay)
    overdue_time = datetime.utcnow()  # Send immediately for now

    overdue_notification = ScheduledNotificationDB(
        id=uuid.UUID(schedule_id),
        todo_id=original_scheduled_notification.todo_id,
        user_id=original_scheduled_notification.user_id,
        scheduled_time=overdue_time,
        notification_type="overdue",
        status="pending"
    )

    db.add(overdue_notification)
    db.commit()

    # Update the original notification as cancelled since it was missed
    original_scheduled_notification.status = "missed"
    original_scheduled_notification.processed_at = datetime.utcnow()
    db.commit()

    logger.info(f"Created overdue notification for todo {original_scheduled_notification.todo_id}")


async def schedule_overdue_follow_up(
    db: Session,
    todo_id: str,
    user_id: str,
    title: str,
    follow_up_delay_hours: int = 24  # Default to 24 hours
):
    """
    Schedule a follow-up notification for a missed deadline.

    Args:
        db: Database session
        todo_id: ID of the todo
        user_id: ID of the user
        title: Title of the todo
        follow_up_delay_hours: Hours to wait before sending follow-up
    """
    schedule_id = str(uuid.uuid4())

    # Schedule follow-up notification after the specified delay
    follow_up_time = datetime.utcnow() + timedelta(hours=follow_up_delay_hours)

    follow_up_notification = ScheduledNotificationDB(
        id=uuid.UUID(schedule_id),
        todo_id=uuid.UUID(todo_id),
        user_id=uuid.UUID(user_id),
        scheduled_time=follow_up_time,
        notification_type="overdue_followup",
        status="pending"
    )

    db.add(follow_up_notification)
    db.commit()

    logger.info(f"Scheduled follow-up notification for todo {todo_id} at {follow_up_time}")


async def handle_todo_updated_cancel_scheduled_notifications(
    db: Session,
    todo_id: str
):
    """
    Cancel all scheduled notifications when a todo is updated.

    Args:
        db: Database session
        todo_id: ID of the todo that was updated
    """
    # Get all pending scheduled notifications for this todo
    scheduled_notifications = db.query(ScheduledNotificationDB).filter(
        ScheduledNotificationDB.todo_id == uuid.UUID(todo_id),
        ScheduledNotificationDB.status == "pending"
    ).all()

    for scheduled in scheduled_notifications:
        # Update status in database
        scheduled.status = "cancelled"
        scheduled.processed_at = datetime.utcnow()

    db.commit()
    logger.info(f"Cancelled scheduled notifications for updated todo {todo_id}")


async def handle_todo_deleted_cancel_scheduled_notifications(
    db: Session,
    todo_id: str
):
    """
    Cancel all scheduled notifications when a todo is deleted.

    Args:
        db: Database session
        todo_id: ID of the todo that was deleted
    """
    # Get all pending scheduled notifications for this todo
    scheduled_notifications = db.query(ScheduledNotificationDB).filter(
        ScheduledNotificationDB.todo_id == uuid.UUID(todo_id),
        ScheduledNotificationDB.status == "pending"
    ).all()

    for scheduled in scheduled_notifications:
        # Update status in database
        scheduled.status = "cancelled"
        scheduled.processed_at = datetime.utcnow()

    db.commit()
    logger.info(f"Cancelled scheduled notifications for deleted todo {todo_id}")


async def get_overdue_todos(db: Session) -> List[TodoDB]:
    """
    Get all todos that are overdue (past their deadline and not completed).

    Args:
        db: Database session

    Returns:
        List of overdue todos
    """
    current_time = datetime.utcnow()

    overdue_todos = db.query(TodoDB).filter(
        TodoDB.deadline < current_time,
        TodoDB.status != "completed"
    ).all()

    return overdue_todos