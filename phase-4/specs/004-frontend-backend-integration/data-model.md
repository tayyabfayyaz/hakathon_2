# Data Model: Frontend-Backend Integration

**Feature**: 004-frontend-backend-integration
**Date**: 2024-12-31

## Overview

This document defines the data model for the frontend-backend integration, focusing on how data flows between the Next.js frontend, Better-Auth authentication, and the FastAPI backend.

---

## Entities

### 1. User (Better-Auth Managed)

The User entity is managed by Better-Auth and stored in the Neon PostgreSQL database.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | string (UUID) | Unique user identifier | Primary Key, auto-generated |
| email | string | User's email address | Unique, required, max 255 chars |
| name | string | User's display name | Required, min 1, max 100 chars |
| emailVerified | boolean | Whether email is verified | Default: false |
| image | string? | Avatar URL | Optional |
| createdAt | datetime | Account creation timestamp | Auto-generated |
| updatedAt | datetime | Last update timestamp | Auto-updated |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Name must be 1-100 characters
- Password (handled separately by Better-Auth): min 8 chars, uppercase, lowercase, number

### 2. Session (Better-Auth Managed)

The Session entity tracks active user sessions.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | string (UUID) | Session identifier | Primary Key |
| userId | string (UUID) | Reference to User | Foreign Key |
| token | string | Session token | Unique, indexed |
| expiresAt | datetime | Session expiry time | Required |
| ipAddress | string? | Client IP | Optional |
| userAgent | string? | Browser info | Optional |
| createdAt | datetime | Session start | Auto-generated |
| updatedAt | datetime | Last activity | Auto-updated |

**Session Lifecycle**:
- Created on successful login
- Updated on each authenticated request
- Expires after 7 days of inactivity
- Deleted on logout

### 3. Task (FastAPI Backend Managed)

The Task entity is managed by the FastAPI backend (already implemented).

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID (v7) | Unique task identifier | Primary Key, time-ordered |
| user_id | string | Owner's user ID | Foreign Key (logical), indexed |
| text | string | Task description | Required, 1-500 chars |
| completed | boolean | Completion status | Default: false |
| order | integer | Display order | Default: 0 |
| created_at | datetime | Creation timestamp | Auto-generated |
| updated_at | datetime | Last update | Auto-updated |
| completed_at | datetime? | When marked complete | Set on completion |

**Validation Rules**:
- Text: 1-500 characters, trimmed
- User can only access their own tasks
- completed_at set when completed=true, cleared when false

---

## State Transitions

### Task State Machine

```
                    ┌─────────────────┐
                    │    CREATED      │
                    │  completed=false│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │  EDITED  │   │ COMPLETED│   │ DELETED  │
       │  text    │   │ completed│   │          │
       │  changed │   │  =true   │   │ (removed)│
       └────┬─────┘   └────┬─────┘   └──────────┘
            │              │
            │              ▼
            │        ┌──────────┐
            └───────▶│UNCOMPLETED
                     │completed │
                     │ =false   │
                     └──────────┘
```

### Session State Machine

```
     ┌─────────────┐        ┌─────────────┐
     │  LOGGED_OUT │───────▶│  LOGGING_IN │
     │  (no token) │        │  (pending)  │
     └─────────────┘        └──────┬──────┘
            ▲                      │
            │              success │ failure
            │                      ▼        ▼
            │              ┌──────────┐  ┌───────┐
            │              │LOGGED_IN │  │ ERROR │
            │              │(has token│  │       │
            │              └────┬─────┘  └───────┘
            │                   │
            │    logout/expired │
            └───────────────────┘
```

---

## Frontend State Shape

### Auth State

```typescript
interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface User {
  id: string;
  email: string;
  name: string;
  image?: string;
}

interface Session {
  token: string;
  expiresAt: Date;
}
```

### Tasks State (TanStack Query Cache)

```typescript
interface TasksQueryData {
  tasks: Task[];
  count: number;
}

interface Task {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
  completedAt: Date | null;
}

// Query Key Structure
["tasks"]                    // All tasks for current user
["tasks", taskId]           // Single task (optional, for detail view)
```

