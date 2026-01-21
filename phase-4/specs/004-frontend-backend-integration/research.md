# Research: Frontend-Backend Integration

**Feature**: 004-frontend-backend-integration
**Date**: 2024-12-31

## Research Summary

This document captures technical research and decisions for integrating the Next.js frontend with the FastAPI backend using Better-Auth authentication.

---

## 1. Better-Auth Setup for Next.js

### Decision: Use Better-Auth with Bearer Plugin

**Rationale**: Better-Auth provides a modern, TypeScript-first authentication solution with built-in support for:
- Email/password authentication
- JWT Bearer tokens for API authentication
- Session management with cookie and token-based options

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| NextAuth.js | Widely used, mature | Complex migration path, less flexible for custom backends | Rejected |
| Auth.js v5 | Modern, well-documented | Different token handling, less suited for external APIs | Rejected |
| Better-Auth | TypeScript-first, Bearer plugin for external APIs, simpler config | Newer, smaller community | **Selected** |

### Configuration Approach

**Server-Side (`lib/auth.ts`)**:
```typescript
import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
  },
  database: {
    // Use Drizzle adapter with Neon PostgreSQL
    // OR use same Neon DB as backend
  },
  plugins: [bearer()],
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL,
});
```

**API Route (`app/api/auth/[...all]/route.ts`)**:
```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

**Client-Side (`lib/auth-client.ts`)**:
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  fetchOptions: {
    auth: {
      type: "Bearer",
      token: () => localStorage.getItem("bearer_token") || ""
    }
  }
});
```

### Bearer Token Flow

1. User signs in via Better-Auth
2. Token received in `set-auth-token` response header
3. Token stored in localStorage
4. Token included in Authorization header for FastAPI calls
5. FastAPI validates token using shared secret

