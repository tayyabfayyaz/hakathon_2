# Research: FastAPI Tasks CRUD API

**Feature**: 003-fastapi-tasks-api
**Date**: 2025-12-31
**Status**: Complete

## Research Summary

This document captures technology decisions and best practices research for implementing the FastAPI Tasks CRUD API.

---

## 1. FastAPI + SQLModel + PostgreSQL Integration

### Decision
Use SQLModel with async support via `asyncpg` driver, combined with SQLAlchemy 2.0 async engine.

### Rationale
- SQLModel provides unified Pydantic + SQLAlchemy models, reducing boilerplate
- Fully type-annotated and integrates naturally with FastAPI
- Single model definition serves both database operations and request/response validation
- SQLAlchemy 2.0 provides mature async support

### Alternatives Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| SQLAlchemy + Pydantic separate | More flexibility | Duplicate model definitions, more boilerplate | Rejected |
| Tortoise ORM | Native async | Less mature, smaller ecosystem | Rejected |
| SQLModel (chosen) | Unified models, FastAPI native | Newer library | **Selected** |

### Implementation Details
```python
# Required packages
dependencies = [
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "asyncpg>=0.30.0",
    "pydantic-settings>=2.0.0",
    "uvicorn[standard]>=0.32.0",
]
```

**Sources**:
- [FastAPI SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel Async with FastAPI](https://daniel.feldroy.com/posts/til-2025-08-using-sqlmodel-asynchronously-with-fastapi-and-air-with-postgresql)

---

## 2. Neon Serverless PostgreSQL Connection

### Decision
Use Neon's pooled connection string with asyncpg driver and proper connection pool lifecycle management.

### Rationale
- Neon supports up to 10,000 concurrent connections via PgBouncer
- Built-in connection pooling masks cold starts
- Sub-100ms query times for simple operations after initial connection
- Native PostgreSQL compatibility with asyncpg

### Connection String Format
```
postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

For pooled connections (recommended):
```
postgresql+asyncpg://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
```

### Pool Lifecycle Management
```python
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create engine and session factory
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    app.state.async_session = async_session
    yield
    # Shutdown: dispose engine
    await engine.dispose()
```

### Best Practices
- Use pooled connection string (`-pooler` suffix)
- Implement proper session lifecycle with context managers
- Set reasonable pool size limits (default: 5-10 for serverless)
- Handle connection timeouts gracefully

**Sources**:
- [Neon Connection Pooling](https://neon.com/docs/connect/connection-pooling)
- [Neon FastAPI Async Guide](https://neon.com/guides/fastapi-async)

---

## 3. Better-Auth JWT Token Validation in Python

### Decision
Validate Better-Auth JWT tokens using PyJWT library with shared secret or public key verification.

### Rationale
- Better-Auth is a JavaScript/TypeScript authentication library
- FastAPI backend needs to validate tokens issued by Better-Auth frontend
- PyJWT provides standard JWT decoding and verification
- HTTPBearer class extracts tokens from Authorization header

### Token Validation Approach

Better-Auth's Bearer plugin adds tokens to Authorization header. The FastAPI backend validates these tokens:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,  # Shared secret with Better-Auth
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Configuration Requirements
- `BETTER_AUTH_SECRET`: Shared secret key between Next.js and FastAPI
- Same algorithm (HS256) must be configured on both sides
- Token expiration handled gracefully with clear error messages

### Security Best Practices
- Use strong, randomly generated secret keys (256+ bits)
- Store secrets in environment variables, never in code
- Set short token expiration times
- Always serve over HTTPS
- Validate all claims (sub, exp, iat)

**Sources**:
- [FastAPI JWT OAuth2 Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Better-Auth Bearer Plugin](https://www.better-auth.com/docs/plugins/bearer)

---

## 4. Project Structure Pattern

### Decision
Use single-project structure with clear separation of concerns.

### Rationale
- API-only project (frontend already exists)
- Simple enough for single service
- Clear separation: models, api, core, tests

### Recommended Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, routers
│   ├── config.py            # Pydantic settings
│   ├── database.py          # Engine, session factory
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # SQLModel Task model
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (auth, db session)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── tasks.py     # Task CRUD endpoints
│   │       └── health.py    # Health check endpoint
│   └── schemas/
│       ├── __init__.py
│       └── task.py          # Request/Response schemas
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures
│   ├── test_tasks.py        # Task endpoint tests
│   └── test_auth.py         # Auth tests
├── alembic/                  # Database migrations
├── pyproject.toml           # Dependencies (Poetry/UV)
├── .env.example             # Environment template
└── README.md
```

**Sources**:
- [FastAPI Project Structure Discussion](https://github.com/fastapi/fastapi/discussions/9936)
- [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template)

---

## 5. Testing Strategy

### Decision
Use pytest with pytest-asyncio for async test support, httpx for API testing.

### Rationale
- pytest is standard Python testing framework
- pytest-asyncio handles async fixtures and tests
- httpx provides async HTTP client for API testing
- SQLite in-memory for fast unit tests

### Test Dependencies
```python
test_dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "pytest-cov>=6.0.0",
]
```

### Test Configuration
```python
# conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def async_client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
```

---

## 6. UUID Strategy

### Decision
Use UUID7 for task IDs (time-ordered UUIDs).

### Rationale
- UUID7 combines timestamp with random data
- Time-ordered for efficient database indexing
- PostgreSQL has native UUID type support
- Better performance than UUID4 for B-tree indexes

### Implementation
```python
from uuid import UUID
import uuid6  # uuid6 package provides UUID7

def generate_task_id() -> UUID:
    return uuid6.uuid7()
```

---

## 7. Error Handling Pattern

### Decision
Use structured error responses with consistent format.

### Error Response Schema
```python
class ErrorResponse(BaseModel):
    error: str          # Error code (e.g., "VALIDATION_ERROR")
    message: str        # Human-readable message
    details: list[str] | None = None  # Additional context
```

### HTTP Status Code Mapping
| Scenario | Status Code | Error Code |
|----------|-------------|------------|
| Validation error | 422 | VALIDATION_ERROR |
| Unauthorized | 401 | UNAUTHORIZED |
| Not found | 404 | NOT_FOUND |
| Server error | 500 | INTERNAL_ERROR |
| Database error | 503 | SERVICE_UNAVAILABLE |

---

## Constitution Compliance Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Data Integrity First | ✅ PASS | Atomic ops via transactions, single source of truth |
| II. Offline-First Architecture | ⚠️ N/A | Backend API - offline handled by frontend |
| III. User Experience Excellence | ✅ PASS | <200ms response target, clear error messages |
| IV. Test-Driven Development | ✅ PASS | pytest + pytest-asyncio, coverage requirements |
| V. Security & Privacy by Design | ✅ PASS | JWT auth, user isolation, TLS required |
| VI. Performance Budget | ✅ PASS | <200ms p95 reads, <500ms p95 writes |

---

## Next Steps

1. Generate `data-model.md` with SQLModel definitions
2. Generate `contracts/api-schema.yaml` with OpenAPI spec
3. Generate `quickstart.md` with setup instructions
4. Complete `plan.md` with all sections
