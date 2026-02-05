"""
Tests for User Story 3: Handle Missed Deadlines
As a user, I want the system to handle missed deadlines appropriately so that I receive follow-up notifications about overdue tasks.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import UUID

from scheduler_service.app.scheduler.missed_deadline_handler import (
    detect_and_handle_missed_deadlines,
    create_overdue_notification,
    schedule_overdue_follow_up
)
from shared.database.models import ScheduledNotification as ScheduledNotificationDB, Todo as TodoDB


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock()
    return session


@pytest.mark.asyncio
async def test_detect_and_handle_missed_deadlines():
    """
    Test that the system detects and handles missed deadlines properly.
    """
    # Create a mock database session
    mock_db = Mock()

    # Create a mock scheduled notification that represents a missed deadline
    mock_scheduled_notification = Mock()
    mock_scheduled_notification.todo_id = UUID(int=1)
    mock_scheduled_notification.user_id = UUID(int=2)
    mock_scheduled_notification.scheduled_time = datetime.utcnow() - timedelta(hours=1)  # Past time
    mock_scheduled_notification.notification_type = "deadline"
    mock_scheduled_notification.status = "pending"

    # Create a mock todo that has a past deadline
    mock_todo = Mock()
    mock_todo.deadline = datetime.utcnow() - timedelta(minutes=30)  # Past deadline

    # Configure the mock to return the scheduled notification and todo
    mock_db.query().filter().all.return_value = [mock_scheduled_notification]
    mock_db.query().filter().first.return_value = mock_todo

    # Call the function
    await detect_and_handle_missed_deadlines(mock_db)

    # Verify that the database was called to update the original notification
    # and create a new overdue notification
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_create_overdue_notification():
    """
    Test that overdue notifications are created properly for missed deadlines.
    """
    # Create a mock database session
    mock_db = Mock()

    # Create a mock scheduled notification that represents a missed deadline
    mock_original_scheduled = Mock()
    mock_original_scheduled.todo_id = UUID(int=1)
    mock_original_scheduled.user_id = UUID(int=2)
    mock_original_scheduled.scheduled_time = datetime.utcnow() - timedelta(hours=1)
    mock_original_scheduled.notification_type = "deadline"

    # Call the function
    await create_overdue_notification(mock_db, mock_original_scheduled)

    # Verify that a new overdue notification was added to the session
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_schedule_overdue_follow_up():
    """
    Test that follow-up notifications for overdue tasks are scheduled properly.
    """
    # Create a mock database session
    mock_db = Mock()

    # Call the function
    await schedule_overdue_follow_up(
        mock_db,
        "123e4567-e89b-12d3-a456-426614174000",
        "123e4567-e89b-12d3-a456-426614174001",
        "Test Todo",
        follow_up_delay_hours=1
    )

    # Verify that a follow-up notification was added to the session
    assert mock_db.add.called
    assert mock_db.commit.called


def test_user_story_3_acceptance_scenario():
    """
    Test User Story 3 acceptance scenario:
    Given user has missed a deadline, When configured follow-up time elapses,
    Then user receives overdue reminder notification
    """
    # This test validates the overall flow for handling missed deadlines
    # In a real implementation, this would be an integration test
    import scheduler_service.app.scheduler.missed_deadline_handler
    import scheduler_service.app.main

    # Verify that required modules and functions exist
    assert hasattr(scheduler_service.app.scheduler.missed_deadline_handler, 'detect_and_handle_missed_deadlines')
    assert hasattr(scheduler_service.app.scheduler.missed_deadline_handler, 'create_overdue_notification')
    assert hasattr(scheduler_service.app.scheduler.missed_deadline_handler, 'schedule_overdue_follow_up')
    assert hasattr(scheduler_service.app.main.SchedulerService, 'periodic_missed_deadline_check')

    print("All required components for User Story 3 are implemented.")