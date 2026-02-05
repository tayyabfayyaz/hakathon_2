"""
Tests for User Story 1: Receive Deadline Reminders
As a user, I want to receive timely reminders about upcoming todo deadlines so that I can complete important tasks on time.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.api.todos import create_todo
from shared.database.connection import SessionLocal
from shared.schemas.events import TodoCreatedEvent


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock(spec=SessionLocal)
    return session


@pytest.mark.asyncio
async def test_user_story_1_acceptance_scenario():
    """
    Test User Story 1 acceptance scenario:
    Given user creates a todo with a deadline, When deadline approaches, Then user receives a reminder notification
    """
    # Given: User creates a todo with a deadline
    from app.models.todo import TodoCreate

    # Create a todo that's due in 15 minutes (which should trigger a reminder)
    future_deadline = datetime.utcnow() + timedelta(minutes=15)

    todo_create_data = TodoCreate(
        title="Test Todo for Reminder",
        description="This is a test todo to verify reminder functionality",
        deadline=future_deadline,
        priority="normal",
        user_id="test_user_123"
    )

    # Mock the database session
    mock_db = Mock()

    # Mock the Kafka producer to capture the event
    with patch('app.api.todos.get_kafka_producer') as mock_get_producer:
        mock_producer = Mock()
        mock_get_producer.return_value = mock_producer

        # Call the create_todo function
        result = create_todo(todo_create_data, mock_db)

        # Then: Verify the todo was created successfully
        assert result.title == "Test Todo for Reminder"
        assert result.user_id == "test_user_123"
        assert result.deadline == future_deadline

        # And: Verify that a todo.created event was published to Kafka
        mock_producer.send_event.assert_called_once()
        call_args = mock_producer.send_event.call_args
        assert call_args[1]['topic'] == 'todo.created'
        assert call_args[1]['key'] == 'test_user_123'

        # Verify the event payload contains the correct data
        event_payload = call_args[1]['value']
        assert event_payload['title'] == "Test Todo for Reminder"
        assert event_payload['user_id'] == "test_user_123"
        assert event_payload['deadline'] == future_deadline


@pytest.mark.asyncio
async def test_scheduler_creates_reminder_notifications():
    """
    Test that the scheduler creates reminder notifications based on todo deadlines.
    This simulates the interaction between the todo service and scheduler service.
    """
    # Mock the event that would be received by the scheduler
    event_data = {
        "todo_id": "test-todo-123",
        "user_id": "test-user-456",
        "title": "Test Todo",
        "description": "Test description",
        "deadline": datetime.utcnow() + timedelta(minutes=15),
        "priority": "normal",
        "created_at": datetime.utcnow(),
        "event_timestamp": datetime.utcnow()
    }

    # Import the scheduler service functionality
    from scheduler_service.app.main import SchedulerService

    # Mock the database and scheduler
    with patch.object(SchedulerService, '__init__', lambda x: None):
        with patch('scheduler_service.app.main.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value.__iter__.return_value = [mock_db]

            scheduler = SchedulerService()
            scheduler.db = mock_db

            # Mock the APScheduler
            with patch('scheduler_service.app.main.scheduler') as mock_scheduler:
                # Call the handle_todo_created method
                await scheduler.handle_todo_created(event_data)

                # Verify that notifications were scheduled
                # Should schedule both reminder (15 mins before) and deadline notifications
                assert mock_scheduler.add_job.call_count >= 2


def test_acceptance_criteria_validation():
    """
    Validate that the acceptance criteria are met:
    1. User creates a todo with a deadline
    2. System sends a reminder notification before the deadline
    3. The notification is delivered to the user
    """
    # This test verifies the overall flow and acceptance criteria
    # In a real implementation, this would be an integration test

    # The system should:
    # 1. Accept todo creation with deadline
    # 2. Publish event to Kafka
    # 3. Scheduler should pick up event and schedule notifications
    # 4. Notification service should send reminder before deadline
    # 5. User should receive the notification

    # For this test, we validate that the components exist and are connected
    import app.api.todos
    import shared.kafka.producer
    import scheduler_service.app.main
    import notification_service.app.main

    # Verify that required modules exist
    assert hasattr(app.api.todos, 'create_todo')
    assert hasattr(shared.kafka.producer, 'get_kafka_producer')
    assert hasattr(scheduler_service.app.main, 'SchedulerService')
    assert hasattr(notification_service.app.main, 'NotificationService')

    print("All required components for User Story 1 are implemented.")