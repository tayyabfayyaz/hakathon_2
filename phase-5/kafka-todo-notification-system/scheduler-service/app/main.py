import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import json
import uuid
from kafka import KafkaConsumer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.orm import Session
from datetime import datetime as dt
import pytz

from shared.kafka_config.config import KafkaConfig
from shared.schemas.events import TodoCreatedEvent, TodoUpdatedEvent, TodoDeletedEvent, NotificationRequestEvent
from shared.database.connection import SessionLocal
from shared.database.models import ScheduledNotification as ScheduledNotificationDB, TodoEvent as TodoEventDB
from shared.utils import calculate_advance_time, is_in_do_not_disturb
import json as json_lib
from .scheduler.missed_deadline_handler import (
    detect_and_handle_missed_deadlines,
    handle_todo_updated_cancel_scheduled_notifications,
    handle_todo_deleted_cancel_scheduled_notifications,
    schedule_overdue_follow_up
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SchedulerService:
    def __init__(self):
        self.consumer = None
        self.running = False
        self.db_generator = get_db()
        self.db = next(self.db_generator)

    async def start(self):
        """Start the scheduler service."""
        global scheduler
        logger.info("Starting Scheduler Service...")

        # Initialize scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }

        scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        scheduler.start()

        # Schedule periodic check for missed deadlines (every 5 minutes)
        scheduler.add_job(
            func=self.periodic_missed_deadline_check,
            trigger='interval',
            minutes=5,
            id='missed_deadline_checker'
        )

        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            KafkaConfig.TOPIC_TODO_CREATED,
            KafkaConfig.TOPIC_TODO_UPDATED,
            KafkaConfig.TOPIC_TODO_DELETED,
            bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
            group_id=KafkaConfig.CONSUMER_GROUP_SCHEDULER,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )

        self.running = True

        # Start consuming messages
        await self.consume_messages()

    async def consume_messages(self):
        """Consume Kafka messages and process them."""
        logger.info("Scheduler service started consuming messages")

        try:
            for message in self.consumer:
                if not self.running:
                    break

                topic = message.topic
                event_data = message.value

                try:
                    if topic == KafkaConfig.TOPIC_TODO_CREATED:
                        await self.handle_todo_created(event_data)
                    elif topic == KafkaConfig.TOPIC_TODO_UPDATED:
                        await self.handle_todo_updated(event_data)
                    elif topic == KafkaConfig.TOPIC_TODO_DELETED:
                        await self.handle_todo_deleted(event_data)

                    # Commit the offset after successful processing
                    self.consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {str(e)}")
                    # In a production system, you might want to send to a dead letter topic
                    self.consumer.commit()  # Still commit to avoid getting stuck

        except Exception as e:
            logger.error(f"Error in message consumption loop: {str(e)}")

    async def handle_todo_created(self, event_data):
        """Handle todo created event."""
        try:
            event = TodoCreatedEvent(**event_data)
            logger.info(f"Handling todo created event: {event.todo_id}")

            # Get user preferences for notification settings
            advance_minutes = 15  # Default, would normally fetch from user preferences

            # Calculate reminder time (based on user preferences)
            if event.deadline:
                # Calculate reminder time (15 minutes before deadline)
                reminder_time = calculate_advance_time(event.deadline, advance_minutes)

                # Schedule reminder notification
                await self.schedule_notification(
                    todo_id=event.todo_id,
                    user_id=event.user_id,
                    scheduled_time=reminder_time,
                    notification_type="reminder",
                    title=event.title,
                    message=f"Reminder: Your task '{event.title}' is due soon!"
                )

                # Schedule deadline notification
                await self.schedule_notification(
                    todo_id=event.todo_id,
                    user_id=event.user_id,
                    scheduled_time=event.deadline,
                    notification_type="deadline",
                    title=event.title,
                    message=f"Deadline reached: Your task '{event.title}' is now due!"
                )

        except Exception as e:
            logger.error(f"Error handling todo created event: {str(e)}")

    async def handle_todo_updated(self, event_data):
        """Handle todo updated event."""
        try:
            event = TodoUpdatedEvent(**event_data)
            logger.info(f"Handling todo updated event: {event.todo_id}")

            # Cancel existing scheduled notifications for this todo
            await handle_todo_updated_cancel_scheduled_notifications(self.db, event.todo_id)

            # Schedule new notifications based on updated deadline
            if event.deadline:
                # Calculate reminder time (15 minutes before deadline)
                advance_minutes = 15  # Default, would normally fetch from user preferences
                reminder_time = calculate_advance_time(event.deadline, advance_minutes)

                # Schedule reminder notification
                await self.schedule_notification(
                    todo_id=event.todo_id,
                    user_id=event.user_id,
                    scheduled_time=reminder_time,
                    notification_type="reminder",
                    title=event.title,
                    message=f"Reminder: Your task '{event.title}' is due soon!"
                )

                # Schedule deadline notification
                await self.schedule_notification(
                    todo_id=event.todo_id,
                    user_id=event.user_id,
                    scheduled_time=event.deadline,
                    notification_type="deadline",
                    title=event.title,
                    message=f"Deadline reached: Your task '{event.title}' is now due!"
                )

        except Exception as e:
            logger.error(f"Error handling todo updated event: {str(e)}")

    async def handle_todo_deleted(self, event_data):
        """Handle todo deleted event."""
        try:
            event = TodoDeletedEvent(**event_data)
            logger.info(f"Handling todo deleted event: {event.todo_id}")

            # Cancel existing scheduled notifications for this todo
            await handle_todo_deleted_cancel_scheduled_notifications(self.db, event.todo_id)

        except Exception as e:
            logger.error(f"Error handling todo deleted event: {str(e)}")

    async def schedule_notification(self, todo_id: str, user_id: str, scheduled_time: dt,
                                   notification_type: str, title: str, message: str):
        """Schedule a notification at the specified time."""
        schedule_id = str(uuid.uuid4())

        # Create scheduled notification entry in database
        scheduled_notification = ScheduledNotificationDB(
            id=uuid.UUID(schedule_id),
            todo_id=uuid.UUID(todo_id),
            user_id=uuid.UUID(user_id),
            scheduled_time=scheduled_time,
            notification_type=notification_type,
            status="pending"
        )

        self.db.add(scheduled_notification)
        self.db.commit()

        # Schedule the job with APScheduler
        job_id = f"notification_{schedule_id}"

        # Create a closure to capture the parameters
        async def notification_callback():
            await self.trigger_notification(schedule_id, todo_id, user_id, notification_type, title, message)

        scheduler.add_job(
            func=notification_callback,
            trigger='date',
            run_date=scheduled_time,
            id=job_id
        )

        logger.info(f"Scheduled {notification_type} notification for todo {todo_id} at {scheduled_time}")

    async def trigger_notification(self, schedule_id: str, todo_id: str, user_id: str,
                                  notification_type: str, title: str, message: str):
        """Trigger a notification when scheduled time arrives."""
        logger.info(f"Triggering notification for schedule {schedule_id}")

        # Update status in database
        scheduled_notification = self.db.query(ScheduledNotificationDB).filter(
            ScheduledNotificationDB.id == uuid.UUID(schedule_id)
        ).first()

        if scheduled_notification:
            scheduled_notification.status = "triggered"
            scheduled_notification.processed_at = dt.utcnow()
            self.db.commit()

        # Publish notification request event to Kafka
        try:
            notification_id = str(uuid.uuid4())

            # Default to email channel, would normally fetch from user preferences
            channels = ["email"]

            event = NotificationRequestEvent(
                notification_id=notification_id,
                todo_id=todo_id,
                user_id=user_id,
                title=title,
                message=message,
                deadline=scheduled_notification.scheduled_time if scheduled_notification else dt.utcnow(),
                channels=channels,
                priority="high" if notification_type == "deadline" else "normal"
            )

            # Send event to Kafka
            from shared.kafka.producer import get_kafka_producer
            kafka_producer = get_kafka_producer()
            kafka_producer.send_event(
                topic="notification.request",
                key=user_id,
                value=event.dict()
            )

            logger.info(f"Published notification request event for notification {notification_id}")
        except Exception as e:
            logger.error(f"Failed to publish notification request event: {str(e)}")

    async def cancel_scheduled_notifications_for_todo(self, todo_id: str):
        """Cancel all scheduled notifications for a specific todo."""
        try:
            # Get all pending scheduled notifications for this todo
            scheduled_notifications = self.db.query(ScheduledNotificationDB).filter(
                ScheduledNotificationDB.todo_id == uuid.UUID(todo_id),
                ScheduledNotificationDB.status == "pending"
            ).all()

            for scheduled in scheduled_notifications:
                # Remove from scheduler
                job_id = f"notification_{scheduled.id}"
                if scheduler.get_job(job_id):
                    scheduler.remove_job(job_id)

                # Update status in database
                scheduled.status = "cancelled"
                scheduled.processed_at = dt.utcnow()

            self.db.commit()
            logger.info(f"Cancelled scheduled notifications for todo {todo_id}")

        except Exception as e:
            logger.error(f"Error cancelling scheduled notifications for todo {todo_id}: {str(e)}")

    async def periodic_missed_deadline_check(self):
        """Periodically check for missed deadlines and handle them."""
        try:
            logger.info("Checking for missed deadlines...")
            await detect_and_handle_missed_deadlines(self.db)
        except Exception as e:
            logger.error(f"Error in periodic missed deadline check: {str(e)}")

    async def stop(self):
        """Stop the scheduler service."""
        logger.info("Stopping Scheduler Service...")
        self.running = False

        if scheduler:
            scheduler.shutdown()

        if self.consumer:
            self.consumer.close()

        # Close database session
        self.db.close()

        logger.info("Scheduler Service stopped")


async def main():
    """Main function to run the scheduler service."""
    scheduler_service = SchedulerService()

    try:
        await scheduler_service.start()
    except KeyboardInterrupt:
        print("Received interrupt signal")
    finally:
        await scheduler_service.stop()


if __name__ == "__main__":
    asyncio.run(main())