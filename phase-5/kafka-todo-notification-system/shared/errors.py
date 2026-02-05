"""Custom exception classes for the notification system."""


class NotificationError(Exception):
    """Base exception for notification-related errors."""
    pass


class TodoNotFoundError(NotificationError):
    """Raised when a todo is not found."""
    pass


class UserNotFoundError(NotificationError):
    """Raised when a user is not found."""
    pass


class NotificationChannelError(NotificationError):
    """Raised when there's an error with a notification channel."""
    pass


class KafkaConnectionError(NotificationError):
    """Raised when there's an error connecting to Kafka."""
    pass


class DatabaseError(NotificationError):
    """Raised when there's an error with database operations."""
    pass


class SchedulerError(NotificationError):
    """Raised when there's an error with the scheduler."""
    pass


class ValidationError(NotificationError):
    """Raised when data validation fails."""
    pass