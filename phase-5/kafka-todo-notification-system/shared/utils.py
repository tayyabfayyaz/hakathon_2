import uuid
from datetime import datetime, timedelta
from typing import Optional
import pytz


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()


def convert_to_utc(dt: datetime, source_timezone: str = 'UTC') -> datetime:
    """Convert datetime from source timezone to UTC."""
    if dt.tzinfo is not None:
        # If datetime is already timezone-aware, convert to UTC
        return dt.astimezone(pytz.UTC).replace(tzinfo=None)
    else:
        # If datetime is naive, assume it's in the source timezone and convert to UTC
        tz = pytz.timezone(source_timezone)
        localized_dt = tz.localize(dt)
        return localized_dt.astimezone(pytz.UTC).replace(tzinfo=None)


def calculate_advance_time(deadline: datetime, minutes_before: int) -> datetime:
    """Calculate the time for advance notification before a deadline."""
    return deadline - timedelta(minutes=minutes_before)


def is_in_do_not_disturb(current_time: datetime, start_time: Optional[str], end_time: Optional[str]) -> bool:
    """Check if current time falls within do-not-disturb period."""
    if not start_time or not end_time:
        return False

    current_hour_min = current_time.strftime('%H:%M')
    return start_time <= current_hour_min <= end_time


def validate_email(email: str) -> bool:
    """Simple email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None