# Quickstart: Frontend-Backend Integration

**Feature**: 004-frontend-backend-integration
**Date**: 2024-12-31

## Prerequisites

Before starting implementation, ensure you have:

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Neon PostgreSQL database provisioned
- [ ] Backend from `003-fastapi-tasks-api` branch working

## Environment Setup

### 1. Shared Secret Configuration

**CRITICAL**: Both frontend and backend MUST use the same `BETTER_AUTH_SECRET` for JWT token validation.

Generate a secret (if not already done):
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 2. Backend Configuration

File: `backend/.env`
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:xxxxx@ep-xxx.neon.tech/neondb?ssl=require
BETTER_AUTH_SECRET=<your-shared-secret>
CORS_ORIGINS=http://localhost:3000
API_VERSION=1.0.0
DEBUG=true
```

### 3. Frontend Configuration

File: `todolist-pro/.env.local`
```env
# Better-Auth
BETTER_AUTH_SECRET=<your-shared-secret>
BETTER_AUTH_URL=http://localhost:3000

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database (for Better-Auth session storage)
DATABASE_URL=postgresql://neondb_owner:xxxxx@ep-xxx.neon.tech/neondb?sslmode=require
```

## Installation Steps

### Step 1: Install Frontend Dependencies

```bash
cd todolist-pro
npm install better-auth @tanstack/react-query
```

### Step 2: Run Database Migrations

Better-Auth needs its own tables. Run:
```bash
npx @better-auth/cli migrate
```

This creates the following tables in Neon:
- `user` - User accounts
- `session` - Active sessions
- `verification` - Email verification tokens (optional)

### Step 3: Start Both Services

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd todolist-pro
npm run dev
```

## File Structure After Integration

```
todolist-pro/
├── src/
│   ├── lib/
│   │   ├── auth.ts              # NEW: Better-Auth server config
│   │   ├── auth-client.ts       # NEW: Better-Auth client
│   │   └── api.ts               # NEW: API client with auth
│   ├── hooks/
│   │   ├── use-auth.ts          # NEW: Auth hook
│   │   └── use-tasks.ts         # NEW: Tasks hook
│   ├── components/
│   │   ├── providers/
│   │   │   └── query-provider.tsx  # NEW: TanStack Query provider
│   │   ├── auth/
│   │   │   ├── login-form.tsx   # UPDATED: Real auth
│   │   │   └── register-form.tsx # UPDATED: Real auth
│   │   └── tasks/
│   │       ├── task-list.tsx    # UPDATED: Real data
│   │       └── task-input.tsx   # UPDATED: Real mutations
│   └── app/
│       ├── api/
│       │   └── auth/
│       │       └── [...all]/
│       │           └── route.ts  # NEW: Better-Auth handler
│       └── (dashboard)/
│           └── layout.tsx        # UPDATED: Auth protection
```

## Key Implementation Files

### 1. Better-Auth Server (`src/lib/auth.ts`)

```typescript
import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
  },
  plugins: [bearer()],
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // Update every 24 hours
  },
});
```

### 2. API Route Handler (`src/app/api/auth/[...all]/route.ts`)

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 3. Auth Client (`src/lib/auth-client.ts`)

```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "",
});
```

### 4. API Client (`src/lib/api.ts`)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, public data: any) {
    super(data.detail || "An error occurred");
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("bearer_token")
    : null;

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}
```

## Testing the Integration

### 1. Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","version":"1.0.0"}
```

### 2. Register User

```bash
curl -X POST http://localhost:3000/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234","name":"Test User"}'
```

### 3. Login and Get Token

```bash
curl -X POST http://localhost:3000/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}' \
  -v  # Look for set-auth-token header
```

### 4. Create Task with Token

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token-from-login>" \
  -d '{"text":"My first task"}'
```

## Common Issues

### Issue: 401 Unauthorized from FastAPI

**Cause**: JWT token not being validated correctly

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches in both `.env` files
2. Check token is being sent in Authorization header
3. Verify token hasn't expired

### Issue: CORS Error

**Cause**: Backend not allowing frontend origin

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
2. Restart FastAPI server after changing `.env`

### Issue: Session Cookie Not Set

**Cause**: Missing secure cookie configuration

**Solution**:
1. Ensure `BETTER_AUTH_URL` is set correctly
2. For localhost, cookies work without HTTPS
3. For production, ensure HTTPS is used

### Issue: Better-Auth Tables Missing

**Cause**: Migrations not run

**Solution**:
```bash
cd todolist-pro
npx @better-auth/cli migrate
```

## Verification Checklist

After implementation, verify:

- [ ] User can register with email/password
- [ ] User can login and is redirected to dashboard
- [ ] Dashboard shows empty state for new user
- [ ] User can create a task
- [ ] Task persists after page refresh
- [ ] User can toggle task completion
- [ ] User can edit task text
- [ ] User can delete task with confirmation
- [ ] User can logout and is redirected to home
- [ ] Unauthenticated access to /dashboard redirects to /login
- [ ] Different users see only their own tasks

## Next Steps

After verifying the quickstart:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks following TDD approach
3. Run E2E tests to verify all flows