**Source**: [Better-Auth Bearer Plugin](https://www.better-auth.com/docs/plugins/bearer)

---

## 2. Database Strategy

### Decision: Separate User Tables (Better-Auth) from Task Tables (FastAPI)

**Rationale**:
- Better-Auth manages its own user/session tables
- FastAPI backend already has Task table with `user_id` foreign key
- Both connect to same Neon PostgreSQL database
- User ID from JWT token links the two systems

**Schema Relationship**:
```
┌─────────────────────┐         ┌─────────────────────┐
│  Better-Auth Tables │         │   FastAPI Tables    │
├─────────────────────┤         ├─────────────────────┤
│  user               │◄────────│  tasks              │
│  ├─ id (PK)         │  FK     │  ├─ id (PK)         │
│  ├─ email           │         │  ├─ user_id ────────┤
│  ├─ name            │         │  ├─ text            │
│  └─ ...             │         │  ├─ completed       │
│                     │         │  └─ ...             │
│  session            │         │                     │
│  ├─ id              │         │                     │
│  ├─ userId          │         │                     │
│  └─ token           │         │                     │
└─────────────────────┘         └─────────────────────┘
```

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Single shared user table | Simpler FK relationship | Requires manual Better-Auth table setup | Rejected |
| Separate databases | Full isolation | Complex, unnecessary | Rejected |
| Same DB, separate tables | Clean separation, standard approach | Requires JWT user_id mapping | **Selected** |

---

## 3. API Client Architecture

### Decision: Custom Fetch Wrapper + TanStack Query

**Rationale**:
- TanStack Query provides caching, optimistic updates, and automatic refetching
- Custom fetch wrapper adds Bearer token to all requests
- Optimistic updates for instant UI feedback

**Implementation Pattern**:
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("bearer_token");

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.json());
  }

  return response.json();
}
```

**TanStack Query Setup**:
```typescript
// hooks/use-tasks.ts
export function useTasks() {
  return useQuery({
    queryKey: ["tasks"],
    queryFn: () => apiClient<TaskListResponse>("/tasks"),
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (text: string) =>
      apiClient<Task>("/tasks", {
        method: "POST",
        body: JSON.stringify({ text }),
      }),
    onMutate: async (text) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previous = queryClient.getQueryData(["tasks"]);
      queryClient.setQueryData(["tasks"], (old) => ({
        ...old,
        tasks: [{ id: "temp", text, completed: false }, ...old.tasks],
      }));
      return { previous };
    },
    onError: (err, text, context) => {
      // Rollback on error
      queryClient.setQueryData(["tasks"], context.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
```

**Source**: [TanStack Query Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)

---

## 4. Route Protection Strategy

### Decision: Middleware + Server Component Checks

**Rationale**:
- Middleware provides fast initial redirect for unauthenticated users
- Server component checks provide authoritative session validation
- Client hooks provide reactive UI updates

**Implementation Layers**:

1. **Middleware (fast, cookie-based)**:
```typescript
// middleware.ts
import { getSessionCookie } from "better-auth/cookies";

export async function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request);

  if (!sessionCookie && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}
```

2. **Server Component (authoritative)**:
```typescript
// app/(dashboard)/layout.tsx
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function DashboardLayout({ children }) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return <>{children}</>;
}
```

3. **Client Hook (reactive)**:
```typescript
// hooks/use-auth.ts
import { authClient } from "@/lib/auth-client";

export function useAuth() {
  const session = authClient.useSession();
  return {
    user: session.data?.user,
    isLoading: session.isPending,
    isAuthenticated: !!session.data,
  };
}
```

**Source**: [Better-Auth Next.js Integration](https://www.better-auth.com/docs/integrations/next)

---

## 5. Session & Token Management

### Decision: Dual Storage (Cookie + LocalStorage)

**Rationale**:
- Better-Auth session cookie for SSR/middleware
- Bearer token in localStorage for API calls
- Both synced on login/logout

**Token Lifecycle**:
```
Login:
  1. User submits credentials
  2. Better-Auth validates and creates session
  3. Session cookie set automatically
  4. Bearer token extracted from response header
  5. Token stored in localStorage

API Call:
  1. Retrieve token from localStorage
  2. Add to Authorization header
  3. FastAPI validates JWT with shared secret

Logout:
  1. Call authClient.signOut()
  2. Session cookie cleared
  3. Remove token from localStorage
  4. Redirect to home page
```

---

## 6. Error Handling Strategy

### Decision: Centralized Error Handler with User-Friendly Messages

**Error Types**:
| Error Code | User Message | Action |
|------------|--------------|--------|
| 401 | "Session expired. Please log in again." | Redirect to login |
| 403 | "You don't have permission for this action." | Show error toast |
| 404 | "Task not found." | Remove from cache |
| 422 | "Invalid input. Please check your data." | Show validation errors |
| 500 | "Something went wrong. Please try again." | Show retry button |
| Network | "Unable to connect. Check your internet." | Show offline indicator |

**Implementation**:
```typescript
// lib/api.ts
export class ApiError extends Error {
  constructor(public status: number, public data: any) {
    super(data.detail || "An error occurred");
  }
}

// Error boundary or hook
function handleApiError(error: ApiError) {
  if (error.status === 401) {
    localStorage.removeItem("bearer_token");
    window.location.href = "/login?expired=true";
  }
  // ... other handlers
}
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| better-auth | ^1.x | Authentication framework |
| @tanstack/react-query | ^5.x | Data fetching and caching |
| zod | ^3.x | Schema validation (existing) |
| react-hook-form | ^7.x | Form handling (existing) |

---

## References

- [Better-Auth Installation](https://www.better-auth.com/docs/installation)
- [Better-Auth Next.js Integration](https://www.better-auth.com/docs/integrations/next)
- [Better-Auth Bearer Plugin](https://www.better-auth.com/docs/plugins/bearer)
- [TanStack Query Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)
- [TanStack Query Mutations](https://tanstack.com/query/latest/docs/framework/react/guides/mutations)
