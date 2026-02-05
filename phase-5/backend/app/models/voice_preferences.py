"""UserVoicePreferences database model for voice assistant settings."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserVoicePreferences(SQLModel, table=True):
    """User voice assistant preferences stored server-side for cross-device sync.

    Attributes:
        user_id: Primary key - user ID from JWT token
        voice_output_enabled: Whether AI responses should be spoken aloud
        continuous_mode_enabled: Whether continuous listening mode is active
        preferred_voice: Browser voice URI for TTS (null = browser default)
        updated_at: When preferences were last updated
    """

    __tablename__ = "user_voice_preferences"

    user_id: str = Field(
        primary_key=True,
        description="Owner user ID from JWT token"
    )
    voice_output_enabled: bool = Field(
        default=True,
        description="Whether AI responses should be spoken aloud"
    )
    continuous_mode_enabled: bool = Field(
        default=False,
        description="Whether continuous listening mode is active"
    )
    preferred_voice: Optional[str] = Field(
        default=None,
        description="Browser voice URI for TTS (null = browser default)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When preferences were last updated"
    )
