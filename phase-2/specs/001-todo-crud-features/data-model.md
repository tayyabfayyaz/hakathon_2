# Data Model: TodoList Pro

**Branch**: `001-todo-crud-features`
**Date**: 2025-12-24
**Database**: Neon DB (PostgreSQL)

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              users                   │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: VARCHAR(255) UNIQUE NOT NULL │
│ password_hash: VARCHAR(255) NOT NULL│
│ created_at: TIMESTAMP NOT NULL      │
│ updated_at: TIMESTAMP NOT NULL      │
│ last_login_at: TIMESTAMP            │
└─────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────┐
│              todos                   │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ user_id: UUID (FK) NOT NULL         │
│ title: VARCHAR(200) NOT NULL        │
│ description: TEXT                    │
│ is_completed: BOOLEAN DEFAULT FALSE │
│ created_at: TIMESTAMP NOT NULL      │
│ updated_at: TIMESTAMP NOT NULL      │
│ deleted_at: TIMESTAMP               │
└─────────────────────────────────────┘
```

## Entity Definitions

### User

Represents a registered user of the application.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique identifier (UUIDv4) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| `created_at` | TIMESTAMP | NOT NULL, auto | Account creation time (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL, auto | Last profile update time (UTC) |
| `last_login_at` | TIMESTAMP | NULL | Last successful login time (UTC) |

**Validation Rules** (Constitution I compliance):
- `email`: Valid email format, trimmed, max 255 chars
- `password`: Min 8 characters (stored as hash, never plain text)

**Indexes**:
- `users_email_idx` on `email` (unique)

### Todo

Represents a task item owned by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, auto-generated | Unique identifier (UUIDv4) |
| `user_id` | UUID | FK → users.id, NOT NULL | Owner of this todo |
| `title` | VARCHAR(200) | NOT NULL | Task title (1-200 chars) |
| `description` | TEXT | NULL | Optional task description (0-2000 chars) |
| `is_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, auto | Creation time (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL, auto | Last modification time (UTC) |
| `deleted_at` | TIMESTAMP | NULL | Soft delete timestamp (NULL = active) |

**Validation Rules** (Constitution I compliance):
- `title`: 1-200 characters, trimmed, not whitespace-only
- `description`: 0-2000 characters, trimmed
- `is_completed`: Explicit boolean (true/false only)

**Indexes**:
- `todos_user_id_idx` on `user_id`
- `todos_user_created_idx` on `(user_id, created_at DESC)` for pagination
- `todos_user_completed_idx` on `(user_id, is_completed)` for filtering

**Foreign Key**:
- `user_id` → `users.id` ON DELETE CASCADE

## State Transitions

### Todo Status

```
                  ┌───────────────┐
                  │   REMAINING   │ (is_completed = false)
                  └───────┬───────┘
                          │
           toggle status  │  toggle status
                          ▼
                  ┌───────────────┐
                  │   COMPLETED   │ (is_completed = true)
                  └───────────────┘
```

**Business Rules**:
- New todos are created with `is_completed = false`
- Status can be toggled in either direction at any time
- No restrictions on toggling frequency

### Todo Lifecycle

```
┌─────────┐     create      ┌─────────┐
│  (new)  │ ───────────────▶│  ACTIVE │
└─────────┘                 └────┬────┘
                                 │
                    soft delete  │  restore (future)
                                 ▼
                            ┌─────────┐
                            │ DELETED │ (deleted_at NOT NULL)
                            └─────────┘
```

**Business Rules**:
- Active todos have `deleted_at = NULL`
- Soft-deleted todos have `deleted_at` set to deletion timestamp
- Query filters exclude soft-deleted items by default
- Permanent deletion is out of scope for MVP

## SQLModel Definitions

```python
# backend/src/models/user.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    email: str = Field(max_length=255, index=True, unique=True)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

class UserCreate(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)

class UserRead(SQLModel):
    id: UUID
    email: str
    created_at: datetime
```

```python
# backend/src/models/todo.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class Todo(TodoBase, table=True):
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

class TodoCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class TodoUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)

class TodoRead(SQLModel):
    id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
```

## Database Migrations

### Initial Migration (001_initial_schema.sql)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX users_email_idx ON users(email);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX todos_user_id_idx ON todos(user_id);
CREATE INDEX todos_user_created_idx ON todos(user_id, created_at DESC);
CREATE INDEX todos_user_completed_idx ON todos(user_id, is_completed);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Constraints Summary

| Entity | Field | Constraint | Source |
|--------|-------|------------|--------|
| User | email | Unique, valid format | FR-001, FR-002 |
| User | password | Min 8 chars | FR-003 |
| User | password_hash | Never plain text | FR-004 |
| Todo | title | 1-200 chars, not empty | FR-011, Constitution I |
| Todo | description | 0-2000 chars | FR-012, Constitution I |
| Todo | is_completed | Boolean only | Constitution I |
| Todo | user_id | FK to owner | FR-016 |
| Todo | timestamps | Auto-managed | FR-027, FR-028, Constitution III |
