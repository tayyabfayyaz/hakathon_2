# Implementation Plan: TodoList Pro Core Features

**Branch**: `001-todo-crud-features` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-todo-crud-features/spec.md`

## Summary

TodoList Pro is a full-stack web application enabling authenticated users to manage personal todo items with CRUD operations, status toggling, search, and filtering capabilities. The implementation uses Next.js 14 for the frontend and FastAPI with SQLModel for the backend, persisting data in Neon DB (PostgreSQL).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Pydantic v2, Next.js 14, React 18
**Storage**: Neon DB (PostgreSQL) with SQLModel ORM
**Testing**: pytest + httpx (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Web browsers (responsive design)
**Project Type**: Web application (frontend + backend separation)
**Performance Goals**: <3s page load, <500ms status toggle, <1s search results
**Constraints**: 100 concurrent users, 24h session expiry
**Scale/Scope**: MVP for single-user todo management, ~5 screens

## Constitution Check

*GATE: Must pass before implementation. All gates verified against Constitution v1.0.0*

| Principle | Gate | Status | Notes |
|-----------|------|--------|-------|
| I. Input Validation | API-level validation for all inputs | PASS | Pydantic v2 schemas validate all requests |
| I. Input Validation | String trimming, length validation, XSS sanitization | PASS | TodoCreate/TodoUpdate schemas enforce constraints |
| I. Input Validation | Structured error responses with field details | PASS | ErrorResponse schema in OpenAPI contract |
| II. API Design | REST conventions with proper HTTP methods | PASS | GET/POST/PATCH/DELETE per contract |
| II. API Design | OpenAPI documentation | PASS | contracts/openapi.yaml complete |
| II. API Design | API versioning via URL path | PASS | /api/v1/ prefix |
| II. API Design | Pagination for 20+ items | PASS | Cursor-based pagination in GET /todos |
| III. Data Integrity | SQLModel with type annotations | PASS | data-model.md defines all models |
| III. Data Integrity | Foreign key constraints | PASS | user_id FK with ON DELETE CASCADE |
| III. Data Integrity | Auto-managed timestamps | PASS | created_at, updated_at with triggers |
| III. Data Integrity | Soft deletes for todos | PASS | deleted_at field implemented |
| IV. Error Handling | Structured JSON error format | PASS | error_code, message, details.fields |
| IV. Error Handling | Appropriate HTTP status codes | PASS | 400, 401, 404, 409, 500 mapped |
| IV. Error Handling | No stack traces to client | PASS | Production error handler planned |
| V. Testing | Critical path tests | PLANNED | CRUD, validation, auth tests required |
| VI. Simplicity | Minimal dependencies | PASS | Using stdlib where possible |
| VI. Simplicity | No premature abstractions | PASS | Direct service pattern |

**Gate Result**: PASS - All constitution requirements satisfied or planned.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-crud-features/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/
│   └── openapi.yaml     # API contract
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection (auth, db)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Main router
│   │       ├── auth.py          # Auth endpoints
│   │       └── todos.py         # Todo endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings from env
│   │   ├── security.py          # JWT, password hashing
│   │   └── database.py          # DB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User SQLModel
│   │   └── todo.py              # Todo SQLModel
│   └── services/
│       ├── __init__.py
│       ├── user_service.py      # User business logic
│       └── todo_service.py      # Todo business logic
├── tests/
│   ├── conftest.py              # Fixtures
│   ├── test_auth.py             # Auth tests
│   └── test_todos.py            # Todo tests
├── alembic/                     # Migrations
├── main.py                      # FastAPI app entry
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Home (redirect)
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── register/
│   │   │   └── page.tsx         # Register page
│   │   └── todos/
│   │       └── page.tsx         # Todo list page
│   ├── components/
│   │   ├── ui/                  # Base UI components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   └── todos/
│   │       ├── TodoList.tsx
│   │       ├── TodoItem.tsx
│   │       ├── TodoForm.tsx
│   │       ├── SearchBar.tsx
│   │       └── FilterTabs.tsx
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── auth.ts              # Auth utilities
│   │   └── validation.ts        # Client-side validation
│   └── hooks/
│       ├── useTodos.ts          # Todo state management
│       └── useAuth.ts           # Auth state management
├── tests/
│   └── components/
├── package.json
├── next.config.js
├── tailwind.config.js
└── .env.example
```

**Structure Decision**: Web application structure (Option 2) selected due to separate frontend (Next.js) and backend (FastAPI) requirements per constitution technology stack.

## Implementation Phases

### Phase 1: Project Setup & Infrastructure

**Goal**: Establish project foundation with database and basic configuration

**Tasks**:
1. Initialize backend Python project with FastAPI
2. Initialize frontend Next.js project with TypeScript
3. Configure Neon DB connection
4. Set up Alembic for migrations
5. Create initial database schema (users, todos tables)
6. Configure environment variables handling
7. Set up CORS configuration

