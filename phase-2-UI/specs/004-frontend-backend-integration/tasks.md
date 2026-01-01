# Tasks: Frontend-Backend Integration

**Input**: Design documents from `/specs/004-frontend-backend-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-schema.yaml

**Tests**: Not explicitly requested - test tasks are omitted. Focus is on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `todolist-pro/src/` (Next.js)
- **Backend**: `backend/` (FastAPI - existing, minimal changes)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create foundational files

- [X] T001 Install Better-Auth and TanStack Query dependencies in todolist-pro/package.json
- [X] T002 [P] Create Better-Auth server configuration in todolist-pro/src/lib/auth.ts
- [X] T003 [P] Create Better-Auth client configuration in todolist-pro/src/lib/auth-client.ts
- [X] T004 [P] Create API client with Bearer token support in todolist-pro/src/lib/api.ts
- [X] T005 Create API route handler in todolist-pro/src/app/api/auth/[...all]/route.ts
- [X] T006 Run Better-Auth database migrations to create user/session tables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create TanStack Query provider in todolist-pro/src/components/providers/query-provider.tsx
- [X] T008 Wrap app layout with QueryProvider in todolist-pro/src/app/layout.tsx
- [X] T009 [P] Update TypeScript types for auth and API responses in todolist-pro/src/types/index.ts
- [X] T010 [P] Create useAuth hook in todolist-pro/src/hooks/use-auth.ts
- [X] T011 Create middleware for route protection in todolist-pro/src/middleware.ts
- [X] T012 Update dashboard layout with server-side auth check in todolist-pro/src/app/(dashboard)/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1)

**Goal**: Enable new users to create accounts with email/password

**Independent Test**: Navigate to /register, fill form with valid data, verify account created and can log in

### Implementation for User Story 1

- [X] T013 [US1] Update RegisterForm to use Better-Auth signUp in todolist-pro/src/components/auth/register-form.tsx
- [X] T014 [US1] Add token storage on successful registration in todolist-pro/src/components/auth/register-form.tsx
- [X] T015 [US1] Add error handling for duplicate email and validation errors in todolist-pro/src/components/auth/register-form.tsx
- [X] T016 [US1] Add success redirect to login page after registration in todolist-pro/src/components/auth/register-form.tsx

**Checkpoint**: User Story 1 complete - users can register accounts

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: Enable existing users to authenticate and access their dashboard

**Independent Test**: Log in with valid credentials, verify redirect to dashboard with session persisted

### Implementation for User Story 2

- [X] T017 [US2] Update LoginForm to use Better-Auth signIn in todolist-pro/src/components/auth/login-form.tsx
- [X] T018 [US2] Extract and store bearer token from response header in todolist-pro/src/components/auth/login-form.tsx
- [X] T019 [US2] Add error handling for invalid credentials in todolist-pro/src/components/auth/login-form.tsx
- [X] T020 [US2] Add redirect to dashboard on successful login in todolist-pro/src/components/auth/login-form.tsx
- [X] T021 [US2] Add session persistence check (remember me functionality) in todolist-pro/src/components/auth/login-form.tsx

**Checkpoint**: User Story 2 complete - users can log in and access dashboard

---

## Phase 5: User Story 3 - Create Task (Priority: P1)

**Goal**: Enable authenticated users to create new tasks that persist to database

**Independent Test**: Log in, add task, verify it appears and persists after refresh

### Implementation for User Story 3

- [X] T022 [US3] Create useTasks hook with TanStack Query in todolist-pro/src/hooks/use-tasks.ts
- [X] T023 [US3] Implement useCreateTask mutation with optimistic update in todolist-pro/src/hooks/use-tasks.ts
- [X] T024 [US3] Update TaskInput to use useCreateTask mutation in todolist-pro/src/components/tasks/task-input.tsx
- [X] T025 [US3] Add loading state during task creation in todolist-pro/src/components/tasks/task-input.tsx
- [X] T026 [US3] Add error handling and rollback for failed creation in todolist-pro/src/components/tasks/task-input.tsx

**Checkpoint**: User Story 3 complete - users can create tasks that persist

---

## Phase 6: User Story 4 - View Tasks (Priority: P1)

**Goal**: Display user's tasks fetched from backend API

**Independent Test**: Log in, verify previously created tasks are displayed

### Implementation for User Story 4

- [X] T027 [US4] Update Dashboard page to fetch tasks using useTasks hook in todolist-pro/src/app/(dashboard)/dashboard/page.tsx
- [X] T028 [US4] Update TaskList to receive tasks from API instead of mock data in todolist-pro/src/components/tasks/task-list.tsx
- [X] T029 [US4] Add loading skeleton while fetching tasks in todolist-pro/src/components/tasks/task-list.tsx
- [X] T030 [US4] Update EmptyState to show when no tasks exist in todolist-pro/src/components/tasks/empty-state.tsx
- [X] T031 [US4] Add error state display for failed task fetch in todolist-pro/src/app/(dashboard)/dashboard/page.tsx

**Checkpoint**: User Story 4 complete - users see their persisted tasks

---

## Phase 7: User Story 5 - Complete Task (Priority: P2)

**Goal**: Enable users to toggle task completion status with persistence

**Independent Test**: Toggle task completion, verify status persists after refresh

### Implementation for User Story 5

- [X] T032 [US5] Implement useToggleTask mutation with optimistic update in todolist-pro/src/hooks/use-tasks.ts
- [X] T033 [US5] Update TaskItem to use useToggleTask mutation in todolist-pro/src/components/tasks/task-item.tsx
- [X] T034 [US5] Add visual feedback during toggle operation in todolist-pro/src/components/tasks/task-item.tsx
- [X] T035 [US5] Add error handling and rollback for failed toggle in todolist-pro/src/components/tasks/task-item.tsx

**Checkpoint**: User Story 5 complete - users can toggle task completion

---

## Phase 8: User Story 6 - Edit Task (Priority: P2)

**Goal**: Enable users to modify task text with persistence

**Independent Test**: Edit task text, verify change persists after refresh

### Implementation for User Story 6

- [X] T036 [US6] Implement useUpdateTask mutation with optimistic update in todolist-pro/src/hooks/use-tasks.ts
- [X] T037 [US6] Update TaskItem to use useUpdateTask mutation in todolist-pro/src/components/tasks/task-item.tsx
- [X] T038 [US6] Add cancel edit functionality (restore original text) in todolist-pro/src/components/tasks/task-item.tsx
- [X] T039 [US6] Add error handling and rollback for failed update in todolist-pro/src/components/tasks/task-item.tsx

**Checkpoint**: User Story 6 complete - users can edit task text

---

## Phase 9: User Story 7 - Delete Task (Priority: P2)

**Goal**: Enable users to permanently delete tasks

**Independent Test**: Delete task with confirmation, verify it no longer appears

### Implementation for User Story 7

- [X] T040 [US7] Implement useDeleteTask mutation with optimistic update in todolist-pro/src/hooks/use-tasks.ts
- [X] T041 [US7] Update DeleteDialog to use useDeleteTask mutation in todolist-pro/src/components/tasks/delete-dialog.tsx
- [X] T042 [US7] Update TaskItem delete button to trigger DeleteDialog in todolist-pro/src/components/tasks/task-item.tsx
- [X] T043 [US7] Add error handling and rollback for failed deletion in todolist-pro/src/components/tasks/delete-dialog.tsx

**Checkpoint**: User Story 7 complete - users can delete tasks

---

## Phase 10: User Story 8 - User Logout (Priority: P3)

**Goal**: Enable users to end their session securely

**Independent Test**: Log out, verify redirect to home and dashboard access denied

### Implementation for User Story 8

- [X] T044 [US8] Add logout button to Navbar component in todolist-pro/src/components/layout/navbar.tsx
- [X] T045 [US8] Implement logout handler using authClient.signOut in todolist-pro/src/components/layout/navbar.tsx
- [X] T046 [US8] Clear bearer token from localStorage on logout in todolist-pro/src/components/layout/navbar.tsx
- [X] T047 [US8] Add redirect to home page after logout in todolist-pro/src/components/layout/navbar.tsx
- [X] T048 [US8] Add user display (name/avatar) in Navbar when authenticated in todolist-pro/src/components/layout/navbar.tsx

**Checkpoint**: User Story 8 complete - users can log out securely

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T049 [P] Add global error boundary for API errors in todolist-pro/src/app/error.tsx
- [X] T050 [P] Add session expiry handling (redirect to login with message) in todolist-pro/src/lib/api.ts
- [X] T051 [P] Add loading indicator component for API operations in todolist-pro/src/components/ui/loading.tsx
- [X] T052 Update task counts (total, completed, remaining) to use real data in todolist-pro/src/app/(dashboard)/dashboard/page.tsx
- [X] T053 Remove mock-data.ts and unused mock imports in todolist-pro/src/lib/mock-data.ts
- [X] T054 Run quickstart.md verification checklist

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    └── Phase 2: Foundational (BLOCKS all user stories)
            └── Phase 3-10: User Stories (can run in priority order)
                    └── Phase 11: Polish
```

