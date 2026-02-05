"""Message database model using SQLModel."""

from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field
import uuid6


def generate_uuid7() -> UUID:
    """Generate a time-ordered UUID7."""
    return uuid6.uuid7()


class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"


class InputMethod(str, Enum):
    """How the message was input by the user."""
    TEXT = "text"
    VOICE = "voice"


class Message(SQLModel, table=True):
    """Message database model - stores chat messages."""

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        index=True,
        foreign_key="conversations.id",
        description="Parent conversation ID"
    )
    user_id: str = Field(
        index=True,
        description="Owner user ID for ownership validation"
    )
    role: str = Field(
        sa_column=sa.Column(sa.String(50), nullable=False),
        description="Message sender role (user or assistant)"
    )
    content: str = Field(
        max_length=10000,
        description="Message content"
    )
    input_method: str = Field(
        default="text",
        sa_column=sa.Column(sa.String(10), nullable=False, server_default="text"),
        description="How the message was input (text or voice)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was created"
    )
