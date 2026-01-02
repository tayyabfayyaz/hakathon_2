# Quickstart: FastAPI Tasks CRUD API

**Feature**: 003-fastapi-tasks-api
**Date**: 2025-12-31

---

## Prerequisites

- Python 3.11+
- Neon PostgreSQL account (https://neon.tech)
- Better-Auth configured on frontend (shared secret)

---

## 1. Project Setup

### Create Project Directory

```bash
mkdir backend
cd backend
```

### Initialize with UV (Recommended)

```bash
# Install UV if not already installed
pip install uv

# Create virtual environment and pyproject.toml
uv init --python 3.11
```

### Install Dependencies

```bash
uv add fastapi[standard] sqlmodel asyncpg pydantic-settings uuid6 pyjwt alembic
uv add --dev pytest pytest-asyncio httpx pytest-cov
```

Or with pip:

```bash
pip install fastapi[standard] sqlmodel asyncpg pydantic-settings uuid6 pyjwt alembic
pip install pytest pytest-asyncio httpx pytest-cov
```

---

## 2. Environment Configuration

### Create `.env` file

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=your-shared-secret-with-frontend
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### Create `.env.example`

```bash
# .env.example (for version control)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/todolist
BETTER_AUTH_SECRET=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

---

## 3. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings with pydantic-settings
│   ├── database.py          # Async engine and session
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task SQLModel
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (auth, db)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── tasks.py     # CRUD endpoints
│   │       └── health.py    # Health check
│   └── schemas/
│       ├── __init__.py
│       ├── task.py          # Request/Response schemas
│       └── error.py         # Error response schemas
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   └── test_tasks.py        # Task endpoint tests
├── alembic/                  # Migrations
├── alembic.ini
├── pyproject.toml
├── .env
├── .env.example
└── README.md
```

---

## 4. Configuration Module

### `app/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    better_auth_secret: str
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 5. Database Setup

### `app/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session():
    async with async_session() as session:
        yield session
```

---

## 6. Run Development Server

```bash
# From backend directory
uvicorn app.main:app --reload --port 8000
```

### Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

## 7. Database Migrations

### Initialize Alembic

```bash
alembic init alembic
```

### Configure `alembic/env.py`

```python
# Add at top of file
from app.models.task import Task
from app.database import engine
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata

# Update run_migrations_online() to use async
```

### Create Initial Migration

```bash
alembic revision --autogenerate -m "create tasks table"
alembic upgrade head
```

---

## 8. Test the API

### Create a Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Buy groceries"}'
```

### List Tasks

```bash
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Toggle Completion

```bash
curl -X PATCH http://localhost:8000/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 9. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v
```

---

## 10. Frontend Integration

### Configure CORS

The FastAPI app allows requests from origins specified in `CORS_ORIGINS` environment variable.

### Get Bearer Token

On the Next.js frontend with Better-Auth:

```typescript
// After sign-in, get the session token
const authToken = ctx.response.headers.get("set-auth-token");
localStorage.setItem("bearer_token", authToken);

// Include in API requests
fetch("http://localhost:8000/tasks", {
  headers: {
    "Authorization": `Bearer ${localStorage.getItem("bearer_token")}`
  }
});
```

---

## Troubleshooting

### Connection Errors

1. Verify Neon database URL includes `-pooler` suffix
2. Check `sslmode=require` is in connection string
3. Ensure IP is allowed in Neon dashboard

### Auth Errors

1. Verify `BETTER_AUTH_SECRET` matches frontend config
2. Check token is not expired
3. Confirm token format is `Bearer <token>`

### CORS Errors

1. Add frontend origin to `CORS_ORIGINS`
2. Restart server after changing `.env`
