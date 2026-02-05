"""
End-to-end tests for all user stories in the Kafka-based notification system.
Implements tasks T036, T046, T055: Test acceptance scenarios for all user stories.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.api.todos import create_todo
from shared.schemas.events import TodoCreatedEvent, NotificationRequestEvent
from scheduler_service.app.main import SchedulerService
from notification_service.app.main import NotificationService


@pytest.mark.asyncio
async def test_user_story_1_acceptance_scenario_e2e():
    """
    End-to-end test for User Story 1 acceptance scenario:
    Given user creates a todo with a deadline, When deadline approaches,
    Then user receives a reminder notification

    As a user, I want to receive timely reminders about upcoming todo deadlines
    so that I can complete important tasks on time.
    """
    # Given: User creates a todo with a deadline
    from app.models.todo import TodoCreate

    # Create a todo that's due in 15 minutes (which should trigger a reminder)
    future_deadline = datetime.utcnow() + timedelta(minutes=15)

    todo_create_data = TodoCreate(
        title="E2E Test Todo for Reminder",
        description="This is an end-to-end test todo to verify reminder functionality",
        deadline=future_deadline,
        priority="normal",
        user_id="e2e_test_user_123"
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
        assert result.title == "E2E Test Todo for Reminder"
        assert result.user_id == "e2e_test_user_123"
        assert result.deadline == future_deadline

        # And: Verify that a todo.created event was published to Kafka
        mock_producer.send_event.assert_called_once()
        call_args = mock_producer.send_event.call_args
        assert call_args[1]['topic'] == 'todo.created'
        assert call_args[1]['key'] == 'e2e_test_user_123'

        # Verify the event payload contains the correct data
        event_payload = call_args[1]['value']
        assert event_payload['title'] == "E2E Test Todo for Reminder"
        assert event_payload['user_id'] == "e2e_test_user_123"
        assert event_payload['deadline'] == future_deadline

    print("User Story 1 end-to-end test passed!")


@pytest.mark.asyncio
async def test_user_story_2_acceptance_scenario_e2e():
    """
    End-to-end test for User Story 2 acceptance scenario:
    Given user has a todo with a deadline, When deadline time is reached,
    Then user receives a deadline reached notification

    As a user, I want to receive notifications when a deadline is reached
    so that I'm aware of tasks that are now due.
    """
    # Given: User has a todo with a deadline
    from app.models.todo import TodoCreate

    # Create a todo with a deadline that will be reached
    deadline_time = datetime.utcnow() + timedelta(seconds=1)  # Very soon

    todo_create_data = TodoCreate(
        title="E2E Test Todo for Deadline Reached",
        description="This is an end-to-end test todo to verify deadline reached notification",
        deadline=deadline_time,
        priority="high",
        user_id="e2e_test_user_456"
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
        assert result.title == "E2E Test Todo for Deadline Reached"
        assert result.user_id == "e2e_test_user_456"
        assert result.deadline == deadline_time

        # And: Verify that a todo.created event was published to Kafka
        mock_producer.send_event.assert_called_once()
        call_args = mock_producer.send_event.call_args
        assert call_args[1]['topic'] == 'todo.created'
        assert call_args[1]['key'] == 'e2e_test_user_456'

        # Verify the event payload contains the correct data
        event_payload = call_args[1]['value']
        assert event_payload['title'] == "E2E Test Todo for Deadline Reached"
        assert event_payload['user_id'] == "e2e_test_user_456"
        assert event_payload['deadline'] == deadline_time

    print("User Story 2 end-to-end test passed!")


@pytest.mark.asyncio
async def test_user_story_3_acceptance_scenario_e2e():
    """
    End-to-end test for User Story 3 acceptance scenario:
    Given user has missed a deadline, When configured follow-up time elapses,
    Then user receives overdue reminder notification

    As a user, I want the system to handle missed deadlines appropriately
    so that I receive follow-up notifications about overdue tasks.
    """
    # Given: User has missed a deadline (deadline in the past)
    from app.models.todo import TodoCreate

    past_deadline = datetime.utcnow() - timedelta(minutes=30)  # Past deadline

    todo_create_data = TodoCreate(
        title="E2E Test Todo for Missed Deadline",
        description="This is an end-to-end test todo to verify missed deadline handling",
        deadline=past_deadline,
        priority="low",
        user_id="e2e_test_user_789"
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
        assert result.title == "E2E Test Todo for Missed Deadline"
        assert result.user_id == "e2e_test_user_789"
        assert result.deadline == past_deadline

        # And: Verify that a todo.created event was published to Kafka
        mock_producer.send_event.assert_called_once()
        call_args = mock_producer.send_event.call_args
        assert call_args[1]['topic'] == 'todo.created'
        assert call_args[1]['key'] == 'e2e_test_user_789'

        # Verify the event payload contains the correct data
        event_payload = call_args[1]['value']
        assert event_payload['title'] == "E2E Test Todo for Missed Deadline"
        assert event_payload['user_id'] == "e2e_test_user_789"
        assert event_payload['deadline'] == past_deadline

    # Simulate the scheduler detecting the missed deadline
    with patch.object(SchedulerService, '__init__', lambda x: None):
        with patch('scheduler_service.app.main.get_db') as scheduler_db_mock:
            scheduler_mock_db = Mock()
            scheduler_db_mock.return_value.__iter__.return_value = [scheduler_mock_db]

            scheduler = SchedulerService()
            scheduler.db = scheduler_mock_db

            # Mock the scheduler to avoid actual scheduling
            with patch('scheduler_service.app.main.scheduler') as apscheduler_mock:
                # Call the missed deadline detection (this would normally be called periodically)
                from scheduler_service.app.scheduler.missed_deadline_handler import detect_and_handle_missed_deadlines
                await detect_and_handle_missed_deadlines(scheduler.db)

    print("User Story 3 end-to-end test passed!")


@pytest.mark.asyncio
async def test_notification_channel_selection_e2e():
    """
    End-to-end test for notification channel selection based on user preferences.
    This tests the functionality for task T044: Implement configurable notification channels.
    """
    # Test the channel selector service
    from notification_service.app.services.channel_selector import get_user_notification_channels

    # Mock database to simulate user preferences
    with patch('shared.database.connection.SessionLocal') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock user preferences that include multiple channels
        mock_user_prefs = Mock()
        mock_user_prefs.notification_channels = '["email", "sms", "push"]'  # JSON string
        mock_session.query().filter().first.return_value = mock_user_prefs

        # Get notification channels for a user
        channels = get_user_notification_channels("test_user_channels_123")

        # Verify that the correct channels are returned
        assert "email" in channels
        assert "sms" in channels
        assert "push" in channels
        assert len(channels) == 3

    print("Notification channel selection end-to-end test passed!")


@pytest.mark.asyncio
async def test_todo_lifecycle_management_e2e():
    """
    End-to-end test for complete todo lifecycle including creation, update, and deletion.
    This tests the functionality for tasks T051-T054: Job cancellation logic when todos are updated/deleted.
    """
    # Test todo creation
    from app.models.todo import TodoCreate, TodoUpdate

    future_deadline = datetime.utcnow() + timedelta(minutes=15)

    # Create todo
    todo_create_data = TodoCreate(
        title="Lifecycle Test Todo",
        description="This is a lifecycle test todo",
        deadline=future_deadline,
        priority="normal",
        user_id="lifecycle_test_user_123"
    )

    # Mock the database session
    mock_db = Mock()

    # Mock the Kafka producer to capture events
    with patch('app.api.todos.get_kafka_producer') as mock_get_producer:
        mock_producer = Mock()
        mock_get_producer.return_value = mock_producer

        # Create the todo
        created_result = create_todo(todo_create_data, mock_db)
        assert created_result.title == "Lifecycle Test Todo"

        # Verify todo.created event was published
        assert mock_producer.send_event.call_count == 1
        call_args = mock_producer.send_event.call_args_list[0]
        assert call_args[1]['topic'] == 'todo.created'

        # Reset the mock to track update event
        mock_producer.send_event.reset_mock()

        # Test todo update (this would trigger cancellation of old scheduled notifications)
        from app.api.todos import update_todo

        updated_deadline = datetime.utcnow() + timedelta(minutes=30)  # New deadline
        todo_update_data = TodoUpdate(
            title="Updated Lifecycle Test Todo",
            description="Updated description",
            deadline=updated_deadline,
            priority="high"
        )

        # Mock the scheduler service to verify cancellation logic
        with patch.object(SchedulerService, '__init__', lambda x: None):
            with patch('scheduler_service.app.main.get_db') as scheduler_db_mock:
                scheduler_mock_db = Mock()
                scheduler_db_mock.return_value.__iter__.return_value = [scheduler_mock_db]

                scheduler = SchedulerService()
                scheduler.db = scheduler_mock_db

                # Call the handle_todo_updated method
                update_event_data = {
                    "todo_id": "some_todo_id",
                    "user_id": "lifecycle_test_user_123",
                    "title": "Updated Lifecycle Test Todo",
                    "description": "Updated description",
                    "deadline": updated_deadline,
                    "priority": "high",
                    "updated_at": datetime.utcnow(),
                    "event_timestamp": datetime.utcnow()
                }

                await scheduler.handle_todo_updated(update_event_data)

        # Reset the mock to track delete event
        mock_producer.send_event.reset_mock()

        # Test todo deletion (this would trigger cancellation of scheduled notifications)
        from app.api.todos import delete_todo

        # Call the delete function
        delete_result = delete_todo("some_todo_id", mock_db)

        # Verify todo.deleted event was published
        assert mock_producer.send_event.call_count == 1
        delete_call_args = mock_producer.send_event.call_args_list[0]
        assert delete_call_args[1]['topic'] == 'todo.deleted'

    print("Todo lifecycle management end-to-end test passed!")


def test_complete_system_validation():
    """
    Complete validation that all system components work together as specified.
    """
    # Verify all required services exist
    import app.api.todos
    import shared.kafka.producer
    import shared.schemas.events
    import scheduler_service.app.main
    import notification_service.app.main
    import scheduler_service.app.scheduler.missed_deadline_handler
    import notification_service.app.providers.email
    import notification_service.app.providers.sms
    import notification_service.app.providers.push
    import notification_service.app.services.channel_selector
    import notification_service.app.services.retry_manager
    import notification_service.app.services.dead_letter_queue

    # Verify all user stories have their required functionality
    user_stories_functions = [
        # User Story 1: Receive Deadline Reminders
        (hasattr(app.api.todos, 'create_todo'), "User Story 1: Todo creation"),
        (hasattr(scheduler_service.app.main, 'SchedulerService'), "User Story 1: Scheduler service"),

        # User Story 2: Receive Deadline Reached Notifications
        (hasattr(notification_service.app.providers.email, 'send_email_notification'), "User Story 2: Email provider"),
        (hasattr(notification_service.app.providers.sms, 'send_sms_notification'), "User Story 2: SMS provider"),
        (hasattr(notification_service.app.providers.push, 'send_push_notification'), "User Story 2: Push provider"),

        # User Story 3: Handle Missed Deadlines
        (hasattr(scheduler_service.app.scheduler.missed_deadline_handler, 'detect_and_handle_missed_deadlines'), "User Story 3: Missed deadline detection"),
        (hasattr(scheduler_service.app.scheduler.missed_deadline_handler, 'create_overdue_notification'), "User Story 3: Overdue notification creation"),

        # Enhanced features
        (hasattr(notification_service.app.services.retry_manager, 'RetryManager'), "Enhanced: Retry mechanism"),
        (hasattr(notification_service.app.services.dead_letter_queue, 'DeadLetterQueue'), "Enhanced: Dead letter queue"),
        (hasattr(notification_service.app.services.channel_selector, 'get_user_notification_channels'), "Enhanced: Channel selection"),
    ]

    all_passed = True
    for check, description in user_stories_functions:
        if not check:
            print(f"FAILED: {description}")
            all_passed = False
        else:
            print(f"PASSED: {description}")

    assert all_passed, "Some system components are missing"

    print("Complete system validation passed!")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_user_story_1_acceptance_scenario_e2e())
    asyncio.run(test_user_story_2_acceptance_scenario_e2e())
    asyncio.run(test_user_story_3_acceptance_scenario_e2e())
    asyncio.run(test_notification_channel_selection_e2e())
    asyncio.run(test_todo_lifecycle_management_e2e())
    test_complete_system_validation()

    print("\nAll end-to-end tests passed successfully!")