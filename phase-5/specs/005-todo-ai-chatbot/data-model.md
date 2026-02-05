# Data Model: Todo AI Chatbot with Voice Assistant (Phase-3 Enhanced)

**Feature Branch**: `005-todo-ai-chatbot` (enhanced with `001-voice-assistant`)
**Date**: 2026-01-25 (Voice Assistant addition)

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │   Conversation  │       │     Message     │
│  (External)     │       │                 │       │                 │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id: string      │◄──────│ user_id: string │       │ id: UUID        │
│                 │       │ id: UUID        │◄──────│ conversation_id │
│                 │       │ created_at      │       │ user_id: string │
│                 │       │ updated_at      │       │ role: enum      │
│                 │       │                 │       │ content: text   │
│                 │       │                 │       │ input_method    │ ← NEW
│                 │       │                 │       │ created_at      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
        │
        │                 ┌─────────────────┐       ┌─────────────────────┐
        │                 │      Task       │       │ UserVoicePreferences│ ← NEW
        │                 │   (Existing)    │       │                     │
        │                 ├─────────────────┤       ├─────────────────────┤
        └────────────────►│ user_id: string │◄──────│ user_id: string     │
                          │ id: UUID        │       │ voice_output_enabled│
                          │ text: string    │       │ continuous_mode     │
                          │ completed: bool │       │ preferred_voice     │
                          │ order: int      │       │ updated_at          │
                          │ created_at      │       └─────────────────────┘
                          │ updated_at      │
                          │ completed_at    │
                          └─────────────────┘
```

## Entities

### Conversation (New)

Represents a chat session for a user. Each user has exactly one conversation (single-conversation model per spec assumptions).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID7 | PK, auto-generated | Unique conversation identifier |
| user_id | string | NOT NULL, INDEX, UNIQUE | Owner's user ID from JWT |
| created_at | datetime | NOT NULL, auto | When conversation was started |
| updated_at | datetime | NOT NULL, auto | When last message was added |

**Validation Rules**:
- `user_id` must be non-empty string
- One conversation per user (enforced by UNIQUE constraint)

**Indexes**:
- Primary key on `id`
- Unique index on `user_id` (for fast lookup and one-per-user enforcement)

---

### Message (Existing - Extended for Voice)

Represents a single message in a conversation. Messages are either from the user or the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID7 | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK → Conversation.id, NOT NULL | Parent conversation |
| user_id | string | NOT NULL, INDEX | Owner's user ID (denormalized for queries) |
| role | enum('user', 'assistant') | NOT NULL | Message sender role |
| content | text | NOT NULL, max 10000 chars | Message text content |
| **input_method** | enum('text', 'voice') | NOT NULL, default 'text' | **NEW**: How the message was input |
| created_at | datetime | NOT NULL, auto | When message was created |

**Validation Rules**:
- `role` must be one of: 'user', 'assistant'
- `content` must be non-empty, max 10,000 characters
- `content` must not be empty string or whitespace-only
- `input_method` must be one of: 'text', 'voice'

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` (for fetching conversation history)
- Index on `user_id` (for user-scoped queries)
- Composite index on `(conversation_id, created_at)` for ordered message retrieval

---

### UserVoicePreferences (New)

Represents a user's voice assistant settings. Persisted server-side for cross-device consistency.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | string | PK | Owner's user ID from JWT |
| voice_output_enabled | bool | NOT NULL, default true | Whether AI responses are spoken |
| continuous_mode_enabled | bool | NOT NULL, default false | Whether continuous listening is on |
| preferred_voice | string | NULLABLE | Browser voice URI identifier |
| updated_at | datetime | NOT NULL, auto | When preferences were last changed |

**Validation Rules**:
- `user_id` must be non-empty string
- `preferred_voice` can be null (use browser default) or a valid voiceURI string

**Indexes**:
- Primary key on `user_id`

---

### Task (Existing - Extended)

The existing Task model from Phase-2 needs a `description` field added per spec requirements.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID7 | PK, auto-generated | Unique task identifier |
| user_id | string | NOT NULL, INDEX | Owner's user ID from JWT |
| text | string | NOT NULL, 1-500 chars | Task title/main text |
| **description** | text | NULLABLE, max 2000 chars | **NEW**: Optional task description |
| completed | bool | NOT NULL, default false | Completion status |
| order | int | NOT NULL, default 0 | Display order |
| created_at | datetime | NOT NULL, auto | Creation timestamp |
| updated_at | datetime | NOT NULL, auto | Last modification timestamp |
| completed_at | datetime | NULLABLE | When marked complete |

**Migration Required**: Add `description` column to existing `tasks` table.

---

