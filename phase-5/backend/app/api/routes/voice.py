"""Voice preferences API endpoints.

Implements REST endpoints for managing user voice assistant preferences:
- GET /{user_id}/voice/preferences - Get user's voice settings
- PUT /{user_id}/voice/preferences - Update voice settings
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models import UserVoicePreferences
from app.schemas.voice import VoicePreferences, VoicePreferencesUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/{user_id}/voice", tags=["Voice"])


async def get_or_create_voice_preferences(
    session: SessionDep,
    user_id: str
) -> UserVoicePreferences:
    """Get existing voice preferences or create defaults for user.

    Args:
        session: Database session
        user_id: User ID from JWT token

    Returns:
        UserVoicePreferences object (existing or newly created with defaults)
    """
    statement = select(UserVoicePreferences).where(
        UserVoicePreferences.user_id == user_id
    )
    result = await session.execute(statement)
    prefs = result.scalar_one_or_none()

    if prefs is None:
        prefs = UserVoicePreferences(user_id=user_id)
        session.add(prefs)
        await session.commit()
        await session.refresh(prefs)

    return prefs


@router.get(
    "/preferences",
    response_model=VoicePreferences,
    responses={
        401: {"description": "Unauthorized - Invalid or missing JWT"},
        403: {"description": "Forbidden - User ID mismatch with JWT"},
    },
)
async def get_voice_preferences(
    user_id: str,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> VoicePreferences:
    """
    Get user's voice assistant preferences.

    Returns current voice settings. Creates defaults if none exist.

    - **user_id**: User ID (must match JWT token)
    """
    # Security: Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    prefs = await get_or_create_voice_preferences(session, user_id)

    return VoicePreferences(
        user_id=prefs.user_id,
        voice_output_enabled=prefs.voice_output_enabled,
        continuous_mode_enabled=prefs.continuous_mode_enabled,
        preferred_voice=prefs.preferred_voice,
        updated_at=prefs.updated_at,
    )


@router.put(
    "/preferences",
    response_model=VoicePreferences,
    responses={
        400: {"description": "Invalid request body"},
        401: {"description": "Unauthorized - Invalid or missing JWT"},
        403: {"description": "Forbidden - User ID mismatch with JWT"},
    },
)
async def update_voice_preferences(
    user_id: str,
    update_data: VoicePreferencesUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> VoicePreferences:
    """
    Update user's voice assistant preferences.

    Only provided fields will be updated. Omitted fields remain unchanged.

    - **user_id**: User ID (must match JWT token)
    - **voice_output_enabled**: Whether AI responses should be spoken
    - **continuous_mode_enabled**: Whether continuous listening mode is on
    - **preferred_voice**: Browser voice URI for TTS
    """
    # Security: Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    prefs = await get_or_create_voice_preferences(session, user_id)

    # Update only provided fields
    if update_data.voice_output_enabled is not None:
        prefs.voice_output_enabled = update_data.voice_output_enabled
    if update_data.continuous_mode_enabled is not None:
        prefs.continuous_mode_enabled = update_data.continuous_mode_enabled
    if update_data.preferred_voice is not None:
        prefs.preferred_voice = update_data.preferred_voice

    prefs.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(prefs)

    logger.info(f"Updated voice preferences for user {user_id}")

    return VoicePreferences(
        user_id=prefs.user_id,
        voice_output_enabled=prefs.voice_output_enabled,
        continuous_mode_enabled=prefs.continuous_mode_enabled,
        preferred_voice=prefs.preferred_voice,
        updated_at=prefs.updated_at,
    )
