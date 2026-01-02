# Tasks: FastAPI Tasks CRUD API

**Feature**: 003-fastapi-tasks-api
**Input**: Design documents from `/specs/003-fastapi-tasks-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-schema.yaml

**Tests**: Tests are included as the constitution mandates TDD (Test-Driven Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend API**: `backend/app/` for source, `backend/tests/` for tests
- Per plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure per plan.md: `backend/app/{api,models,schemas}`, `backend/tests/`, `backend/alembic/`
- [ ] T002 Initialize Python project with pyproject.toml: FastAPI, SQLModel, asyncpg, pydantic-settings, uuid6, PyJWT, uvicorn
- [ ] T003 [P] Add dev dependencies: pytest, pytest-asyncio, httpx, pytest-cov, alembic
- [ ] T004 [P] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS placeholders in backend/.env.example
- [ ] T005 [P] Create backend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement config module with Pydantic BaseSettings in backend/app/config.py
- [ ] T007 Implement async database connection with SQLModel in backend/app/database.py
- [ ] T008 [P] Create Task SQLModel entity in backend/app/models/task.py (per data-model.md)
- [ ] T009 [P] Create TaskCreate, TaskUpdate, TaskPatch, TaskResponse schemas in backend/app/schemas/task.py
- [ ] T010 [P] Create ErrorResponse schema in backend/app/schemas/error.py
- [ ] T011 [P] Create HealthResponse schema in backend/app/schemas/health.py
- [ ] T012 Initialize Alembic with async support in backend/alembic/env.py
- [ ] T013 Create initial migration for tasks table in backend/alembic/versions/001_create_tasks_table.py
- [ ] T014 Create FastAPI app with lifespan, CORS in backend/app/main.py
- [ ] T015 Create __init__.py files for all packages: app, models, schemas, api, api/routes

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 5 - Token Validation (Priority: P1 - Security Foundation)

**Goal**: Validate Better-Auth JWT tokens on all protected requests

**Independent Test**: Send requests with valid/invalid/expired tokens, verify 401 for bad tokens

> **Note**: Authentication is implemented first as it's required by all CRUD stories

### Tests for User Story 5

- [ ] T016 [P] [US5] Create test fixtures for JWT tokens (valid, expired, malformed) in backend/tests/conftest.py
- [ ] T017 [P] [US5] Write auth dependency tests in backend/tests/test_auth.py (expect FAIL initially)

### Implementation for User Story 5

- [ ] T018 [US5] Implement JWT token validation with PyJWT in backend/app/api/deps.py (get_current_user dependency)
- [ ] T019 [US5] Implement get_session dependency for database sessions in backend/app/api/deps.py
- [ ] T020 [US5] Add HTTPBearer security scheme to FastAPI app in backend/app/main.py
- [ ] T021 [US5] Run auth tests - verify they PASS after implementation

**Checkpoint**: Authentication infrastructure complete - CRUD stories can now use get_current_user

---

## Phase 4: User Story 1 - Create Task (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create new tasks via POST /tasks

**Independent Test**: POST /tasks with valid token and text returns 201 with task details

### Tests for User Story 1

- [ ] T022 [P] [US1] Write POST /tasks endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test 201 Created with valid data
  - Test 401 Unauthorized without token
  - Test 422 Validation Error with empty text

### Implementation for User Story 1

- [ ] T023 [US1] Create tasks router file in backend/app/api/routes/tasks.py
- [ ] T024 [US1] Implement POST /tasks endpoint in backend/app/api/routes/tasks.py
- [ ] T025 [US1] Register tasks router in backend/app/main.py
- [ ] T026 [US1] Run create task tests - verify they PASS

**Checkpoint**: Users can create tasks - minimal viable product achieved

---

## Phase 5: User Story 2 - Retrieve Tasks (Priority: P1)

**Goal**: Authenticated users can view their tasks (list and single)

**Independent Test**: GET /tasks returns only the authenticated user's tasks

### Tests for User Story 2

- [ ] T027 [P] [US2] Write GET /tasks list endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test 200 OK with user's tasks
  - Test empty array when no tasks
  - Test user isolation (can't see other users' tasks)
- [ ] T028 [P] [US2] Write GET /tasks/{id} endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test 200 OK with task details
  - Test 404 Not Found for non-existent task
  - Test 404 Not Found for other user's task

### Implementation for User Story 2

- [ ] T029 [US2] Implement GET /tasks endpoint in backend/app/api/routes/tasks.py
- [ ] T030 [US2] Implement GET /tasks/{id} endpoint in backend/app/api/routes/tasks.py
- [ ] T031 [US2] Run retrieve task tests - verify they PASS

**Checkpoint**: Users can create and view tasks

---

## Phase 6: User Story 3 - Update Task (Priority: P1)

**Goal**: Authenticated users can update task text and toggle completion status

**Independent Test**: PUT/PATCH /tasks/{id} updates task and returns updated data

### Tests for User Story 3

- [ ] T032 [P] [US3] Write PUT /tasks/{id} endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test 200 OK with full update
  - Test 404 Not Found for non-existent task
  - Test 422 Validation Error for invalid data
- [ ] T033 [P] [US3] Write PATCH /tasks/{id} endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test toggle completion (completed_at set/cleared)
  - Test partial text update
  - Test 404 for other user's task

### Implementation for User Story 3

- [ ] T034 [US3] Implement PUT /tasks/{id} endpoint in backend/app/api/routes/tasks.py
- [ ] T035 [US3] Implement PATCH /tasks/{id} endpoint with completion timestamp logic in backend/app/api/routes/tasks.py
- [ ] T036 [US3] Run update task tests - verify they PASS

**Checkpoint**: Users can create, view, and update tasks

---

## Phase 7: User Story 4 - Delete Task (Priority: P1)

**Goal**: Authenticated users can delete their tasks

**Independent Test**: DELETE /tasks/{id} removes task, subsequent GET returns 404

### Tests for User Story 4

- [ ] T037 [P] [US4] Write DELETE /tasks/{id} endpoint tests in backend/tests/test_tasks.py (expect FAIL initially)
  - Test 204 No Content on success
  - Test 404 Not Found for non-existent task
  - Test 404 Not Found for other user's task

### Implementation for User Story 4

- [ ] T038 [US4] Implement DELETE /tasks/{id} endpoint in backend/app/api/routes/tasks.py
- [ ] T039 [US4] Run delete task tests - verify they PASS

**Checkpoint**: Full CRUD functionality complete

---

## Phase 8: User Story 6 - Health & Documentation (Priority: P2)

**Goal**: Provide health check endpoint and OpenAPI documentation

**Independent Test**: GET /health returns status without authentication

### Tests for User Story 6

- [ ] T040 [P] [US6] Write health endpoint tests in backend/tests/test_health.py (expect FAIL initially)
  - Test 200 OK with healthy status
  - Test database connectivity check

### Implementation for User Story 6

- [ ] T041 [US6] Create health router in backend/app/api/routes/health.py
- [ ] T042 [US6] Implement GET /health endpoint with database check in backend/app/api/routes/health.py
- [ ] T043 [US6] Register health router in backend/app/main.py
- [ ] T044 [US6] Verify /docs Swagger UI renders correctly
- [ ] T045 [US6] Run health tests - verify they PASS

**Checkpoint**: API is production-ready with monitoring and documentation

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 [P] Add request logging middleware with correlation IDs in backend/app/main.py
- [ ] T047 [P] Add global exception handlers for database errors in backend/app/main.py
- [ ] T048 [P] Update backend/README.md with full API documentation
- [ ] T049 Run full test suite with coverage: `pytest --cov=app --cov-report=html`
- [ ] T050 Verify all endpoints match contracts/api-schema.yaml
- [ ] T051 Run quickstart.md validation - test end-to-end flow

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────────►
                  │
Phase 2 (Foundational) ───────────────────────────────────────────►
                        │
                        ├── Phase 3 (US5: Auth) ──────────────────►
                        │                       │
                        │                       ├── Phase 4 (US1: Create) ──►
                        │                       ├── Phase 5 (US2: Read) ────►
                        │                       ├── Phase 6 (US3: Update) ──►
                        │                       ├── Phase 7 (US4: Delete) ──►
                        │                       │
                        │                       └── Phase 8 (US6: Health) ──►
                        │                                              │
                        └──────────────────────────────────────────────┴── Phase 9 (Polish) ──►
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|----------------------|
| US5 (Auth) | Foundational | - |
| US1 (Create) | US5 | US2, US3, US4, US6 |
| US2 (Read) | US5 | US1, US3, US4, US6 |
| US3 (Update) | US5 | US1, US2, US4, US6 |
| US4 (Delete) | US5 | US1, US2, US3, US6 |
| US6 (Health) | Foundational | US1, US2, US3, US4 |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Implement endpoint code
3. Run tests - verify they PASS
4. Move to next story

### Parallel Opportunities per Phase

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel

**Phase 2 (Foundational)**: T008, T009, T010, T011 can run in parallel

**Phase 3 (US5)**: T016, T017 can run in parallel

**Phase 4-7 (CRUD)**: After US5 completes, all CRUD stories can run in parallel

**Phase 9 (Polish)**: T046, T047, T048 can run in parallel

---

## Parallel Example: After Auth Complete (Phase 3)

```bash
# Developer A - User Story 1 (Create)
Task: "Write POST /tasks endpoint tests"
Task: "Implement POST /tasks endpoint"

