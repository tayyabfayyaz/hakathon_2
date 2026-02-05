---
name: frontend-auth
description: Authentication patterns using Better-Auth, session management, and protected routes. Use when implementing login, logout, registration, auth middleware, or checking user sessions.
argument-hint: "[action]"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Authentication with Better-Auth

Implement authentication following the TodoList Pro patterns.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│    Frontend     │────▶│   Better-Auth    │────▶│  PostgreSQL │
│   (Next.js)     │     │   (API Routes)   │     │  (Sessions) │
└─────────────────┘     └──────────────────┘     └─────────────┘
        │                        │
        │                        ▼
        │               ┌──────────────────┐
        └──────────────▶│  Backend API     │
          Bearer Token  │  (FastAPI)       │
                        └──────────────────┘
```

## Key Files

```
frontend/src/
├── lib/
│   ├── auth.ts           # Server-side auth config
│   └── auth-client.ts    # Client-side auth
├── app/
│   └── api/
│       ├── auth/[...all]/route.ts  # Auth API routes
│       └── token/route.ts          # Bearer token endpoint
└── middleware.ts         # Route protection
```

## Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { bearer } from "better-auth/plugins";
import { Pool } from "@neondatabase/serverless";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },

  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  plugins: [bearer()],

  trustedOrigins: [
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL!,
    process.env.NEXT_PUBLIC_API_URL!,
  ],
});
```

## Client Configuration

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

## API Routes

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

```typescript
// app/api/token/route.ts
import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function POST() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const token = await auth.api.signInWithBearer({
    userId: session.user.id,
  });

  return NextResponse.json({ token: token.token });
}
```

## Middleware (Route Protection)

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = ["/dashboard", "/chat"];
const authRoutes = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get("better-auth.session_token");
  const { pathname } = request.nextUrl;

  // Redirect to login if accessing protected route without session
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!sessionCookie) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirect to dashboard if accessing auth routes with session
  if (authRoutes.includes(pathname)) {
    if (sessionCookie) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/chat/:path*", "/login", "/register"],
};
```

## Auth Hook

```typescript
// hooks/use-auth.ts
"use client";

import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

export function useAuth() {
  const { data: session, isPending: isLoading, error } = useSession();
  const router = useRouter();

  const logout = useCallback(async () => {
    localStorage.removeItem("bearer_token");
    await fetch("/api/auth/sign-out", { method: "POST" });
    router.push("/login");
  }, [router]);

  return {
    user: session?.user ?? null,
    session: session?.session ?? null,
    isLoading,
    isAuthenticated: !!session?.user,
    error,
    logout,
  };
}
```

## Sign In Flow

```typescript
"use client";

import { authClient } from "@/lib/auth-client";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();

  const handleSubmit = async (data: LoginFormData) => {
    try {
      // 1. Sign in with Better-Auth
      await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });

      // 2. Get bearer token for API calls
      const tokenResponse = await fetch("/api/auth/token", {
        method: "POST",
        credentials: "include",
      });
      const { token } = await tokenResponse.json();
      localStorage.setItem("bearer_token", token);

      // 3. Redirect to dashboard
      router.push("/dashboard");
    } catch (error: any) {
      setError(error.message);
    }
  };
}
```

## Sign Up Flow

```typescript
const handleRegister = async (data: RegisterFormData) => {
  try {
    await authClient.signUp.email({
      name: data.name,
      email: data.email,
      password: data.password,
    });

    // Auto sign-in after registration
    await authClient.signIn.email({
      email: data.email,
      password: data.password,
    });

    // Get bearer token
    const tokenResponse = await fetch("/api/auth/token", {
      method: "POST",
      credentials: "include",
    });
    const { token } = await tokenResponse.json();
    localStorage.setItem("bearer_token", token);

    router.push("/dashboard");
  } catch (error: any) {
    setError(error.message);
  }
};
```

## Protected Layout (Server Component)

```typescript
// app/(dashboard)/layout.tsx
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return <div className="dashboard-layout">{children}</div>;
}
```

## Displaying User Info

```typescript
"use client";

import { useAuth } from "@/hooks/use-auth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function UserMenu() {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) return <Skeleton className="h-8 w-8 rounded-full" />;
  if (!user) return null;

  const initials = user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <div className="flex items-center gap-2">
      <Avatar>
        <AvatarFallback>{initials}</AvatarFallback>
      </Avatar>
      <span>{user.name}</span>
      <Button variant="ghost" onClick={logout}>
        Logout
      </Button>
    </div>
  );
}
```

## Environment Variables

```env
# .env.local
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Best Practices

1. **Use server components** for initial auth checks
2. **Store bearer token** in localStorage for API calls
3. **Clear token on logout** and 401 responses
4. **Use middleware** for route protection
5. **Handle callback URLs** for post-login redirect
6. **Show loading states** during auth checks
