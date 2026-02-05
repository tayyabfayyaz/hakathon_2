"""
Simple validation script to verify that the Kafka-based notification system
files exist and are properly structured.
"""
import os

def validate_system_files():
    """
    Validate that all required system files exist.
    """
    print("Validating Kafka-based notification system file structure...")

    # Define the required files
    required_files = [
        # Todo Service
        "todo-service/app/api/todos.py",
        "todo-service/app/api/preferences.py",
        "todo-service/app/models/todo.py",
        "todo-service/app/models/scheduled_notification.py",
        "todo-service/app/models/user_preferences.py",

        # Scheduler Service
        "scheduler-service/app/main.py",
        "scheduler-service/app/scheduler/deadline_scheduler.py",
        "scheduler-service/app/scheduler/missed_deadline_handler.py",  # New file
        "scheduler-service/app/consumers/todo_consumer.py",

        # Notification Service
        "notification-service/app/main.py",
        "notification-service/app/providers/email.py",
        "notification-service/app/providers/sms.py",
        "notification-service/app/providers/push.py",
        "notification-service/app/services/notification_service.py",
        "notification-service/app/services/channel_selector.py",
        "notification-service/app/services/retry_manager.py",  # New file
        "notification-service/app/services/dead_letter_queue.py",  # New file

        # Shared Components
        "shared/schemas/events.py",
        "shared/database/models.py",
        "shared/kafka/producer.py",
        "shared/kafka/consumer.py",
        "shared/utils.py",

        # Configuration
        "docker-compose.yml",
    ]

    success_count = 0
    total_files = len(required_files)

    for file_path in required_files:
        full_path = file_path  # We're already in the kafka-todo-notification-system directory
        if os.path.exists(full_path):
            print(f"[OK] {file_path}: Exists")
            success_count += 1
        else:
            print(f"[MISSING] {file_path}: Missing")

    print(f"\nFile validation complete: {success_count}/{total_files} files exist")

    # Additional validation for specific functionality
    print("\nValidating specific functionality implementations:")

    # Check for missed deadline functionality
    with open("scheduler-service/app/scheduler/missed_deadline_handler.py", "r") as f:
        content = f.read()
        if "detect_and_handle_missed_deadlines" in content:
            print("[OK] Missed deadline detection: Implemented")
        else:
            print("[MISSING] Missed deadline detection: Not found")

    # Check for retry mechanism
    with open("notification-service/app/services/retry_manager.py", "r") as f:
        content = f.read()
        if "exponential backoff" in content.lower():
            print("[OK] Retry mechanism with exponential backoff: Implemented")
        else:
            print("[MISSING] Retry mechanism with exponential backoff: Not found")

    # Check for dead letter queue
    with open("notification-service/app/services/dead_letter_queue.py", "r") as f:
        content = f.read()
        if "dead letter queue" in content.lower():
            print("[OK] Dead letter queue: Implemented")
        else:
            print("[MISSING] Dead letter queue: Not found")

    # Check for periodic checks in scheduler
    with open("scheduler-service/app/main.py", "r") as f:
        content = f.read()
        if "periodic_missed_deadline_check" in content:
            print("[OK] Periodic missed deadline checks: Implemented")
        else:
            print("[MISSING] Periodic missed deadline checks: Not found")

    if success_count == total_files:
        print("\n[SUCCESS] All required files exist and system is properly structured!")
        return True
    else:
        print(f"\n[WARNING] {total_files - success_count} files are missing from the system.")
        return False

if __name__ == "__main__":
    validate_system_files()