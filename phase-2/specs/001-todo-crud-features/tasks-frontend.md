# Frontend Tasks: TodoList Pro

**Feature**: 001-todo-crud-features
**Input**: Design documents from `specs/001-todo-crud-features/`
**Prerequisites**: plan.md, spec.md, contracts/openapi.yaml
**Technology**: Next.js 14, TypeScript 5.x, React 18, Tailwind CSS

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Frontend Setup

**Goal**: Initialize Next.js project with TypeScript and Tailwind

- [x] F001 Create Next.js 14 project with TypeScript and App Router at `frontend/`
- [x] F002 Install and configure Tailwind CSS at `frontend/tailwind.config.js`
- [x] F003 [P] Create .env.example with NEXT_PUBLIC_API_URL at `frontend/.env.example`
- [x] F004 [P] Create globals.css with Tailwind directives and base styles at `frontend/src/app/globals.css`
- [x] F005 Create root layout.tsx with html/body structure at `frontend/src/app/layout.tsx`
- [x] F006 Create home page.tsx with redirect to /login or /todos at `frontend/src/app/page.tsx`
- [x] F007 [P] Create lib/api.ts with base fetch wrapper for API calls at `frontend/src/lib/api.ts`
- [x] F008 [P] Create types/index.ts with User, Todo, ApiError interfaces at `frontend/src/types/index.ts`

**Checkpoint**: Frontend starts with `pnpm dev` and shows home page

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Shared components and utilities needed by all features

- [x] F009 Create Button component with variants (primary, secondary, danger) at `frontend/src/components/ui/Button.tsx`
- [x] F010 [P] Create Input component with label and error states at `frontend/src/components/ui/Input.tsx`
- [x] F011 [P] Create Card component for content containers at `frontend/src/components/ui/Card.tsx`
- [x] F012 [P] Create LoadingSpinner component at `frontend/src/components/ui/LoadingSpinner.tsx`
- [x] F013 Create Toast notification component at `frontend/src/components/ui/Toast.tsx`
- [x] F014 Create lib/validation.ts with email and password validators at `frontend/src/lib/validation.ts`
- [x] F015 Create lib/auth.ts with auth cookie handling utilities at `frontend/src/lib/auth.ts`
- [x] F016 Create middleware.ts for route protection at `frontend/src/middleware.ts`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1)

**Goal**: Enable user registration, login, logout UI

**Independent Test**: Visit /register, create account, logout, login again

### Implementation for User Story 1

- [x] F017 [P] [US1] Create useAuth hook with login, register, logout, user state at `frontend/src/hooks/useAuth.ts`
- [x] F018 [P] [US1] Create AuthContext provider for app-wide auth state at `frontend/src/contexts/AuthContext.tsx`
- [x] F019 [US1] Create LoginForm component with email/password inputs at `frontend/src/components/auth/LoginForm.tsx`
- [x] F020 [US1] Create RegisterForm component with email/password/confirm inputs at `frontend/src/components/auth/RegisterForm.tsx`
- [x] F021 [US1] Create login page at `frontend/src/app/login/page.tsx`
- [x] F022 [US1] Create register page at `frontend/src/app/register/page.tsx`
- [x] F023 [US1] Add AuthProvider to root layout.tsx at `frontend/src/app/layout.tsx`
- [x] F024 [US1] Create Header component with user info and logout button at `frontend/src/components/layout/Header.tsx`
- [x] F025 [US1] Update middleware.ts to redirect unauthenticated users at `frontend/src/middleware.ts`

### Tests for User Story 1

- [x] F026 [P] [US1] Test LoginForm renders and submits at `frontend/tests/components/LoginForm.test.tsx`
- [ ] F027 [P] [US1] Test RegisterForm validates password length at `frontend/tests/components/RegisterForm.test.tsx`
- [ ] F028 [P] [US1] Test useAuth hook handles login/logout at `frontend/tests/hooks/useAuth.test.ts`

**Checkpoint**: User Story 1 complete - users can register, login, logout

---

## Phase 4: User Story 2 - Add New Todo Item (Priority: P1)

**Goal**: Enable creating todos and displaying list

**Independent Test**: Login, create todo with title/description, see it appear in list

### Implementation for User Story 2

- [x] F029 [P] [US2] Create useTodos hook with todos state, createTodo, fetchTodos at `frontend/src/hooks/useTodos.ts`
- [x] F030 [US2] Create TodoForm component with title input and submit at `frontend/src/components/todos/TodoForm.tsx`
- [x] F031 [US2] Create TodoList component displaying array of TodoItem at `frontend/src/components/todos/TodoList.tsx`
- [x] F032 [US2] Create TodoItem component showing title, description, status at `frontend/src/components/todos/TodoItem.tsx`
- [x] F033 [US2] Create todos page with TodoForm and TodoList at `frontend/src/app/todos/page.tsx`
- [x] F034 [US2] Add empty state "No todos yet" message to TodoList at `frontend/src/components/todos/TodoList.tsx`
- [x] F035 [US2] Add client-side validation for title (1-200 chars) to TodoForm at `frontend/src/components/todos/TodoForm.tsx`