### User Story Dependencies

| Story | Priority | Dependencies | Can Start After |
|-------|----------|--------------|-----------------|
| US1: Registration | P1 | Phase 2 | Phase 2 complete |
| US2: Login | P1 | Phase 2 | Phase 2 complete |
| US3: Create Task | P1 | Phase 2, US2 (need to be logged in) | US2 complete |
| US4: View Tasks | P1 | Phase 2, US2 | US2 complete |
| US5: Complete Task | P2 | US4 (need tasks to toggle) | US4 complete |
| US6: Edit Task | P2 | US4 (need tasks to edit) | US4 complete |
| US7: Delete Task | P2 | US4 (need tasks to delete) | US4 complete |
| US8: Logout | P3 | US2 (need to be logged in) | US2 complete |

### Within Each User Story

1. Hook implementation first (if new mutations needed)
2. Component updates second
3. Error handling and edge cases last

### Parallel Opportunities

**Setup Phase (T001-T006)**:
- T002, T003, T004 can run in parallel (different files)

**Foundational Phase (T007-T012)**:
- T009, T010 can run in parallel (different files)

**User Stories (T013-T048)**:
- US5, US6, US7 can run in parallel (after US4, different mutations)
- US8 can run in parallel with US5-US7 (only needs US2)

---

## Parallel Example: After Phase 2 Complete

