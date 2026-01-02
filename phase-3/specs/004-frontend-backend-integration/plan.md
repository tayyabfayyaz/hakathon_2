# Implementation Plan: Frontend-Backend Integration

**Branch**: `004-frontend-backend-integration` | **Date**: 2024-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-backend-integration/spec.md`

## Summary

This feature integrates the existing Next.js frontend with the FastAPI backend and Better-Auth authentication system. The implementation will:
1. Configure Better-Auth in the Next.js frontend for user registration and login
2. Create an API client to communicate with FastAPI backend endpoints
3. Replace mock data with real API calls for all task CRUD operations
4. Implement route protection and session management
5. Handle loading states, error handling, and optimistic UI updates

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend - existing)
**Primary Dependencies**: Next.js 14+, Better-Auth, React Hook Form, Zod, TanStack Query
**Storage**: Neon PostgreSQL via FastAPI backend (existing)
**Testing**: Vitest for unit tests, Playwright for E2E tests
**Target Platform**: Web (modern browsers)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <3s dashboard load, <2s task operations, <100ms UI response
**Constraints**: Must use existing FastAPI backend API, shared JWT secret with Better-Auth
**Scale/Scope**: Single user application, ~1000 tasks per user max

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Data Integrity First | PASS | Backend is source of truth; optimistic updates with rollback planned |
| II. Offline-First Architecture | PARTIAL | Initial implementation online-only; offline queuing deferred to future iteration |
| III. User Experience Excellence | PASS | Loading states, error messages, instant UI response planned |
| IV. Test-Driven Development | PASS | Tests will be written for auth flows and API integration |
| V. Security & Privacy by Design | PASS | Better-Auth for secure auth; JWT tokens; user data isolation |
| VI. Performance Budget | PASS | <3s load time, <200KB JS bundle targets |

**Offline-First Exception**: Initial implementation will be online-only. Offline support is explicitly out of scope per spec. This is acceptable for MVP but should be added in a future iteration.

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-backend-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-schema.yaml
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/                    # Existing FastAPI backend (from 003-fastapi-tasks-api)
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   └── api/
│       ├── deps.py
│       └── routes/
└── tests/

todolist-pro/               # Existing Next.js frontend (from 002-todolist-pro-ui)
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/
│   │   │   └── dashboard/
│   │   └── (marketing)/
│   ├── components/
│   │   ├── auth/           # Login/Register forms (to be updated)
│   │   ├── tasks/          # Task components (to be updated)
│   │   ├── layout/
│   │   └── ui/
│   ├── lib/
│   │   ├── auth.ts         # NEW: Better-Auth client config
│   │   ├── api.ts          # NEW: API client for backend
│   │   ├── validations.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── use-auth.ts     # NEW: Auth hook
│   │   └── use-tasks.ts    # NEW: Tasks hook with TanStack Query
│   └── types/
│       └── index.ts
└── tests/
    ├── unit/
    └── e2e/
```

**Structure Decision**: Web application with existing frontend and backend. New files will be added to integrate the two layers while preserving existing component structure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                              │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │   Pages     │────▶│   Hooks     │────▶│  API Client │           │
│  │  (Auth,     │     │ (useAuth,   │     │  (fetch +   │           │
│  │  Dashboard) │     │  useTasks)  │     │   tokens)   │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│         │                   │                    │                  │
│         ▼                   ▼                    │                  │
│  ┌─────────────┐     ┌─────────────┐            │                  │
│  │ Components  │     │ TanStack    │            │                  │
│  │ (Forms,     │     │ Query       │            │                  │
│  │  TaskList)  │     │ (caching)   │            │                  │
│  └─────────────┘     └─────────────┘            │                  │
├─────────────────────────────────────────────────┼──────────────────┤
│                     Better-Auth                  │                  │
│  ┌─────────────────────────────────────────┐    │                  │
│  │  - Session management                    │    │                  │
│  │  - JWT token generation                  │◀───┤                  │
│  │  - User registration/login               │    │                  │
│  └─────────────────────────────────────────┘    │                  │
└─────────────────────────────────────────────────┼──────────────────┘
                                                   │
                          HTTP + JWT Bearer Token  │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │   Routes    │────▶│    Deps     │────▶│   Models    │           │
│  │  /tasks/*   │     │ (JWT auth)  │     │  (Task)     │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                  │                  │
│                                                  ▼                  │
│                                          ┌─────────────┐           │
│                                          │    Neon     │           │
│                                          │ PostgreSQL  │           │
│                                          └─────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Integration Points

### 1. Authentication Flow

```
User → Login Form → Better-Auth signIn() → JWT Token → Stored in Session
                                                            │
User → Dashboard → useAuth() → Get Session → Extract Token ─┘
                                                            │
API Request → Include Bearer Token in Header ───────────────┘
                                                            │
FastAPI → Validate JWT → Extract user_id → Filter Tasks ────┘
```

### 2. Task Operations Flow

```
User Action → useTasks() hook → Optimistic Update → API Call
                                      │                  │
                                      ▼                  ▼
                               Update UI         FastAPI Backend
                                      │                  │
                              On Error ◀─────────────────┘
                                      │
                               Rollback UI
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Offline-First deferred | MVP needs quick delivery | Full offline sync adds significant complexity; can be added iteratively |

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT secret mismatch | Auth fails completely | Validate shared secret in quickstart.md |
| CORS issues | API calls blocked | Already configured in FastAPI backend |
| Session expiry handling | Poor UX | Implement token refresh or redirect to login |
| Network errors | Data loss | Optimistic updates with rollback + error messages |
