"""
Module to handle selection of notification channels based on user preferences.
"""
import logging
from typing import List, Dict, Any
from shared.database.connection import SessionLocal
from shared.database.models import UserPreferences as UserPreferencesDB
import json

logger = logging.getLogger(__name__)


def get_user_notification_channels(user_id: str) -> List[str]:
    """
    Get the notification channels preferred by a user.

    Args:
        user_id: ID of the user

    Returns:
        List of notification channels (e.g., ['email', 'sms', 'push'])
    """
    try:
        db = SessionLocal()
        user_prefs = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == user_id).first()

        if user_prefs:
            # Parse the JSON string for notification channels
            channels = json.loads(user_prefs.notification_channels)
            return channels
        else:
            # Default to email if no preferences found
            logger.info(f"No preferences found for user {user_id}, using default channels")
            return ["email"]

    except Exception as e:
        logger.error(f"Error retrieving user preferences for {user_id}: {str(e)}")
        # Return default channels in case of error
        return ["email"]
    finally:
        db.close()


def get_user_timezone(user_id: str) -> str:
    """
    Get the timezone preference for a user.

    Args:
        user_id: ID of the user

    Returns:
        User's timezone (default: UTC)
    """
    try:
        db = SessionLocal()
        user_prefs = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == user_id).first()

        if user_prefs:
            return user_prefs.timezone
        else:
            logger.info(f"No timezone found for user {user_id}, using default")
            return "UTC"

    except Exception as e:
        logger.error(f"Error retrieving user timezone for {user_id}: {str(e)}")
        return "UTC"
    finally:
        db.close()


def get_advance_notification_minutes(user_id: str) -> int:
    """
    Get the advance notification minutes preference for a user.

    Args:
        user_id: ID of the user

    Returns:
        Minutes before deadline to send notification (default: 15)
    """
    try:
        db = SessionLocal()
        user_prefs = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == user_id).first()

        if user_prefs:
            return user_prefs.advance_notification_minutes
        else:
            logger.info(f"No advance notification preference found for user {user_id}, using default")
            return 15

    except Exception as e:
        logger.error(f"Error retrieving advance notification preference for {user_id}: {str(e)}")
        return 15
    finally:
        db.close()


def is_in_do_not_disturb_window(user_id: str) -> bool:
    """
    Check if the current time is within the user's do-not-disturb window.

    Args:
        user_id: ID of the user

    Returns:
        True if currently in do-not-disturb window, False otherwise
    """
    try:
        from datetime import datetime
        import pytz

        db = SessionLocal()
        user_prefs = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == user_id).first()

        if user_prefs and user_prefs.do_not_disturb_start and user_prefs.do_not_disturb_end:
            # Get current time in user's timezone
            user_tz = pytz.timezone(user_prefs.timezone)
            current_time = datetime.now(user_tz)

            # Get the current time in HH:MM format
            current_hour_min = current_time.strftime('%H:%M')

            # Check if current time is in the do-not-disturb window
            start_time = user_prefs.do_not_disturb_start
            end_time = user_prefs.do_not_disturb_end

            if start_time <= end_time:
                # Same day window (e.g., 22:00 to 07:00)
                return start_time <= current_hour_min <= end_time
            else:
                # Cross-day window (e.g., 22:00 to 07:00 next day)
                return current_hour_min >= start_time or current_hour_min <= end_time

        return False

    except Exception as e:
        logger.error(f"Error checking do-not-disturb window for {user_id}: {str(e)}")
        return False
    finally:
        db.close()