# Data Model: TodoList Pro

**Feature Branch**: `002-todolist-pro-ui`
**Date**: 2025-12-30
**Status**: Complete

## Entity Overview

This document defines the data structures for the TodoList Pro UI. Since this is a UI-only implementation (TypeScript frontend), these models represent TypeScript interfaces that will be used throughout the application.

## Core Entities

### User

Represents a registered user account.

```typescript
interface User {
  id: string;              // Unique identifier (UUID)
  name: string;            // Full name (2-50 characters)
  email: string;           // Email address (unique, validated format)
  createdAt: Date;         // Account creation timestamp
  lastLoginAt: Date | null; // Last successful login timestamp
  avatarUrl?: string;      // Optional profile image URL
}
```

**Validation Rules**:
- `name`: Required, 2-50 characters, trimmed whitespace
- `email`: Required, valid email format (RFC 5322), case-insensitive uniqueness
- `id`: Auto-generated, immutable

**State Transitions**:
- Created → Active (on successful registration)
- Active → Active (on login, updates lastLoginAt)

---

### Task

Represents a todo item belonging to a user.

```typescript
interface Task {
  id: string;              // Unique identifier (UUID)
  userId: string;          // Owner reference (User.id)
  text: string;            // Task content (1-500 characters)
  completed: boolean;      // Completion status
  createdAt: Date;         // Creation timestamp
  updatedAt: Date;         // Last modification timestamp
  completedAt: Date | null; // Completion timestamp (null if incomplete)
  order: number;           // Display order within user's tasks
}
```

**Validation Rules**:
- `text`: Required, 1-500 characters, trimmed, sanitized for XSS
- `completed`: Default false
- `order`: Auto-assigned based on creation order

**State Transitions**:
```
Created (completed: false)
    ↓ toggle
Completed (completed: true, completedAt: now)
    ↓ toggle
Incomplete (completed: false, completedAt: null)
    ↓ delete
Deleted (soft-delete per constitution, 30-day recovery)
```

---

### Session

Represents an authenticated user session (for auth state management).

```typescript
interface Session {
  token: string;           // JWT or session token
  userId: string;          // Associated user ID
  expiresAt: Date;         // Session expiration timestamp
  createdAt: Date;         // Session creation timestamp
}
```

**Validation Rules**:
- `token`: Required, valid JWT format
- `expiresAt`: Must be in the future

---

## Form Data Types

### Registration Form

```typescript
interface RegistrationFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}
```

**Validation Schema (Zod)**:
```typescript
const registrationSchema = z.object({
  name: z.string()
    .min(2, "Name must be at least 2 characters")
    .max(50, "Name must be at most 50 characters")
    .trim(),
  email: z.string()
    .email("Please enter a valid email address")
    .toLowerCase(),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});
```

---

### Login Form

```typescript
interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}
```

**Validation Schema (Zod)**:
```typescript
const loginSchema = z.object({
  email: z.string()
    .email("Please enter a valid email address")
    .toLowerCase(),
  password: z.string()
    .min(1, "Password is required"),
  rememberMe: z.boolean().default(false),
});
```

---

### Task Form

```typescript
interface TaskFormData {
  text: string;
}

interface TaskUpdateData {
  text?: string;
  completed?: boolean;
}
```

**Validation Schema (Zod)**:
```typescript
const taskSchema = z.object({
  text: z.string()
    .min(1, "Task cannot be empty")
    .max(500, "Task must be at most 500 characters")
    .trim(),
});
```

---

## API Response Types

### Auth Responses

```typescript
interface AuthResponse {
  user: User;
  token: string;
  expiresAt: string; // ISO 8601 date string
}

interface AuthError {
  code: "INVALID_CREDENTIALS" | "EMAIL_EXISTS" | "VALIDATION_ERROR";
  message: string;
  field?: string; // For validation errors
}
```

---

### Task Responses

```typescript
interface TaskListResponse {
  tasks: Task[];
  total: number;
}

interface TaskResponse {
  task: Task;
}

interface TaskError {
  code: "NOT_FOUND" | "UNAUTHORIZED" | "VALIDATION_ERROR";
  message: string;
}
```

---

## UI State Types

### Auth Context State

```typescript
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

type AuthAction =
  | { type: "LOGIN_START" }
  | { type: "LOGIN_SUCCESS"; payload: User }
  | { type: "LOGIN_ERROR"; payload: string }
  | { type: "LOGOUT" }
  | { type: "RESTORE_SESSION"; payload: User };
```

---

### Task UI State

```typescript
interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  pendingDeletes: Set<string>; // Task IDs with active undo timers
}

interface OptimisticTask extends Task {
  _optimistic?: boolean; // Flag for optimistic updates
  _pendingAction?: "create" | "update" | "delete";
}
```

---

### Toast/Notification State

```typescript
interface Toast {
  id: string;
  type: "success" | "error" | "info" | "warning";
  title: string;
  description?: string;
  duration?: number; // milliseconds, default 5000
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

---

## Relationships

```
┌──────────┐         ┌──────────┐
│   User   │ 1─────N │   Task   │
│          │         │          │
│ id (PK)  │◄────────│ userId   │
│ name     │         │ id (PK)  │
│ email    │         │ text     │
│ ...      │         │ completed│
└──────────┘         │ ...      │
      │              └──────────┘
      │
      │ 1
      │
      ▼ N
┌──────────┐
│ Session  │
│          │
│ token    │
│ userId   │
│ ...      │
└──────────┘
```

## Data Flow

### Registration Flow
```
RegistrationFormData → validate → POST /api/auth/register → AuthResponse → AuthState
```

### Login Flow
```
LoginFormData → validate → POST /api/auth/login → AuthResponse → AuthState + Session storage
```

### Task CRUD Flow
```
TaskFormData → validate → POST /api/tasks → TaskResponse → TaskState (optimistic)
                                                  ↓
                                          Rollback on error
```

## Storage Strategy

### Client-Side (UI-Only Implementation)

| Data | Storage | Rationale |
|------|---------|-----------|
| Session Token | HTTP-only cookie (production) or localStorage (dev) | Security vs convenience |
| User Profile | React Context | Session lifetime only |
| Tasks | React State + localStorage cache | Optimistic updates, offline support |
| Form State | React Hook Form | Ephemeral, no persistence |

### Mock Data (Development)

For UI development without backend:
```typescript
const mockUsers: User[] = [...];
const mockTasks: Task[] = [...];

// localStorage keys
const STORAGE_KEYS = {
  AUTH_TOKEN: 'todolist_auth_token',
  USER: 'todolist_user',
  TASKS: 'todolist_tasks',
} as const;
```