```bash
# Launch User Stories 1 and 2 in parallel (both P1, independent):
Task: "T013 [US1] Update RegisterForm..."
Task: "T017 [US2] Update LoginForm..."

# After US4 complete, launch US5, US6, US7 in parallel:
Task: "T032 [US5] Implement useToggleTask..."
Task: "T036 [US6] Implement useUpdateTask..."
Task: "T040 [US7] Implement useDeleteTask..."
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T012)
3. Complete Phase 3: Registration (T013-T016)
4. Complete Phase 4: Login (T017-T021)
5. Complete Phase 5: Create Task (T022-T026)
6. Complete Phase 6: View Tasks (T027-T031)
7. **STOP and VALIDATE**: All P1 stories complete - MVP ready!

### Incremental Delivery

| Milestone | Stories Complete | User Value |
|-----------|------------------|------------|
| MVP | US1-4 | Register, login, create and view tasks |
| +Completion | US1-5 | Track task progress |
| +Editing | US1-6 | Fix mistakes in tasks |
| +Deletion | US1-7 | Clean up task list |
| +Logout | US1-8 | Full session management |

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 54 |
| **Setup Tasks** | 6 |
| **Foundational Tasks** | 6 |
| **User Story Tasks** | 36 |
| **Polish Tasks** | 6 |
| **Parallel Opportunities** | 12 tasks marked [P] |

| User Story | Task Count | Priority |
|------------|------------|----------|
| US1: Registration | 4 | P1 |
| US2: Login | 5 | P1 |
| US3: Create Task | 5 | P1 |
| US4: View Tasks | 5 | P1 |
| US5: Complete Task | 4 | P2 |
| US6: Edit Task | 4 | P2 |
| US7: Delete Task | 4 | P2 |
| US8: Logout | 5 | P3 |

**Suggested MVP Scope**: User Stories 1-4 (Registration, Login, Create Task, View Tasks) = 19 tasks + 12 setup/foundational = **31 tasks for MVP**