### Tests for User Story 2

- [x] F036 [P] [US2] Test TodoForm submits with valid title at `frontend/tests/components/TodoForm.test.tsx`
- [x] F037 [P] [US2] Test TodoForm shows error for empty title at `frontend/tests/components/TodoForm.test.tsx`
- [ ] F038 [P] [US2] Test TodoList renders todos at `frontend/tests/components/TodoList.test.tsx`
- [ ] F039 [P] [US2] Test TodoList shows empty state at `frontend/tests/components/TodoList.test.tsx`

**Checkpoint**: User Story 2 complete - users can create and see todos

---

## Phase 5: User Story 3 - Update Existing Todo Item (Priority: P2)

**Goal**: Enable editing todo title and description

**Independent Test**: Click edit on todo, change title, save, verify changes

### Implementation for User Story 3

- [x] F040 [US3] Add updateTodo function to useTodos hook at `frontend/src/hooks/useTodos.ts`
- [x] F041 [US3] Create EditTodoModal component with edit form at `frontend/src/components/todos/EditTodoModal.tsx`
- [x] F042 [US3] Add edit button and modal trigger to TodoItem at `frontend/src/components/todos/TodoItem.tsx`
- [x] F043 [US3] Add optimistic update for edit in useTodos at `frontend/src/hooks/useTodos.ts`

### Tests for User Story 3

- [ ] F044 [P] [US3] Test EditTodoModal prefills current values at `frontend/tests/components/EditTodoModal.test.tsx`
- [ ] F045 [P] [US3] Test EditTodoModal validates empty title at `frontend/tests/components/EditTodoModal.test.tsx`

**Checkpoint**: User Story 3 complete - users can edit todos

---

## Phase 6: User Story 4 - Delete Todo Item (Priority: P2)

**Goal**: Enable deleting todos with confirmation

**Independent Test**: Click delete, confirm, verify todo disappears

### Implementation for User Story 4

- [x] F046 [P] [US4] Create ConfirmDialog component at `frontend/src/components/ui/ConfirmDialog.tsx`
- [x] F047 [US4] Add deleteTodo function to useTodos hook at `frontend/src/hooks/useTodos.ts`
- [x] F048 [US4] Add delete button with confirm dialog to TodoItem at `frontend/src/components/todos/TodoItem.tsx`
- [x] F049 [US4] Add optimistic delete with rollback on error at `frontend/src/hooks/useTodos.ts`

### Tests for User Story 4

- [ ] F050 [P] [US4] Test ConfirmDialog shows and handles confirm/cancel at `frontend/tests/components/ConfirmDialog.test.tsx`
- [ ] F051 [P] [US4] Test TodoItem delete triggers confirmation at `frontend/tests/components/TodoItem.test.tsx`

**Checkpoint**: User Story 4 complete - users can delete todos

---

## Phase 7: User Story 5 - Toggle Todo Status (Priority: P2)

**Goal**: Enable toggling completed/remaining with visual feedback

**Independent Test**: Click checkbox, see strikethrough, refresh, status persists

### Implementation for User Story 5

- [x] F052 [US5] Add toggleTodo function to useTodos hook at `frontend/src/hooks/useTodos.ts`
- [x] F053 [US5] Add checkbox/toggle button to TodoItem at `frontend/src/components/todos/TodoItem.tsx`
- [x] F054 [US5] Add strikethrough/visual styling for completed todos at `frontend/src/components/todos/TodoItem.tsx`
- [x] F055 [US5] Add optimistic toggle with rollback at `frontend/src/hooks/useTodos.ts`

### Tests for User Story 5

- [ ] F056 [P] [US5] Test TodoItem toggle changes visual state at `frontend/tests/components/TodoItem.test.tsx`
- [ ] F057 [P] [US5] Test completed todo shows strikethrough at `frontend/tests/components/TodoItem.test.tsx`

**Checkpoint**: User Story 5 complete - users can toggle status

---

## Phase 8: User Story 6 - Search Todos (Priority: P3)

**Goal**: Enable real-time search with debounce

**Independent Test**: Type in search bar, see filtered results in real-time

### Implementation for User Story 6

- [x] F058 [P] [US6] Create useDebounce hook for 300ms delay at `frontend/src/hooks/useDebounce.ts`
- [x] F059 [US6] Create SearchBar component with search input at `frontend/src/components/todos/SearchBar.tsx`
- [x] F060 [US6] Add searchQuery state and API call to useTodos at `frontend/src/hooks/useTodos.ts`
- [x] F061 [US6] Add SearchBar to todos page above TodoList at `frontend/src/app/todos/page.tsx`
- [x] F062 [US6] Add "No todos found" message for empty search results at `frontend/src/components/todos/TodoList.tsx`

### Tests for User Story 6

