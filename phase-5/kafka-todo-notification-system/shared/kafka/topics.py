"""Constants for Kafka topics used in the notification system."""

# Todo-related topics
TOPIC_TODO_CREATED = "todo.created"
TOPIC_TODO_UPDATED = "todo.updated"
TOPIC_TODO_DELETED = "todo.deleted"

# Deadline-related topics
TOPIC_DEADLINE_SCHEDULED = "deadline.scheduled"
TOPIC_DEADLINE_TRIGGERED = "deadline.triggered"

# Notification-related topics
TOPIC_NOTIFICATION_REQUEST = "notification.request"
TOPIC_NOTIFICATION_SENT = "notification.sent"
TOPIC_NOTIFICATION_FAILED = "notification.failed"

# All topics
ALL_TOPICS = [
    TOPIC_TODO_CREATED,
    TOPIC_TODO_UPDATED,
    TOPIC_TODO_DELETED,
    TOPIC_DEADLINE_SCHEDULED,
    TOPIC_DEADLINE_TRIGGERED,
    TOPIC_NOTIFICATION_REQUEST,
    TOPIC_NOTIFICATION_SENT,
    TOPIC_NOTIFICATION_FAILED,
]