### UI State

```typescript
interface UIState {
  // Task editing
  editingTaskId: string | null;
  editingText: string;

  // Delete confirmation
  deleteDialogOpen: boolean;
  taskToDelete: Task | null;

  // Loading states
  isCreating: boolean;
  isUpdating: Record<string, boolean>;
  isDeleting: Record<string, boolean>;

  // Error states
  error: string | null;
}
```

---

## Data Flow Diagrams

### Login Flow

```
User                  Frontend               Better-Auth              Backend
  │                      │                        │                      │
  │  Submit credentials  │                        │                      │
  ├─────────────────────▶│                        │                      │
  │                      │   POST /api/auth/...   │                      │
  │                      ├───────────────────────▶│                      │
  │                      │                        │  Validate + Create   │
  │                      │                        │  Session             │
  │                      │   Session + Token      │                      │
  │                      │◀───────────────────────┤                      │
  │                      │                        │                      │
  │                      │  Store token locally   │                      │
  │                      │  Redirect to dashboard │                      │
  │  Dashboard loaded    │                        │                      │
  │◀─────────────────────┤                        │                      │
  │                      │                        │                      │
  │                      │  GET /tasks (Bearer)   │                      │
  │                      ├───────────────────────────────────────────────▶│
  │                      │                        │    Validate JWT      │
  │                      │                        │    Return tasks      │
  │                      │  Task list             │                      │
  │◀─────────────────────┼◀──────────────────────────────────────────────┤
```

### Task CRUD Flow (Optimistic Update)

```
User                  Frontend               TanStack Query           Backend
  │                      │                        │                      │
  │  Create task         │                        │                      │
  ├─────────────────────▶│                        │                      │
  │                      │  Optimistic update     │                      │
  │                      ├───────────────────────▶│                      │
  │  UI updates instantly│                        │                      │
  │◀─────────────────────┤                        │                      │
  │                      │                        │  POST /tasks         │
  │                      │                        ├─────────────────────▶│
  │                      │                        │                      │
  │                      │                        │  201 Created         │
  │                      │                        │◀─────────────────────┤
  │                      │  Invalidate + refetch  │                      │
  │                      │◀───────────────────────┤                      │
  │  Final UI state      │                        │                      │
  │◀─────────────────────┤                        │                      │

Error Case:
  │                      │                        │  500 Error           │
  │                      │                        │◀─────────────────────┤
  │                      │  Rollback cache        │                      │
  │                      │◀───────────────────────┤                      │
  │  UI reverts + error  │                        │                      │
  │◀─────────────────────┤                        │                      │
```

---

## Validation Schema (Zod)

```typescript
// schemas/auth.ts
import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
});

export const registrationSchema = z.object({
  name: z.string().min(1, "Name is required").max(100, "Name too long"),
  email: z.string().email("Invalid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain uppercase letter")
    .regex(/[a-z]/, "Password must contain lowercase letter")
    .regex(/[0-9]/, "Password must contain a number"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// schemas/task.ts
export const taskSchema = z.object({
  text: z
    .string()
    .min(1, "Task cannot be empty")
    .max(500, "Task is too long")
    .transform((s) => s.trim()),
});

export const taskUpdateSchema = z.object({
  text: z.string().min(1).max(500).optional(),
  completed: z.boolean().optional(),
});
```

---

## Type Definitions

```typescript
// types/index.ts

// Auth Types
export interface User {
  id: string;
  email: string;
  name: string;
  image?: string | null;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: Date;
}

// Task Types (aligned with FastAPI backend)
export interface Task {
  id: string;
  userId: string;
  text: string;
  completed: boolean;
  order: number;
  createdAt: Date;
  updatedAt: Date;
  completedAt: Date | null;
}

export interface TaskCreate {
  text: string;
}

export interface TaskUpdate {
  text: string;
  completed: boolean;
}

export interface TaskPatch {
  text?: string;
  completed?: boolean;
}

// API Response Types
export interface TaskListResponse {
  tasks: Task[];
  count: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}
```
