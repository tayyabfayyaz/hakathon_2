"""Database migration utilities for the notification system."""
from sqlalchemy import create_engine, inspect
from shared.database.connection import Base, DATABASE_URL
from shared.database.models import Todo, ScheduledNotification, NotificationRequest, TodoEvent, UserPreferences
import logging

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables if they don't exist."""
    engine = create_engine(DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_database():
    """Run database migrations."""
    logger.info("Starting database migration...")

    # Create tables if they don't exist
    create_tables()

    # Check if each table exists and log
    tables = ['todos', 'scheduled_notifications', 'notification_requests', 'todo_events', 'user_preferences']
    for table in tables:
        exists = check_table_exists(table)
        if exists:
            logger.info(f"Table '{table}' exists")
        else:
            logger.warning(f"Table '{table}' does not exist")

    logger.info("Database migration completed")


if __name__ == "__main__":
    migrate_database()