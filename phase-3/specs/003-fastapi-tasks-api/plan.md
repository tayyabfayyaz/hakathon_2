# Implementation Plan: FastAPI Tasks CRUD API

**Branch**: `003-fastapi-tasks-api` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fastapi-tasks-api/spec.md`

---

## Summary

Build a RESTful API for task management using FastAPI with Python 3.11+, SQLModel ORM, and Neon Serverless PostgreSQL. The API provides CRUD operations for tasks, authenticated via Better-Auth JWT Bearer tokens. **User isolation is a core feature** - each user has a completely separate and isolated account where they can only see and manage their own tasks.

---

## User Isolation Feature (Multi-Tenant Architecture)

### Overview

Every user operates in complete isolation. User_1 cannot see, access, or modify User_2's tasks under any circumstances. This is enforced at multiple layers:

### Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Request Flow                              │
├─────────────────────────────────────────────────────────────────┤
│  1. Request arrives with JWT Bearer token                        │
│  2. Token validated → user_id extracted from 'sub' claim         │
│  3. ALL database queries filter by user_id                       │
│  4. Response contains ONLY that user's data                      │
└─────────────────────────────────────────────────────────────────┘
```

### Isolation Enforcement Points

| Layer | Mechanism | File Location |
|-------|-----------|---------------|
| **Authentication** | JWT token validation extracts user_id | `app/api/deps.py:get_current_user()` |
| **Database Model** | `user_id` field indexed on Task table | `app/models/task.py:45-47` |
| **Query Filtering** | All queries include `WHERE user_id = ?` | `app/api/routes/tasks.py` |
| **404 Response** | Tasks not owned return 404 (not 403) | `app/api/routes/tasks.py` |

### Security Guarantees

1. **No Cross-User Data Leakage**: Queries always filter by authenticated user_id
2. **Information Hiding**: Accessing another user's task returns 404, not 403 (prevents enumeration)
3. **Token-Bound Identity**: User ID comes from validated JWT, not request parameters
4. **Index Optimization**: `user_id` is indexed for efficient per-user queries

### Verification Checklist

- [ ] All `/tasks` endpoints require authentication
- [ ] `user_id` is extracted from JWT token (not URL or body)
- [ ] CREATE: New tasks set `user_id` from current user
- [ ] READ (list): Query filters `WHERE user_id = current_user.id`
- [ ] READ (single): Query filters by both `id` AND `user_id`
- [ ] UPDATE: Query filters by both `id` AND `user_id`
- [ ] DELETE: Query filters by both `id` AND `user_id`
- [ ] 404 returned for tasks belonging to other users

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22+, asyncpg 0.30+, PyJWT 2.8+
**Storage**: Neon Serverless PostgreSQL (via pooled connection)
**Testing**: pytest 8.0+, pytest-asyncio 0.24+, httpx 0.28+
**Target Platform**: Linux server / Docker container
**Project Type**: Single API service (web backend)
**Performance Goals**: <200ms p95 reads, <500ms p95 writes, 100 concurrent users
**Constraints**: Token validation <50ms, health check <100ms
**Scale/Scope**: Single user's tasks (up to 1000 per user initially)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design | Notes |
|-----------|------------|-------------|-------|
| I. Data Integrity First | ✅ PASS | ✅ PASS | Atomic transactions via SQLModel, single source of truth |
| II. Offline-First Architecture | ⚠️ N/A | ⚠️ N/A | Backend API - offline handled by frontend |
| III. User Experience Excellence | ✅ PASS | ✅ PASS | <200ms response, clear errors, no learning curve |
| IV. Test-Driven Development | ✅ PASS | ✅ PASS | pytest + pytest-asyncio, >90% coverage target |
| V. Security & Privacy by Design | ✅ PASS | ✅ PASS | JWT auth, user isolation, TLS required |
| VI. Performance Budget | ✅ PASS | ✅ PASS | <200ms p95 reads, <500ms p95 writes |