## SQLModel Definitions

### Conversation Model

```python
class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions."""

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        index=True,
        unique=True,
        description="Owner user ID - one conversation per user"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversation was started"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When last message was added"
    )
```

### Message Model (Extended)

```python
class MessageRole(str, Enum):
    """Valid message sender roles."""
    USER = "user"
    ASSISTANT = "assistant"


class InputMethod(str, Enum):
    """How the message was input."""
    TEXT = "text"
    VOICE = "voice"


class Message(SQLModel, table=True):
    """Message model for conversation messages."""

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation"
    )
    user_id: str = Field(
        index=True,
        description="Owner user ID (denormalized)"
    )
    role: MessageRole = Field(
        description="Message sender role (user or assistant)"
    )
    content: str = Field(
        max_length=10000,
        description="Message text content"
    )
    input_method: InputMethod = Field(
        default=InputMethod.TEXT,
        description="How the message was input (text or voice)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When message was created"
    )
```

### UserVoicePreferences Model (New)

```python
class UserVoicePreferences(SQLModel, table=True):
    """User voice assistant preferences."""

    __tablename__ = "user_voice_preferences"

    user_id: str = Field(
        primary_key=True,
        description="Owner user ID"
    )
    voice_output_enabled: bool = Field(
        default=True,
        description="Whether AI responses are spoken aloud"
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
```

### Task Model Extension

```python
# Add to existing Task model
description: Optional[str] = Field(
    default=None,
    max_length=2000,
    description="Optional detailed task description"
)
```

---

## State Transitions

### Conversation States

```
[Not Exists] ──create──► [Active]
                              │
                              ▼
                        (messages added)
```

Conversations are created on first message and remain active indefinitely.

### Message States

Messages are immutable once created. No state transitions.

### Task States (Existing)

```
[Created] ──complete──► [Completed]
    │                        │
    ▼                        ▼
 (update)                (uncomplete)
    │                        │
    ▼                        ▼
[Updated]              [Uncompleted]
    │
    ▼
 (delete)
    │
    ▼
[Deleted]
```

---

## Database Migration

### Migration: Add Conversation and Message Tables

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

### Migration: Add Description to Tasks

```sql
-- Add description column to tasks table
ALTER TABLE tasks ADD COLUMN description TEXT;
```

### Migration: Add Voice Preferences Table and Message Input Method

```sql
-- Create user_voice_preferences table
CREATE TABLE user_voice_preferences (
    user_id VARCHAR PRIMARY KEY,
    voice_output_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    continuous_mode_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    preferred_voice VARCHAR,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Add input_method column to messages table
ALTER TABLE messages ADD COLUMN input_method VARCHAR NOT NULL DEFAULT 'text';
ALTER TABLE messages ADD CONSTRAINT chk_input_method CHECK (input_method IN ('text', 'voice'));
```

---

## Query Patterns

### Get or Create Conversation

```python
async def get_or_create_conversation(user_id: str) -> Conversation:
    """Get existing conversation or create new one for user."""
    conversation = await session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation
```

### Get Conversation History

```python
async def get_messages(conversation_id: UUID, limit: int = 50) -> list[Message]:
    """Get messages for conversation, ordered by creation time."""
    return await session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    ).all()
```

### Add Message (Updated for Voice)

```python
async def add_message(
    conversation_id: UUID,
    user_id: str,
    role: MessageRole,
    content: str,
    input_method: InputMethod = InputMethod.TEXT
) -> Message:
    """Add a message to the conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        input_method=input_method
    )
    session.add(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message
```

### Get or Create Voice Preferences

```python
async def get_or_create_voice_preferences(user_id: str) -> UserVoicePreferences:
    """Get existing voice preferences or create defaults for user."""
    prefs = await session.get(UserVoicePreferences, user_id)

    if not prefs:
        prefs = UserVoicePreferences(user_id=user_id)
        session.add(prefs)
        await session.commit()
        await session.refresh(prefs)

    return prefs
```

### Update Voice Preferences

```python
async def update_voice_preferences(
    user_id: str,
    voice_output_enabled: Optional[bool] = None,
    continuous_mode_enabled: Optional[bool] = None,
    preferred_voice: Optional[str] = None
) -> UserVoicePreferences:
    """Update user's voice preferences."""
    prefs = await get_or_create_voice_preferences(user_id)

    if voice_output_enabled is not None:
        prefs.voice_output_enabled = voice_output_enabled
    if continuous_mode_enabled is not None:
        prefs.continuous_mode_enabled = continuous_mode_enabled
    if preferred_voice is not None:
        prefs.preferred_voice = preferred_voice

    prefs.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(prefs)
    return prefs
```