**Deliverables**:
- Working backend that starts and connects to DB
- Working frontend that loads
- Database with tables created

### Phase 2: Authentication (User Story 1 - P1)

**Goal**: Enable user registration, login, and session management

**Backend Tasks**:
1. Implement User SQLModel
2. Implement password hashing with bcrypt
3. Implement JWT token generation
4. Create POST /auth/register endpoint
5. Create POST /auth/login endpoint
6. Create POST /auth/logout endpoint
7. Create GET /auth/me endpoint
8. Implement auth dependency for protected routes

**Frontend Tasks**:
1. Create LoginForm component
2. Create RegisterForm component
3. Create login page
4. Create register page
5. Implement auth state management (useAuth hook)
6. Add route protection middleware
7. Add logout functionality

**Tests Required** (Constitution V):
- Registration with valid/invalid data
- Login with correct/incorrect credentials
- Protected route access without auth

### Phase 3: Todo CRUD (User Stories 2-4 - P1/P2)

**Goal**: Enable creating, reading, updating, and deleting todos

**Backend Tasks**:
1. Implement Todo SQLModel
2. Create POST /todos endpoint (create)
3. Create GET /todos endpoint (list with pagination)
4. Create GET /todos/{id} endpoint (read single)
5. Create PATCH /todos/{id} endpoint (update)
6. Create DELETE /todos/{id} endpoint (soft delete)
7. Implement user ownership validation

**Frontend Tasks**:
1. Create TodoList component
2. Create TodoItem component
3. Create TodoForm component (add new)
4. Create EditTodoForm component
5. Implement useTodos hook for state
6. Add delete confirmation dialog
7. Implement optimistic updates

**Tests Required** (Constitution V):
- Create todo with valid/invalid data
- List todos (empty, with items)
- Update todo (valid changes, invalid changes)
- Delete todo
- Ownership validation (can't access other's todos)

### Phase 4: Status Toggle (User Story 5 - P2)

**Goal**: Enable marking todos as completed/remaining

**Backend Tasks**:
1. Create POST /todos/{id}/toggle endpoint
2. Ensure status persists correctly

**Frontend Tasks**:
1. Add toggle checkbox/button to TodoItem
2. Implement visual distinction (strikethrough)
3. Optimistic UI update on toggle

**Tests Required**:
- Toggle from remaining to completed
- Toggle from completed to remaining
- Status persists after refresh

### Phase 5: Search & Filter (User Stories 6-7 - P3)

**Goal**: Enable searching and filtering todos

**Backend Tasks**:
1. Add search query parameter to GET /todos
2. Implement ILIKE search on title/description
3. Add status filter parameter
4. Implement combined search + filter

**Frontend Tasks**:
1. Create SearchBar component
2. Create FilterTabs component (All/Remaining/Completed)
3. Implement debounced search (300ms)
4. Connect filters to API calls
5. Show "no results" message

**Tests Required**:
- Search returns matching items
- Search is case-insensitive
- Filter by status works
- Combined search + filter works

### Phase 6: Polish & Error Handling

**Goal**: Production-ready error handling and UX polish

**Tasks**:
1. Implement global error boundary (frontend)
2. Add loading states
3. Add empty state messages
4. Implement toast notifications
5. Add form validation feedback
6. Test all error scenarios
7. Performance optimization

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Neon DB connection issues | HIGH | Fallback to local PostgreSQL for dev |
| JWT token expiry handling | MEDIUM | Implement refresh token or re-login prompt |
| Search performance at scale | LOW | Add database index, consider full-text search later |
| CORS misconfiguration | MEDIUM | Test cross-origin requests early |

## Dependencies Graph

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Auth) ────────────────┐
    │                          │
    ▼                          │
Phase 3 (CRUD) ◄───────────────┤
    │                          │
    ▼                          │
Phase 4 (Toggle) ◄─────────────┤
    │                          │
    ▼                          │
Phase 5 (Search/Filter) ◄──────┘
    │
    ▼
Phase 6 (Polish)
```

## Success Validation

After implementation, validate against spec success criteria:

- [ ] SC-001: Registration under 1 minute
- [ ] SC-002: Add todo under 5 seconds
- [ ] SC-003: Toggle reflects in 500ms
- [ ] SC-004: Search results in 1 second
- [ ] SC-005: 95% first-todo success rate
- [ ] SC-006: 100 concurrent users supported
- [ ] SC-007: Find todo in 50+ items under 10s
- [ ] SC-008: Page load under 3 seconds
- [ ] SC-009: Data persists correctly
- [ ] SC-010: Filter under 100ms

## Next Steps

1. Run `/sp.tasks` to generate detailed task list
2. Begin Phase 1 implementation
3. Review with stakeholders after Phase 2 (auth MVP)
