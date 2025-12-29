# Quickstart: Better Auth JWT Implementation

## Prerequisites

- Node.js 18+ (for Next.js frontend)
- Python 3.11+ (for FastAPI backend)
- PostgreSQL database (Neon DB)
- Existing TodoList Pro codebase

## Step 1: Install Dependencies

### Frontend (Next.js)

```bash
cd frontend
npm install better-auth
```

### Backend (FastAPI)

No new dependencies required - uses existing `python-jose` for JWT verification.

## Step 2: Configure Better Auth

### Create auth configuration (`frontend/lib/auth.ts`)

```typescript
import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
});
```

### Create auth client (`frontend/lib/auth-client.ts`)

```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
```

## Step 3: Create API Routes

### Auth handler (`frontend/app/api/auth/[...all]/route.ts`)

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { POST, GET } = toNextJsHandler(auth);
```

## Step 4: Update FastAPI JWT Verification

### Update security module (`backend/src/core/security.py`)

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Use the same secret as Better Auth
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"

def verify_better_auth_token(token: str) -> dict:
    """Verify a JWT token from Better Auth."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOKEN", "message": "Invalid authentication token"}
        )
```

### Update dependencies (`backend/src/api/deps.py`)

```python
from fastapi import Depends, HTTPException, status, Cookie, Header
from typing import Optional

async def get_current_user(
    access_token: Optional[str] = Cookie(None, alias="better-auth.session_token"),
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract and verify user from Better Auth JWT token."""
    token = None

    # Try cookie first, then Authorization header
    if access_token:
        token = access_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "MISSING_TOKEN", "message": "Authentication required"}
        )

    payload = verify_better_auth_token(token)
    user_id = payload.get("sub")

    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "USER_NOT_FOUND", "message": "User not found"}
        )

    return user
```

## Step 5: Environment Variables

### Shared Secret (both services)

```bash
# Generate a secure secret
openssl rand -base64 32

# Add to .env files
BETTER_AUTH_SECRET=your-generated-secret-here
```

### Frontend `.env.local`

```bash
DATABASE_URL=postgresql://...@your-neon-db
BETTER_AUTH_SECRET=your-generated-secret-here
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend `.env`

```bash
BETTER_AUTH_SECRET=your-generated-secret-here
# ... other existing variables
```

## Step 6: Database Migration

Better Auth will create required tables on first run. To migrate existing users:

```sql
-- Run after Better Auth tables are created
INSERT INTO "user" (id, email, name, "emailVerified", "createdAt", "updatedAt")
SELECT
    id::text,
    email,
    email,  -- Use email as name initially
    true,
    created_at,
    updated_at
FROM users;

INSERT INTO account (id, "userId", "accountId", "providerId", password, "createdAt", "updatedAt")
SELECT
    gen_random_uuid()::text,
    id::text,
    id::text,
    'credential',
    password_hash,
    created_at,
    updated_at
FROM users;
```

## Step 7: Update Frontend Components

### Login Form Example

```typescript
"use client";

import { signIn } from "@/lib/auth-client";
import { useState } from "react";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await signIn.email({ email, password });

    if (result.error) {
      setError(result.error.message);
    } else {
      // Redirect to dashboard
      window.location.href = "/tasks";
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

## Step 8: Test the Integration

1. Start frontend: `cd frontend && npm run dev`
2. Start backend: `cd backend && uvicorn main:app --reload`
3. Register a new user via the frontend
4. Verify JWT cookie is set in browser
5. Access `/tasks` and verify FastAPI receives and validates token

## Troubleshooting

| Issue | Solution |
|-------|----------|
| JWT verification fails | Ensure BETTER_AUTH_SECRET matches in both services |
| Cookie not sent | Check SameSite and Secure settings for your environment |
| CORS errors | Configure FastAPI CORS to allow credentials |
| User not found | Run migration script to sync existing users |

## Next Steps

After basic auth works:

1. Add session refresh logic
2. Implement logout across all devices
3. Add password change with token invalidation
4. Set up proper production cookie settings
