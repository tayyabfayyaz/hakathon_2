# Data Model: FastAPI Tasks CRUD API

**Feature**: 003-fastapi-tasks-api
**Date**: 2025-12-31
**ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          Task                               │
├─────────────────────────────────────────────────────────────┤
│ id: UUID (PK)           │ Unique identifier (UUID7)        │
│ user_id: str            │ Owner ID (from JWT, not FK)      │
│ text: str               │ Task description (1-500 chars)   │
│ completed: bool         │ Completion status (default: F)   │
│ created_at: datetime    │ Creation timestamp (UTC)         │
│ updated_at: datetime    │ Last modification (UTC)          │
│ completed_at: datetime? │ When marked complete (nullable)  │
│ order: int              │ Display order (default: 0)       │
└─────────────────────────────────────────────────────────────┘
         │
         │ user_id references external
         │ Better-Auth user (not stored locally)
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     User (External)                         │
├─────────────────────────────────────────────────────────────┤
│ Managed by Better-Auth on Next.js frontend                  │
│ User ID extracted from JWT token 'sub' claim                │
└─────────────────────────────────────────────────────────────┘
```

---

## SQLModel Definitions

### Task Model (Database Table)

```python
# app/models/task.py

from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid6

def generate_uuid7() -> UUID:
    """Generate a time-ordered UUID7."""
    return uuid6.uuid7()

class TaskBase(SQLModel):
    """Base task fields shared by all task schemas."""
    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task description text"
    )
    completed: bool = Field(
        default=False,
        description="Whether the task is completed"
    )

class Task(TaskBase, table=True):
    """Task database model."""
    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        description="Unique task identifier"
    )
    user_id: str = Field(
        index=True,
        description="Owner user ID from JWT token"
    )
    order: int = Field(
        default=0,
        description="Display order for sorting"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="When the task was last modified"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When the task was marked complete"
    )
```

---

## Request/Response Schemas

### Task Create Schema

```python
# app/schemas/task.py

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task description text",
        examples=["Buy groceries", "Complete project report"]
    )

class TaskUpdate(BaseModel):
    """Schema for full task update (PUT)."""
    text: str = Field(
        min_length=1,
        max_length=500,
        description="Task description text"
    )
    completed: bool = Field(
        description="Whether the task is completed"
    )

class TaskPatch(BaseModel):
    """Schema for partial task update (PATCH)."""
    text: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Task description text"
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Whether the task is completed"
    )

class TaskResponse(BaseModel):
    """Schema for task in API responses."""
    id: UUID
    text: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""
    tasks: list[TaskResponse]
    count: int
```

---

## Error Response Schemas

```python
# app/schemas/error.py

from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(
        description="Error code identifier",
        examples=["VALIDATION_ERROR", "UNAUTHORIZED", "NOT_FOUND"]
    )
    message: str = Field(
        description="Human-readable error message"
    )
    details: Optional[list[str]] = Field(
        default=None,
        description="Additional error details"
    )

class ValidationErrorDetail(BaseModel):
    """Validation error detail for 422 responses."""
    loc: list[str]
    msg: str
    type: str
```

---

## Health Check Schema

```python
# app/schemas/health.py

from pydantic import BaseModel
from typing import Literal

class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "unhealthy"]
    database: Literal["connected", "disconnected"]
    version: str
```

---

## Database Indexes

| Index Name | Table | Columns | Type | Purpose |
|------------|-------|---------|------|---------|
| `pk_tasks` | tasks | id | Primary | Unique task lookup |
| `ix_tasks_user_id` | tasks | user_id | B-tree | Filter tasks by user |
| `ix_tasks_user_completed` | tasks | (user_id, completed) | Composite | Filter user's pending/completed |
| `ix_tasks_user_created` | tasks | (user_id, created_at) | Composite | Sort user's tasks by date |

---

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| text | 1-500 characters | "Task text must be between 1 and 500 characters" |
| text | Not empty/whitespace only | "Task text cannot be empty" |
| completed | Boolean value | "Completed must be a boolean" |
| id (path) | Valid UUID format | "Invalid task ID format" |

---

## State Transitions

### Task Completion State Machine

```
┌──────────────┐                    ┌──────────────┐
│  INCOMPLETE  │ ───────────────▶   │   COMPLETE   │
│              │   completed=true    │              │
│ completed=F  │   completed_at=now  │ completed=T  │
│ completed_at │ ◀───────────────── │ completed_at │
│    =null     │   completed=false   │   =datetime  │
└──────────────┘   completed_at=null └──────────────┘
```

### Timestamp Behavior

| Event | created_at | updated_at | completed_at |
|-------|------------|------------|--------------|
| Create task | Set to now | Set to now | null |
| Update text | Unchanged | Set to now | Unchanged |
| Mark complete | Unchanged | Set to now | Set to now |
| Mark incomplete | Unchanged | Set to now | Set to null |
| Delete task | N/A | N/A | N/A |

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# alembic/versions/001_create_tasks_table.py

def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('text', sa.String(500), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Composite indexes
    op.create_index('ix_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('ix_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_table('tasks')
```
