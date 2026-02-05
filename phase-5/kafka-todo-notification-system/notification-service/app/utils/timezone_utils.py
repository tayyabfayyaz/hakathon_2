import pytz
from datetime import datetime
from typing import Optional


def convert_to_user_timezone(dt: datetime, user_timezone: str = 'UTC') -> datetime:
    """
    Convert a datetime from UTC to the user's timezone.

    Args:
        dt: The datetime to convert (assumed to be in UTC)
        user_timezone: The target timezone (default: UTC)

    Returns:
        The converted datetime in the user's timezone
    """
    if dt.tzinfo is None:
        # If datetime is naive, assume it's in UTC
        utc_tz = pytz.UTC
        dt = utc_tz.localize(dt)

    target_tz = pytz.timezone(user_timezone)
    return dt.astimezone(target_tz)


def convert_from_user_timezone(dt: datetime, user_timezone: str = 'UTC') -> datetime:
    """
    Convert a datetime from the user's timezone to UTC.

    Args:
        dt: The datetime to convert (in user's timezone)
        user_timezone: The source timezone (default: UTC)

    Returns:
        The converted datetime in UTC
    """
    source_tz = pytz.timezone(user_timezone)

    if dt.tzinfo is None:
        # If datetime is naive, localize it to the source timezone
        dt = source_tz.localize(dt)
    else:
        # If datetime is already timezone-aware, convert it
        dt = dt.astimezone(source_tz)

    return dt.astimezone(pytz.UTC)


def is_time_in_range(current_time: datetime, start_time: Optional[str], end_time: Optional[str]) -> bool:
    """
    Check if the current time falls within a specific range.

    Args:
        current_time: The current time to check
        start_time: Start time in 'HH:MM' format (inclusive)
        end_time: End time in 'HH:MM' format (inclusive)

    Returns:
        True if the current time is in the range, False otherwise
    """
    if not start_time or not end_time:
        return False

    # Convert current_time to HH:MM format
    current_hour_min = current_time.strftime('%H:%M')

    # Compare times as strings in HH:MM format
    return start_time <= current_hour_min <= end_time


def get_current_time_in_timezone(timezone: str = 'UTC') -> datetime:
    """
    Get the current time in the specified timezone.

    Args:
        timezone: The target timezone (default: UTC)

    Returns:
        The current datetime in the specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)