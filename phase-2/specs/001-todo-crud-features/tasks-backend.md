# Backend Tasks: TodoList Pro

**Feature**: 001-todo-crud-features
**Input**: Design documents from `specs/001-todo-crud-features/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml
**Technology**: Python 3.11+, FastAPI, SQLModel, Pydantic v2, Neon DB (PostgreSQL)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Backend Setup

**Goal**: Initialize FastAPI project with database connection

- [x] T001 Create backend directory structure per plan.md at `backend/`
- [x] T002 Create requirements.txt with FastAPI, SQLModel, Pydantic, uvicorn, python-jose, passlib, bcrypt, httpx, pytest, alembic at `backend/requirements.txt`
- [x] T003 [P] Create .env.example with DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, CORS_ORIGINS at `backend/.env.example`
- [x] T004 [P] Create config.py with Settings class using pydantic-settings at `backend/src/core/config.py`
- [x] T005 Create database.py with async engine and session maker for Neon DB at `backend/src/core/database.py`
- [x] T006 [P] Create __init__.py files for all packages at `backend/src/` subdirectories
- [x] T007 Create main.py with FastAPI app, CORS middleware, and router includes at `backend/main.py`
- [x] T008 Initialize Alembic with async PostgreSQL configuration at `backend/alembic/`
- [x] T009 Create initial migration with users and todos tables at `backend/alembic/versions/001_initial_schema.py`

**Checkpoint**: Backend starts with `uvicorn main:app --reload` and connects to database

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Core infrastructure required before any user story

- [x] T010 Create base error response schemas (ErrorResponse, ValidationError) at `backend/src/models/errors.py`
- [x] T011 Create exception handlers for validation and HTTP errors at `backend/src/api/exceptions.py`
- [x] T012 [P] Create security.py with password hashing (bcrypt) and JWT utilities at `backend/src/core/security.py`
- [x] T013 Create deps.py with get_db dependency and get_current_user stub at `backend/src/api/deps.py`
- [x] T014 Create v1 router.py that includes auth and todos routers at `backend/src/api/v1/router.py`
- [x] T015 Create test conftest.py with test database fixtures and test client at `backend/tests/conftest.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1)

**Goal**: Enable user registration, login, logout, and session management

**Independent Test**: Register account, logout, login again - all succeed

### Implementation for User Story 1

- [x] T016 [P] [US1] Create User SQLModel with UserBase, User, UserCreate, UserRead schemas at `backend/src/models/user.py`
- [x] T017 [US1] Create user_service.py with create_user, get_user_by_email, authenticate_user functions at `backend/src/services/user_service.py`
- [x] T018 [US1] Implement POST /auth/register endpoint with email validation and password hashing at `backend/src/api/v1/auth.py`
- [x] T019 [US1] Implement POST /auth/login endpoint with JWT token in HTTP-only cookie at `backend/src/api/v1/auth.py`
- [x] T020 [US1] Implement POST /auth/logout endpoint that clears auth cookie at `backend/src/api/v1/auth.py`
- [x] T021 [US1] Implement GET /auth/me endpoint returning current user info at `backend/src/api/v1/auth.py`
- [x] T022 [US1] Update deps.py get_current_user to decode JWT and fetch user at `backend/src/api/deps.py`
- [x] T023 [US1] Add auth router to v1 router.py at `backend/src/api/v1/router.py`

### Tests for User Story 1

- [x] T024 [P] [US1] Test registration with valid email/password at `backend/tests/test_auth.py`
- [x] T025 [P] [US1] Test registration with invalid email format at `backend/tests/test_auth.py`
- [x] T026 [P] [US1] Test registration with duplicate email (409 conflict) at `backend/tests/test_auth.py`
- [x] T027 [P] [US1] Test login with correct credentials at `backend/tests/test_auth.py`
- [x] T028 [P] [US1] Test login with incorrect credentials (401) at `backend/tests/test_auth.py`
- [x] T029 [P] [US1] Test /auth/me without auth token (401) at `backend/tests/test_auth.py`

**Checkpoint**: User Story 1 complete - users can register, login, logout

---

## Phase 4: User Story 2 - Add New Todo Item (Priority: P1)

**Goal**: Enable creating new todo items with validation

**Independent Test**: Login, create todo with title/description, see it in list

### Implementation for User Story 2

