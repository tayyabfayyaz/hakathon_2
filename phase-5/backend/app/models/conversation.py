"""Conversation database model using SQLModel."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlmodel import SQLModel, Field
import uuid6


def generate_uuid7() -> UUID:
    """Generate a time-ordered UUID7."""
    return uuid6.uuid7()


class Conversation(SQLModel, table=True):
    """Conversation database model - one per user for chat history."""

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        unique=True,
        index=True,
        description="Owner user ID - one conversation per user"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was last updated"
    )
