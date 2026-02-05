---
name: backend-auth
description: JWT authentication with Better-Auth integration, user isolation, and protected routes. Use when implementing authentication, authorization, or user access control.
argument-hint: "[action]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Authentication & Authorization

Implement authentication following the TodoList Pro patterns with Better-Auth JWT.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│ Better-Auth  │────▶│  PostgreSQL │
│  (Next.js)  │     │  (Sessions)  │     │  (Users)    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       │ Bearer Token      │ Shared Secret
       ▼                   ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│   (JWT Validation with same secret) │
└─────────────────────────────────────┘
```

## JWT Validation Dependency

```python
# app/api/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config import get_settings

security = HTTPBearer(auto_error=False)
settings = get_settings()


class CurrentUser:
    """Authenticated user from JWT token."""

    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name

    def __repr__(self) -> str:
        return f"CurrentUser(id={self.id}, email={self.email})"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Extract and validate JWT token from Authorization header.

    Token format: Bearer <jwt_token>

    JWT payload expected:
    {
        "sub": "user_id",
        "email": "user@example.com",
        "name": "User Name",
        "iat": 1234567890,
        "exp": 1234567890
    }
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        return CurrentUser(
            id=user_id,
            email=payload.get("email", ""),
            name=payload.get("name", ""),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


# Type alias for dependency injection
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
```

## Using Authentication in Routes

```python
from fastapi import APIRouter
from app.api.deps import CurrentUserDep, SessionDep

router = APIRouter()


@router.get("/tasks")
async def list_tasks(
    current_user: CurrentUserDep,  # Automatically validates JWT
    session: SessionDep,
) -> list[TaskResponse]:
    """List tasks for authenticated user."""
    # current_user.id is guaranteed to be valid here
    result = await session.exec(
        select(Task)
        .where(Task.user_id == current_user.id)
    )
    return result.all()
```

## User Isolation Pattern

```python
# ALWAYS filter by user_id in queries
async def get_user_tasks(session: AsyncSession, user_id: str) -> list[Task]:
    result = await session.exec(
        select(Task)
        .where(Task.user_id == user_id)  # Critical for isolation
        .order_by(Task.created_at.desc())
    )
    return result.all()


# Validate ownership before returning resource
@router.get("/tasks/{task_id}")
async def get_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TaskResponse:
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # CRITICAL: Check ownership
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task


# Validate ownership before mutation
@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    await session.delete(task)
    await session.commit()
```

## Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Shared secret with Better-Auth frontend
    better_auth_secret: str

    # Database
    database_url: str

    # CORS origins
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Environment Variables

```env
# .env
BETTER_AUTH_SECRET=your-32-character-secret-shared-with-frontend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

## WebSocket Authentication

```python
# app/api/routes/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import jwt

from app.config import get_settings

settings = get_settings()


async def authenticate_websocket(websocket: WebSocket) -> str | None:
    """Authenticate WebSocket connection via query parameter."""
    token = websocket.query_params.get("token")

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None


@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    user_id = await authenticate_websocket(websocket)

    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    # ... handle connection
```

## Testing Authentication

```python
# tests/conftest.py
import pytest
import jwt
from datetime import datetime, timedelta

from app.config import get_settings

settings = get_settings()


def create_test_token(user_id: str, email: str = "test@example.com") -> str:
    """Create a valid JWT for testing."""
    payload = {
        "sub": user_id,
        "email": email,
        "name": "Test User",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")


@pytest.fixture
def auth_headers(user_id: str = "test-user-123") -> dict:
    token = create_test_token(user_id)
    return {"Authorization": f"Bearer {token}"}


# tests/test_auth.py
async def test_unauthorized_without_token(client):
    response = await client.get("/tasks")
    assert response.status_code == 401


async def test_authorized_with_token(client, auth_headers):
    response = await client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200


async def test_user_isolation(client):
    # User A creates task
    headers_a = {"Authorization": f"Bearer {create_test_token('user-a')}"}
    response = await client.post("/tasks", json={"text": "Task A"}, headers=headers_a)
    task_id = response.json()["id"]

    # User B cannot access it
    headers_b = {"Authorization": f"Bearer {create_test_token('user-b')}"}
    response = await client.get(f"/tasks/{task_id}", headers=headers_b)
    assert response.status_code == 403
```

## Best Practices

1. **Shared secret**: Same `BETTER_AUTH_SECRET` in frontend and backend
2. **Always validate ownership**: Check `user_id` before returning/mutating
3. **Use type aliases**: `CurrentUserDep` for clean dependency injection
4. **Filter at query level**: Always include `user_id` in WHERE clauses
5. **Return 403 for ownership failures**: Not 404 (don't leak existence)
6. **Test isolation**: Comprehensive tests for cross-user access