- [x] T030 [P] [US2] Create Todo SQLModel with TodoBase, Todo, TodoCreate, TodoRead schemas at `backend/src/models/todo.py`
- [x] T031 [US2] Create todo_service.py with create_todo function at `backend/src/services/todo_service.py`
- [x] T032 [US2] Implement POST /todos endpoint with title validation (1-200 chars, trim) at `backend/src/api/v1/todos.py`
- [x] T033 [US2] Implement GET /todos endpoint with cursor-based pagination at `backend/src/api/v1/todos.py`
- [x] T034 [US2] Add todos router to v1 router.py at `backend/src/api/v1/router.py`

### Tests for User Story 2

- [x] T035 [P] [US2] Test create todo with valid title at `backend/tests/test_todos.py`
- [x] T036 [P] [US2] Test create todo with empty title (400 validation error) at `backend/tests/test_todos.py`
- [x] T037 [P] [US2] Test create todo with title > 200 chars (400 error) at `backend/tests/test_todos.py`
- [x] T038 [P] [US2] Test create todo without auth (401) at `backend/tests/test_todos.py`
- [x] T039 [P] [US2] Test list todos returns only user's todos at `backend/tests/test_todos.py`

**Checkpoint**: User Story 2 complete - users can create todos

---

## Phase 5: User Story 3 - Update Existing Todo Item (Priority: P2)

**Goal**: Enable editing todo title and description

**Independent Test**: Create todo, edit title/description, verify changes persist

### Implementation for User Story 3

- [x] T040 [US3] Add TodoUpdate schema to todo.py at `backend/src/models/todo.py`
- [x] T041 [US3] Add update_todo, get_todo_by_id functions to todo_service.py at `backend/src/services/todo_service.py`
- [x] T042 [US3] Implement GET /todos/{id} endpoint with ownership check at `backend/src/api/v1/todos.py`
- [x] T043 [US3] Implement PATCH /todos/{id} endpoint with partial update at `backend/src/api/v1/todos.py`

### Tests for User Story 3

- [x] T044 [P] [US3] Test update todo with valid changes at `backend/tests/test_todos.py`
- [x] T045 [P] [US3] Test update todo with empty title (400 error) at `backend/tests/test_todos.py`
- [x] T046 [P] [US3] Test update todo owned by another user (404) at `backend/tests/test_todos.py`
- [x] T047 [P] [US3] Test get todo by id at `backend/tests/test_todos.py`

**Checkpoint**: User Story 3 complete - users can edit todos

---

## Phase 6: User Story 4 - Delete Todo Item (Priority: P2)

**Goal**: Enable soft-deleting todos

**Independent Test**: Create todo, delete it, verify it no longer appears in list

### Implementation for User Story 4

- [x] T048 [US4] Add soft_delete_todo function to todo_service.py at `backend/src/services/todo_service.py`
- [x] T049 [US4] Implement DELETE /todos/{id} endpoint with soft delete at `backend/src/api/v1/todos.py`
- [x] T050 [US4] Update GET /todos to exclude soft-deleted items at `backend/src/api/v1/todos.py`

### Tests for User Story 4

- [x] T051 [P] [US4] Test delete todo returns 204 at `backend/tests/test_todos.py`
- [x] T052 [P] [US4] Test deleted todo not in list at `backend/tests/test_todos.py`
- [x] T053 [P] [US4] Test delete non-existent todo (404) at `backend/tests/test_todos.py`

**Checkpoint**: User Story 4 complete - users can delete todos

---

## Phase 7: User Story 5 - Toggle Todo Status (Priority: P2)

**Goal**: Enable toggling between completed and remaining status

**Independent Test**: Toggle status multiple times, verify persistence

### Implementation for User Story 5

- [x] T054 [US5] Add toggle_todo_status function to todo_service.py at `backend/src/services/todo_service.py`
- [x] T055 [US5] Implement POST /todos/{id}/toggle endpoint at `backend/src/api/v1/todos.py`

### Tests for User Story 5

- [x] T056 [P] [US5] Test toggle from remaining to completed at `backend/tests/test_todos.py`
- [x] T057 [P] [US5] Test toggle from completed to remaining at `backend/tests/test_todos.py`
- [x] T058 [P] [US5] Test toggle non-existent todo (404) at `backend/tests/test_todos.py`