- [ ] F063 [P] [US6] Test SearchBar triggers search on input at `frontend/tests/components/SearchBar.test.tsx`
- [x] F064 [P] [US6] Test useDebounce delays value updates at `frontend/tests/hooks/useDebounce.test.ts`

**Checkpoint**: User Story 6 complete - users can search todos

---

## Phase 9: User Story 7 - Filter Todos by Status (Priority: P3)

**Goal**: Enable filtering by All/Remaining/Completed

**Independent Test**: Click filter tabs, see only matching todos

### Implementation for User Story 7

- [x] F065 [US7] Create FilterTabs component with All/Remaining/Completed at `frontend/src/components/todos/FilterTabs.tsx`
- [x] F066 [US7] Add statusFilter state and API param to useTodos at `frontend/src/hooks/useTodos.ts`
- [x] F067 [US7] Add FilterTabs to todos page between SearchBar and TodoList at `frontend/src/app/todos/page.tsx`
- [x] F068 [US7] Handle combined search + filter in useTodos at `frontend/src/hooks/useTodos.ts`

### Tests for User Story 7

- [ ] F069 [P] [US7] Test FilterTabs switches active filter at `frontend/tests/components/FilterTabs.test.tsx`
- [ ] F070 [P] [US7] Test filter and search combine correctly at `frontend/tests/hooks/useTodos.test.ts`

**Checkpoint**: User Story 7 complete - users can filter todos

---

## Phase 10: Polish & Error Handling

**Goal**: Production-ready UX with error boundaries and loading states

- [x] F071 Create ErrorBoundary component for graceful error handling at `frontend/src/components/ErrorBoundary.tsx`
- [x] F072 Add ErrorBoundary to root layout at `frontend/src/app/layout.tsx`
- [x] F073 Add loading states to all async operations at `frontend/src/hooks/useTodos.ts`
- [x] F074 Create loading.tsx for todos page at `frontend/src/app/todos/loading.tsx`
- [x] F075 Add toast notifications for success/error feedback at `frontend/src/app/todos/page.tsx`
- [x] F076 [P] Add responsive design for mobile screens at `frontend/src/app/globals.css`
- [x] F077 [P] Add keyboard accessibility (Enter to submit, Escape to cancel) at `frontend/src/components/todos/`
- [x] F078 Run Lighthouse audit and fix performance issues at `frontend/`
- [x] F079 [P] Create Footer component with copyright "All rights reserved by Tayyab Fayyaz" at `frontend/src/components/layout/Footer.tsx`
- [x] F080 Add Footer component to root layout at `frontend/src/app/layout.tsx`

**Checkpoint**: Frontend production-ready

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
F003, F004, F007, F008 can run in parallel

# Phase 2 parallel tasks:
F010, F011, F012 can run in parallel

# Phase 3 parallel tasks:
F017, F018 can run in parallel

# Each user story's tests can run in parallel
```

### Backend Dependency

Frontend tasks for each user story should be implemented AFTER the corresponding backend tasks are complete:

| Frontend Phase | Requires Backend Phase |
|----------------|----------------------|
| Phase 3 (US1) | Backend Phase 3 (US1: Auth) |
| Phase 4 (US2) | Backend Phase 4 (US2: Create) |
| Phase 5 (US3) | Backend Phase 5 (US3: Update) |
| Phase 6 (US4) | Backend Phase 6 (US4: Delete) |
| Phase 7 (US5) | Backend Phase 7 (US5: Toggle) |
| Phase 8 (US6) | Backend Phase 8 (US6: Search) |
| Phase 9 (US7) | Backend Phase 9 (US7: Filter) |

---

## Summary

| Phase | User Story | Task Count | Tests |
|-------|------------|------------|-------|
| 1 | Setup | 8 | 0 |
| 2 | Foundational | 8 | 0 |
| 3 | US1: Auth | 9 + 3 tests | 3 |
| 4 | US2: Create | 7 + 4 tests | 4 |
| 5 | US3: Update | 4 + 2 tests | 2 |
| 6 | US4: Delete | 4 + 2 tests | 2 |
| 7 | US5: Toggle | 4 + 2 tests | 2 |
| 8 | US6: Search | 5 + 2 tests | 2 |
| 9 | US7: Filter | 4 + 2 tests | 2 |
| 10 | Polish | 10 | 0 |
| **Total** | | **80 tasks** | **17 tests** |

**MVP Scope**: Complete Phases 1-4 (Setup + Auth + Create Todo) for minimum viable product

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Auth)
4. Complete Phase 4: User Story 2 (Create)
5. **STOP and VALIDATE**: Test end-to-end flow
6. Deploy MVP

### Incremental Delivery

1. Setup + Foundation → Ready to build
2. Add US1 (Auth) → Users can register/login
3. Add US2 (Create) → Users can add todos (MVP!)
4. Add US3 (Update) → Users can edit
5. Add US4 (Delete) → Users can remove
6. Add US5 (Toggle) → Full CRUD complete
7. Add US6 (Search) → Enhanced UX
8. Add US7 (Filter) → Power user features
9. Polish → Production ready
