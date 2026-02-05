"""Deadline scheduler service for task reminder notifications."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID

from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import get_settings
from app.database import async_session_factory
from app.models.task import Task
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.api.routes.websocket import send_notification_to_user

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional["DeadlineScheduler"] = None


class DeadlineScheduler:
    """Background service that monitors task deadlines and sends notifications."""

    # Time thresholds for reminders (in minutes)
    REMINDER_THRESHOLD_MINUTES = 30  # Send reminder 30 minutes before deadline
    CHECK_INTERVAL_SECONDS = 60  # Check every minute

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.settings = get_settings()

    async def start(self) -> None:
        """Start the deadline scheduler."""
        if self._running:
            logger.warning("Deadline scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("Deadline scheduler started")

    async def stop(self) -> None:
        """Stop the deadline scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Deadline scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks deadlines periodically."""
        while self._running:
            try:
                await self._check_deadlines()
            except Exception as e:
                logger.error(f"Error in deadline scheduler: {e}")

            # Wait before next check
            await asyncio.sleep(self.CHECK_INTERVAL_SECONDS)

    def _normalize_datetime(self, dt: datetime) -> datetime:
        """Normalize datetime to naive UTC for comparison."""
        if dt.tzinfo is not None:
            # Convert to UTC and make naive
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    async def _check_deadlines(self) -> None:
        """Check all tasks with deadlines and send appropriate notifications."""
        now = datetime.utcnow()
        reminder_threshold = now + timedelta(minutes=self.REMINDER_THRESHOLD_MINUTES)

        async with async_session_factory() as session:
            # Find tasks with deadlines that need attention
            # - Not completed
            # - Have a deadline set
            statement = select(Task).where(
                and_(
                    Task.completed == False,
                    Task.deadline.isnot(None),
                )
            )
            result = await session.exec(statement)
            tasks = result.all()

            # Filter tasks by deadline threshold in Python (handles timezone differences)
            for task in tasks:
                if task.deadline is None:
                    continue
                # Normalize deadline for comparison
                deadline = self._normalize_datetime(task.deadline)
                if deadline <= reminder_threshold:
                    await self._process_task_deadline(session, task, now)

    async def _process_task_deadline(
        self, session: AsyncSession, task: Task, now: datetime
    ) -> None:
        """Process a single task and send appropriate notification."""
        if task.deadline is None:
            return

        # Normalize deadline to naive UTC for comparison
        deadline = self._normalize_datetime(task.deadline)

        # Determine notification type based on deadline status
        if deadline <= now:
            # Deadline has passed
            time_overdue = now - deadline
            if time_overdue > timedelta(hours=1):
                notification_type = NotificationType.TASK_OVERDUE
                title = "Task Overdue"
                message = f"Task '{task.text}' is overdue by {self._format_duration(time_overdue)}."
            else:
                notification_type = NotificationType.DEADLINE_REACHED
                title = "Deadline Reached"
                message = f"The deadline for task '{task.text}' has just passed."
        else:
            # Deadline is approaching
            time_until = deadline - now
            notification_type = NotificationType.DEADLINE_REMINDER
            title = "Deadline Approaching"
            message = f"Task '{task.text}' is due in {self._format_duration(time_until)}."

        # Check if we already sent this type of notification for this task recently
        already_sent = await self._notification_already_sent(
            session, task.id, task.user_id, notification_type
        )

        if already_sent:
            return

        # Create and send notification
        await self._create_and_send_notification(
            session=session,
            user_id=task.user_id,
            task_id=task.id,
            task_text=task.text,
            notification_type=notification_type,
            title=title,
            message=message,
        )

    async def _notification_already_sent(
        self,
        session: AsyncSession,
        task_id: UUID,
        user_id: str,
        notification_type: NotificationType,
    ) -> bool:
        """Check if a notification of this type was already sent for this task recently."""
        # For deadline_reminder: check last 30 minutes
        # For deadline_reached: check last 5 minutes
        # For task_overdue: check last 1 hour

        if notification_type == NotificationType.DEADLINE_REMINDER:
            time_window = timedelta(minutes=30)
        elif notification_type == NotificationType.DEADLINE_REACHED:
            time_window = timedelta(minutes=5)
        else:  # TASK_OVERDUE
            time_window = timedelta(hours=1)

        cutoff_time = datetime.utcnow() - time_window

        statement = select(Notification).where(
            and_(
                Notification.task_id == task_id,
                Notification.user_id == user_id,
                Notification.type == notification_type.value,
                Notification.created_at >= cutoff_time,
            )
        )
        result = await session.exec(statement)
        existing = result.first()

        return existing is not None

    async def _create_and_send_notification(
        self,
        session: AsyncSession,
        user_id: str,
        task_id: UUID,
        task_text: str,
        notification_type: NotificationType,
        title: str,
        message: str,
    ) -> None:
        """Create notification in database and send via WebSocket."""
        # Create notification record
        notification = Notification(
            user_id=user_id,
            task_id=task_id,
            type=notification_type.value,
            title=title,
            message=message,
            status=NotificationStatus.SENT.value,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)

        logger.info(
            f"Created {notification_type.value} notification for task {task_id} (user: {user_id})"
        )

        # Send via WebSocket
        notification_dict = {
            "id": str(notification.id),
            "user_id": notification.user_id,
            "task_id": str(notification.task_id) if notification.task_id else None,
            "type": notification_type.value,
            "title": notification.title,
            "message": notification.message,
            "status": notification.status,
            "read_at": None,
            "created_at": notification.created_at.isoformat(),
        }

        sent = await send_notification_to_user(user_id, notification_dict)
        if sent:
            logger.info(f"Sent {notification_type.value} notification via WebSocket to user {user_id}")
        else:
            logger.debug(f"User {user_id} not connected via WebSocket (notification saved to DB)")

    def _format_duration(self, duration: timedelta) -> str:
        """Format a timedelta as a human-readable string."""
        total_seconds = int(duration.total_seconds())

        if total_seconds < 0:
            total_seconds = abs(total_seconds)

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 or not parts:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        return ", ".join(parts[:2])  # Only show top 2 units

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running


async def get_scheduler() -> DeadlineScheduler:
    """Get the global deadline scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = DeadlineScheduler()
    return _scheduler


async def start_scheduler() -> DeadlineScheduler:
    """Start and return the global deadline scheduler."""
    scheduler = await get_scheduler()
    await scheduler.start()
    return scheduler


async def stop_scheduler() -> None:
    """Stop the global deadline scheduler."""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None