**Gate Status**: ✅ PASSED - No violations requiring justification.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-fastapi-tasks-api/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technology research and decisions
├── data-model.md        # SQLModel definitions and schemas
├── quickstart.md        # Setup and run instructions
├── contracts/
│   └── api-schema.yaml  # OpenAPI 3.1 specification
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, CORS, routers
│   ├── config.py            # Pydantic settings (env vars)
│   ├── database.py          # Async engine, session factory
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task SQLModel (DB table)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (get_current_user, get_session)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── tasks.py     # Task CRUD endpoints
│   │       └── health.py    # Health check endpoint
│   └── schemas/
│       ├── __init__.py
│       ├── task.py          # TaskCreate, TaskUpdate, TaskResponse
│       └── error.py         # ErrorResponse schema
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures (async client, test DB)
│   ├── test_tasks.py        # Task endpoint tests
│   └── test_auth.py         # Authentication tests
├── alembic/
│   ├── env.py               # Alembic config
│   └── versions/            # Migration files
├── alembic.ini
├── pyproject.toml           # Dependencies (UV/Poetry)
├── .env.example             # Environment template
└── README.md                # Backend documentation
```

**Structure Decision**: Single API service pattern. The FastAPI backend is a standalone service that integrates with the existing Next.js frontend via HTTP/REST. No monorepo structure needed.

---

## Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ORM | SQLModel | Unified Pydantic + SQLAlchemy, FastAPI native |
| Async Driver | asyncpg | High performance async PostgreSQL |
| UUID Type | UUID7 | Time-ordered for efficient indexing |
| Auth | PyJWT + HTTPBearer | Standard JWT validation, FastAPI native |
| Testing | pytest-asyncio + httpx | Async test support, API client |
| Migrations | Alembic | SQLAlchemy-compatible, version controlled |

See [research.md](./research.md) for detailed analysis.

---

## Implementation Phases

### Phase 1: Project Setup
- Initialize Python project with UV/Poetry
- Install dependencies (FastAPI, SQLModel, asyncpg, etc.)
- Configure environment variables (database, secrets)
- Set up Alembic for migrations

### Phase 2: Core Infrastructure
- Implement config module (pydantic-settings)
- Set up async database connection
- Create Task model (SQLModel) with `user_id` field (indexed)
- Run initial migration

### Phase 3: Authentication & User Isolation
- Implement JWT token validation
- Create `get_current_user` dependency that extracts `user_id` from token
- Handle auth errors (401 responses)
- **CRITICAL**: Ensure user_id is NEVER accepted from request body/params

### Phase 4: CRUD Endpoints (with User Isolation)
- POST /tasks - Create task (set `user_id` from JWT)
- GET /tasks - List user's tasks (filter by `user_id`)
- GET /tasks/{id} - Get single task (filter by `id` AND `user_id`)
- PUT /tasks/{id} - Full update (filter by `id` AND `user_id`)
- PATCH /tasks/{id} - Partial update (filter by `id` AND `user_id`)
- DELETE /tasks/{id} - Remove task (filter by `id` AND `user_id`)
- **All queries MUST include `WHERE user_id = current_user.id`**

### Phase 5: Operations
- GET /health - Health check with DB status
- OpenAPI documentation (/docs)
- Request logging with correlation IDs

### Phase 6: Testing (including Isolation Tests)
- Unit tests for models and schemas
- Integration tests for endpoints
- Auth tests (valid/invalid tokens)
- **User isolation tests** (User A cannot see User B's tasks)
- Edge case tests

---

## User Isolation Implementation Details

### Task Creation (POST /tasks)
```python
# CORRECT: user_id from authenticated user
task = Task(
    text=task_data.text,
    user_id=current_user.id,  # From JWT, not request
    completed=False,
)
```

### Task Listing (GET /tasks)
```python
# CORRECT: Filter by user_id
statement = (
    select(Task)
    .where(Task.user_id == current_user.id)
    .order_by(Task.created_at.desc())
)
```

### Task Read/Update/Delete (GET/PUT/PATCH/DELETE /tasks/{id})
```python
# CORRECT: Filter by BOTH id AND user_id
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == current_user.id,  # Critical for isolation
)
# If not found: return 404 (not 403)
```

### Test Cases for Isolation
```python
# Test: User A cannot see User B's task
async def test_user_isolation():
    # Create task as User A
    task = create_task(user_id="user_a", text="User A's task")

    # Try to access as User B - MUST return 404
    response = await client.get(
        f"/tasks/{task.id}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    assert response.status_code == 404

# Test: User A cannot list User B's tasks
async def test_list_isolation():
    # Create tasks for both users
    create_task(user_id="user_a", text="A's task")
    create_task(user_id="user_b", text="B's task")

    # List as User A - MUST NOT include User B's task
    response = await client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    tasks = response.json()["tasks"]
    assert all(t["user_id"] == "user_a" for t in tasks)
```

---

## API Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /tasks | List all user tasks | Required |
| POST | /tasks | Create new task | Required |
| GET | /tasks/{id} | Get specific task | Required |
| PUT | /tasks/{id} | Full task update | Required |
| PATCH | /tasks/{id} | Partial task update | Required |
| DELETE | /tasks/{id} | Delete task | Required |
| GET | /health | Health check | None |
| GET | /docs | Swagger UI | None |

See [contracts/api-schema.yaml](./contracts/api-schema.yaml) for full OpenAPI spec.

---

## Data Model Summary

### Task Entity

| Field | Type | Description |
|-------|------|-------------|
| id | UUID (PK) | Time-ordered UUID7 |
| user_id | string | Owner ID from JWT |
| text | string(500) | Task description |
| completed | boolean | Completion status |
| order | integer | Display order |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last modified |
| completed_at | datetime? | When completed |

See [data-model.md](./data-model.md) for SQLModel definitions.

---

## Security Considerations

### User Isolation (Critical)

1. **Complete Account Separation**: Each user has isolated data space
2. **JWT-Based Identity**: User ID extracted from validated token, never from request
3. **Query-Level Enforcement**: Every database query filters by `user_id`
4. **Information Hiding**: Return 404 (not 403) for other users' tasks to prevent enumeration

### General Security

5. **Authentication**: All /tasks endpoints require valid Better-Auth JWT
6. **Authorization**: Users can only access their own tasks (user_id from JWT)
7. **Input Validation**: Pydantic validates all request bodies
8. **SQL Injection**: SQLModel/SQLAlchemy parameterizes all queries
9. **CORS**: Restrict to frontend origins only

### Chat Endpoint Isolation

The chat endpoints (`/{user_id}/chat`) also enforce user isolation:
- User ID in URL MUST match authenticated user's ID
- Returns 403 Forbidden if user_id mismatch
- Conversation history is per-user (isolated)

---

## Performance Targets

| Metric | Target | How Measured |
|--------|--------|--------------|
| Read latency (p95) | <200ms | Prometheus/logs |
| Write latency (p95) | <500ms | Prometheus/logs |
| Token validation | <50ms | Middleware timing |
| Health check | <100ms | Response time |
| Concurrent users | 100 | Load testing |

---

## Complexity Tracking

> No constitution violations requiring justification.

| Consideration | Status | Notes |
|---------------|--------|-------|
| Single project structure | ✅ Appropriate | API-only service |
| Direct SQLModel usage | ✅ Appropriate | No repository pattern needed |
| No caching layer | ✅ Appropriate | Database is fast enough |
| No rate limiting middleware | ⚠️ Future | Basic protection only |

---

## Next Steps

Run `/sp.tasks` to generate implementation tasks from this plan.

---

## Artifacts Generated

| File | Description |
|------|-------------|
| [spec.md](./spec.md) | Feature specification |
| [research.md](./research.md) | Technology decisions |
| [data-model.md](./data-model.md) | SQLModel definitions |
| [contracts/api-schema.yaml](./contracts/api-schema.yaml) | OpenAPI specification |
| [quickstart.md](./quickstart.md) | Setup instructions |
| plan.md | This implementation plan |
