"""Voice preferences request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VoicePreferences(BaseModel):
    """Schema for voice preferences response."""

    user_id: str = Field(description="User's unique identifier")
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
    updated_at: datetime = Field(description="When preferences were last updated")

    class Config:
        from_attributes = True


class VoicePreferencesUpdate(BaseModel):
    """Schema for updating voice preferences."""

    voice_output_enabled: Optional[bool] = Field(
        default=None,
        description="Whether AI responses should be spoken aloud"
    )
    continuous_mode_enabled: Optional[bool] = Field(
        default=None,
        description="Whether continuous listening mode is active"
    )
    preferred_voice: Optional[str] = Field(
        default=None,
        description="Browser voice URI for TTS (null = browser default)"
    )
