---
name: backend
description: Backend development for FastAPI + SQLModel + PostgreSQL application. Use when working on API endpoints, database models, services, or any backend code. Covers async patterns, Kafka, WebSockets, and MCP tools.
argument-hint: "[task]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Backend Development Guide

This skill provides guidance for developing the TodoList Pro FastAPI backend.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115+ | Async web framework |
| SQLModel | Latest | ORM (SQLAlchemy + Pydantic) |
| PostgreSQL | 15+ | Database |
| AsyncPG | Latest | Async PostgreSQL driver |
| Pydantic | v2 | Validation & settings |
| PyJWT | Latest | JWT authentication |
| aiokafka | Latest | Async Kafka client |
| OpenAI SDK | Latest | Gemini AI integration |
| FastMCP | Latest | MCP tool protocol |
| Alembic | Latest | Database migrations |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app with lifespan
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLModel session factory
│   ├── api/
│   │   ├── deps.py          # Auth & session dependencies
│   │   └── routes/
│   │       ├── tasks.py     # Task CRUD
│   │       ├── chat.py      # AI chat
│   │       ├── notifications.py
│   │       ├── websocket.py
│   │       └── health.py
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── mcp/                 # MCP tools for AI
├── alembic/                 # Migrations
├── tests/                   # pytest tests
└── pyproject.toml
```

## Key Patterns

### Async-First Design

```python
# All I/O operations use async/await
async def get_tasks(session: AsyncSession, user_id: str) -> list[Task]:
    result = await session.exec(
        select(Task).where(Task.user_id == user_id)
    )
    return result.all()
```

### Dependency Injection

```python
from typing import Annotated
from fastapi import Depends

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.get("/tasks")
async def list_tasks(
    current_user: CurrentUserDep,
    session: SessionDep
) -> list[TaskResponse]:
    ...
```

### User Isolation

```python
# Always filter by user_id
tasks = await session.exec(
    select(Task)
    .where(Task.user_id == current_user.id)
    .order_by(Task.created_at.desc())
)
```

## Development Commands

```bash
cd backend

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn app.main:app --reload --port 8000

# Run migrations
alembic upgrade head

# Run tests
pytest -v

# Create migration
alembic revision --autogenerate -m "description"
```

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
BETTER_AUTH_SECRET=your-32-char-secret
GEMINI_API_KEY=your-api-key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_ENABLED=true
CORS_ORIGINS=http://localhost:3000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Related Skills

- **backend-api**: Create API endpoints
- **backend-model**: Database models
- **backend-auth**: Authentication
- **backend-service**: Business logic
- **backend-kafka**: Event streaming
- **backend-websocket**: Real-time features
- **backend-mcp**: AI tool integration
