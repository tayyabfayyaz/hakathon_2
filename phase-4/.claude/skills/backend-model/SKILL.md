---
name: backend-model
description: Create SQLModel database models with proper fields, relationships, and indexes. Use when defining database tables, adding columns, or creating migrations.
argument-hint: "[model-name]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# SQLModel Database Models

Create database models following the TodoList Pro patterns.

## Model Template

```python
# app/models/{resource}.py
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel, Field
from uuid6 import uuid7


class {Resource}(SQLModel, table=True):
    __tablename__ = "{resources}"

    # Primary key - UUID7 for time-ordered IDs
    id: UUID = Field(default_factory=uuid7, primary_key=True)

    # User ownership (always index for isolation queries)
    user_id: str = Field(index=True)

    # Core fields
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

    # Status fields
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

## Existing Models

### Task Model

```python
# app/models/task.py
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    task_number: int = Field(index=True)  # Short ID (1000-9999)
    user_id: str = Field(index=True)
    text: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Conversation Model

```python
# app/models/conversation.py
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: str = Field(unique=True, index=True)  # One per user
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Message Model

```python
# app/models/message.py
from sqlalchemy import Column, String

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str = Field(sa_column=Column(String(50)))  # "user" or "assistant"
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Notification Model

```python
# app/models/notification.py
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    user_id: str = Field(index=True)
    task_id: Optional[UUID] = Field(default=None, index=True)
    type: str  # "deadline_reminder", "deadline_reached", "task_overdue", "system"
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    status: str = Field(default="pending")  # "pending", "sent", "read", "dismissed"
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

## Field Types

```python
from sqlmodel import Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Required string with length limits
title: str = Field(min_length=1, max_length=200)

# Optional string
description: Optional[str] = Field(default=None, max_length=2000)

# Boolean with default
is_active: bool = Field(default=True)

# Integer with constraints
count: int = Field(ge=0, le=100)

# Foreign key
parent_id: UUID = Field(foreign_key="parents.id", index=True)

# Unique constraint
email: str = Field(unique=True, index=True)

# Indexed field
user_id: str = Field(index=True)

# Enum via string
status: str  # Use string, validate in schema
```

## Database Session

```python
# app/database.py
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Migrations with Alembic

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "add {resource} table"
```

### Migration Template

```python
# alembic/versions/xxx_add_resource_table.py
"""add {resource} table

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = 'xxx'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        '{resources}',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_{resources}_user_id', '{resources}', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_{resources}_user_id', table_name='{resources}')
    op.drop_table('{resources}')
```

### Run Migrations

```bash
alembic upgrade head      # Apply all
alembic downgrade -1      # Rollback one
alembic current           # Show current
alembic history           # Show history
```

## Query Patterns

```python
from sqlmodel import select

# Get by ID
item = await session.get(Model, item_id)

# Filter query
result = await session.exec(
    select(Model)
    .where(Model.user_id == user_id)
    .where(Model.is_active == True)
    .order_by(Model.created_at.desc())
    .limit(50)
)
items = result.all()

# Count
result = await session.exec(
    select(func.count(Model.id))
    .where(Model.user_id == user_id)
)
count = result.one()

# Update
item.title = "New Title"
item.updated_at = datetime.now(timezone.utc)
await session.commit()
await session.refresh(item)

# Delete
await session.delete(item)
await session.commit()
```

## Best Practices

1. **UUID7 for primary keys**: Time-ordered for better indexing
2. **Always index user_id**: Critical for user isolation queries
3. **Timestamps on all tables**: created_at, updated_at
4. **Use migrations**: Never modify production schema directly
5. **Validate in schemas**: Keep models clean, validate in Pydantic
6. **Foreign keys with index**: Always index foreign key columns
