# Implementation Plan: FastAPI Tasks CRUD API

**Branch**: `003-fastapi-tasks-api` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fastapi-tasks-api/spec.md`

---

## Summary

Build a RESTful API for task management using FastAPI with Python 3.11+, SQLModel ORM, and Neon Serverless PostgreSQL. The API provides CRUD operations for tasks, authenticated via Better-Auth JWT Bearer tokens. User isolation ensures each user can only access their own tasks.

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
- Create Task model (SQLModel)
- Run initial migration

### Phase 3: Authentication
- Implement JWT token validation
- Create `get_current_user` dependency
- Handle auth errors (401 responses)

### Phase 4: CRUD Endpoints
- POST /tasks - Create task
- GET /tasks - List user's tasks
- GET /tasks/{id} - Get single task
- PUT /tasks/{id} - Full update
- PATCH /tasks/{id} - Partial update
- DELETE /tasks/{id} - Remove task

### Phase 5: Operations
- GET /health - Health check with DB status
- OpenAPI documentation (/docs)
- Request logging with correlation IDs

### Phase 6: Testing
- Unit tests for models and schemas
- Integration tests for endpoints
- Auth tests (valid/invalid tokens)
- Edge case tests

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

1. **Authentication**: All /tasks endpoints require valid Better-Auth JWT
2. **Authorization**: Users can only access their own tasks (user_id from JWT)
3. **Information Hiding**: Return 404 (not 403) for other users' tasks
4. **Input Validation**: Pydantic validates all request bodies
5. **SQL Injection**: SQLModel/SQLAlchemy parameterizes all queries
6. **CORS**: Restrict to frontend origins only

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