# Developer B - User Story 2 (Read)
Task: "Write GET /tasks list endpoint tests"
Task: "Write GET /tasks/{id} endpoint tests"
Task: "Implement GET /tasks and /tasks/{id} endpoints"

# Developer C - User Story 3 & 4 (Update/Delete)
Task: "Write PUT/PATCH/DELETE endpoint tests"
Task: "Implement update and delete endpoints"
```

---

## Implementation Strategy

### MVP First (User Stories 1-5)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US5 (Auth) - Required for all CRUD
4. Complete Phase 4: US1 (Create)
5. **STOP and VALIDATE**: Can create tasks with valid token
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational + Auth → API framework ready
2. Add US1 (Create) → Test independently → Minimal demo
3. Add US2 (Read) → Full read functionality
4. Add US3 (Update) → Toggle completion works
5. Add US4 (Delete) → Full CRUD complete
6. Add US6 (Health) → Production ready
7. Polish → Ship it!

---

## Summary

| Phase | Tasks | Parallel Tasks | Story |
|-------|-------|----------------|-------|
| Setup | 5 | 3 | - |
| Foundational | 10 | 4 | - |
| US5 (Auth) | 6 | 2 | P1 |
| US1 (Create) | 5 | 1 | P1 |
| US2 (Read) | 5 | 2 | P1 |
| US3 (Update) | 5 | 2 | P1 |
| US4 (Delete) | 3 | 1 | P1 |
| US6 (Health) | 6 | 1 | P2 |
| Polish | 6 | 3 | - |
| **Total** | **51** | **19** | - |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD per constitution)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