**Checkpoint**: User Story 5 complete - users can toggle status

---

## Phase 8: User Story 6 - Search Todos (Priority: P3)

**Goal**: Enable case-insensitive search by title/description

**Independent Test**: Create todos, search by keyword, verify matching results

### Implementation for User Story 6

- [x] T059 [US6] Add search parameter to list_todos in todo_service.py with ILIKE query at `backend/src/services/todo_service.py`
- [x] T060 [US6] Update GET /todos to accept search query parameter at `backend/src/api/v1/todos.py`

### Tests for User Story 6

- [x] T061 [P] [US6] Test search returns matching todos at `backend/tests/test_todos.py`
- [x] T062 [P] [US6] Test search is case-insensitive at `backend/tests/test_todos.py`
- [x] T063 [P] [US6] Test search with no matches returns empty list at `backend/tests/test_todos.py`

**Checkpoint**: User Story 6 complete - users can search todos

---

## Phase 9: User Story 7 - Filter Todos by Status (Priority: P3)

**Goal**: Enable filtering by completion status

**Independent Test**: Create completed/remaining todos, apply filters, verify results

### Implementation for User Story 7

- [x] T064 [US7] Add status filter to list_todos in todo_service.py at `backend/src/services/todo_service.py`
- [x] T065 [US7] Update GET /todos to accept status query parameter (all/completed/remaining) at `backend/src/api/v1/todos.py`

### Tests for User Story 7

- [x] T066 [P] [US7] Test filter by completed status at `backend/tests/test_todos.py`
- [x] T067 [P] [US7] Test filter by remaining status at `backend/tests/test_todos.py`
- [x] T068 [P] [US7] Test combined search and filter at `backend/tests/test_todos.py`

**Checkpoint**: User Story 7 complete - users can filter todos

---

## Phase 10: Polish & Error Handling

**Goal**: Production-ready error handling and logging

- [x] T069 Add structured logging with request context at `backend/src/core/logging.py`
- [x] T070 Add rate limiting on auth endpoints (10 req/min) at `backend/src/api/middleware/rate_limit.py`
- [x] T071 Add health check endpoint GET /health at `backend/src/api/v1/router.py`
- [x] T072 Review and update OpenAPI documentation at `backend/main.py`
- [x] T073 Run all tests and verify 100% critical path coverage at `backend/tests/`

**Checkpoint**: Backend production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ─────────────────────┐
    │                                        │
    ▼                                        │
Phase 3 (US1: Auth) ◄────────────────────────┤
    │                                        │
    ▼                                        │
Phase 4 (US2: Create) ◄──────────────────────┤
    │                                        │
    ▼                                        │
Phase 5 (US3: Update) ◄──────────────────────┤
    │                                        │
    ▼                                        │
Phase 6 (US4: Delete) ◄──────────────────────┤
    │                                        │
    ▼                                        │
Phase 7 (US5: Toggle) ◄──────────────────────┤
    │                                        │
    ▼                                        │
Phase 8 (US6: Search) ◄──────────────────────┤
    │                                        │
    ▼                                        │
Phase 9 (US7: Filter) ◄──────────────────────┘
    │
    ▼
Phase 10 (Polish)
```

### Parallel Opportunities

```bash
# Phase 1 parallel tasks:
T003, T004, T006 can run in parallel

# Phase 3 (US1) tests can all run in parallel:
T024, T025, T026, T027, T028, T029

# Each user story's tests can run in parallel after implementation
```

---

## Summary

| Phase | User Story | Task Count | Tests |
|-------|------------|------------|-------|
| 1 | Setup | 9 | 0 |
| 2 | Foundational | 6 | 0 |
| 3 | US1: Auth | 8 + 6 tests | 6 |
| 4 | US2: Create | 5 + 5 tests | 5 |
| 5 | US3: Update | 4 + 4 tests | 4 |
| 6 | US4: Delete | 3 + 3 tests | 3 |
| 7 | US5: Toggle | 2 + 3 tests | 3 |
| 8 | US6: Search | 2 + 3 tests | 3 |
| 9 | US7: Filter | 2 + 3 tests | 3 |
| 10 | Polish | 5 | 0 |
| **Total** | | **73 tasks** | **27 tests** |

**MVP Scope**: Complete Phases 1-4 (Setup + Auth + Create Todo) for minimum viable product
