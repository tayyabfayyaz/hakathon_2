from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json

from shared.database.connection import get_db
from ..models.user_preferences import UserPreferences, UserPreferencesCreate, UserPreferencesUpdate
from shared.database.models import UserPreferences as UserPreferencesDB

router = APIRouter(prefix="/api/v1/users", tags=["preferences"])


@router.get("/{user_id}/preferences", response_model=UserPreferences)
def get_user_preferences(user_id: str, db: Session = Depends(get_db)):
    """Get user preferences."""
    db_preferences = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == uuid.UUID(user_id)).first()
    if not db_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    # Parse JSON fields
    notification_channels = json.loads(db_preferences.notification_channels)

    return UserPreferences(
        user_id=str(db_preferences.user_id),
        notification_channels=notification_channels,
        advance_notification_minutes=db_preferences.advance_notification_minutes,
        do_not_disturb_start=db_preferences.do_not_disturb_start,
        do_not_disturb_end=db_preferences.do_not_disturb_end,
        timezone=db_preferences.timezone,
        created_at=db_preferences.created_at,
        updated_at=db_preferences.updated_at
    )


@router.put("/{user_id}/preferences", response_model=UserPreferences)
def update_user_preferences(user_id: str, preferences_update: UserPreferencesUpdate, db: Session = Depends(get_db)):
    """Update user preferences."""
    # Check if preferences exist
    db_preferences = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == uuid.UUID(user_id)).first()

    if not db_preferences:
        # Create new preferences if they don't exist
        if not preferences_update.notification_channels:
            raise HTTPException(status_code=400, detail="Notification channels are required for new preferences")

        db_preferences = UserPreferencesDB(
            user_id=uuid.UUID(user_id),
            notification_channels=json.dumps(preferences_update.notification_channels),
            advance_notification_minutes=preferences_update.advance_notification_minutes or 15,
            do_not_disturb_start=preferences_update.do_not_disturb_start,
            do_not_disturb_end=preferences_update.do_not_disturb_end,
            timezone=preferences_update.timezone or "UTC",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_preferences)
    else:
        # Update existing preferences
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'notification_channels' and value is not None:
                setattr(db_preferences, field, json.dumps(value))
            elif value is not None:
                setattr(db_preferences, field, value)

        db_preferences.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_preferences)

    # Parse JSON fields
    notification_channels = json.loads(db_preferences.notification_channels)

    return UserPreferences(
        user_id=str(db_preferences.user_id),
        notification_channels=notification_channels,
        advance_notification_minutes=db_preferences.advance_notification_minutes,
        do_not_disturb_start=db_preferences.do_not_disturb_start,
        do_not_disturb_end=db_preferences.do_not_disturb_end,
        timezone=db_preferences.timezone,
        created_at=db_preferences.created_at,
        updated_at=db_preferences.updated_at
    )