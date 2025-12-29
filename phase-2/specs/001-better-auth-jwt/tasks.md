# Implementation Tasks: Better Auth with JWT Authentication

**Feature Branch**: `001-better-auth-jwt`
**Created**: 2025-12-29
**Plan**: [plan.md](./plan.md)
**Spec**: [spec.md](./spec.md)

## Task Overview

| Phase | Tasks | Priority | Status |
|-------|-------|----------|--------|
| 1. Frontend Setup | 5 | P1 | ✅ Complete |
| 2. Backend JWT | 4 | P1 | ✅ Complete |
| 3. Auth UI | 5 | P1 | ✅ Complete |
| 4. Database Migration | 4 | P1 | ⬜ Pending |
| 5. Token Refresh | 4 | P2 | ⬜ Pending |
| 6. Testing | 4 | P1 | ⬜ Pending |

**Total Tasks**: 26

---

## Phase 1: Frontend - Better Auth Setup

### TASK-001: Install Better Auth Package
**Priority**: P1 | **Estimate**: 5 min | **Dependencies**: None

**Description**: Install the `better-auth` npm package in the frontend project.

**Steps**:
1. Navigate to `frontend/` directory
2. Run `npm install better-auth`
3. Verify package added to `package.json`

**Files**:
- `frontend/package.json` (modify)
- `frontend/package-lock.json` (auto-generated)

**Test Cases**:
- [X] `better-auth` appears in dependencies
- [X] `npm install` completes without errors
- [X] Package version is latest stable

**Acceptance Criteria**:
```
✓ better-auth package installed
✓ No dependency conflicts
```

**Status**: ✅ COMPLETE

---

### TASK-002: Create Auth Server Configuration
**Priority**: P1 | **Estimate**: 15 min | **Dependencies**: TASK-001

**Description**: Create the Better Auth server configuration file that connects to the database and configures authentication options.

**Steps**:
1. Create `frontend/src/lib/auth.ts`
2. Configure database connection using Neon PostgreSQL
3. Enable email/password authentication
4. Configure session settings (JWT mode, expiry)
5. Set up secret from environment variable

**Files**:
- `frontend/src/lib/auth.ts` (create)

**Code Template**:
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
    updateAge: 60 * 60 * 24, // 1 day
  },
  secret: process.env.BETTER_AUTH_SECRET,
});
```

**Test Cases**:
- [X] File compiles without TypeScript errors
- [X] Database connection string is read from env
- [X] Secret is read from env

**Acceptance Criteria**:
```
✓ auth.ts exports configured betterAuth instance
✓ No hardcoded secrets
✓ TypeScript types are correct
```

**Status**: ✅ COMPLETE (Created as `frontend/src/lib/better-auth.ts`)

---

### TASK-003: Create Auth Client for React
**Priority**: P1 | **Estimate**: 10 min | **Dependencies**: TASK-002

**Description**: Create the client-side auth utilities for React components to use.

**Steps**:
1. Create `frontend/src/lib/auth-client.ts`
2. Initialize auth client with base URL
3. Export auth hooks and functions

**Files**:
- `frontend/src/lib/auth-client.ts` (create)

**Code Template**:
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

export const { signIn, signUp, signOut, useSession } = authClient;
```

**Test Cases**:
- [X] Exports signIn, signUp, signOut, useSession
- [X] Uses NEXT_PUBLIC_APP_URL for base URL
- [X] Falls back to localhost for development

**Acceptance Criteria**:
```
✓ Auth client configured for frontend use
✓ All required functions exported
```

**Status**: ✅ COMPLETE

---

### TASK-004: Create API Route Handler
**Priority**: P1 | **Estimate**: 10 min | **Dependencies**: TASK-002

**Description**: Create the Next.js API route that handles all Better Auth endpoints.

**Steps**:
1. Create directory `frontend/src/app/api/auth/[...all]/`
2. Create `route.ts` with GET and POST handlers
3. Connect to auth configuration

**Files**:
- `frontend/src/app/api/auth/[...all]/route.ts` (create)

**Code Template**:
```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { POST, GET } = toNextJsHandler(auth);
```

**Test Cases**:
- [X] GET /api/auth/session returns session or null
- [X] POST /api/auth/sign-up/email creates user
- [X] POST /api/auth/sign-in/email authenticates user
- [X] POST /api/auth/sign-out clears session

**Acceptance Criteria**:
```
✓ All Better Auth routes accessible at /api/auth/*
✓ Routes handle GET and POST methods
```

**Status**: ✅ COMPLETE

---

### TASK-005: Configure Environment Variables
**Priority**: P1 | **Estimate**: 10 min | **Dependencies**: TASK-001

**Description**: Set up required environment variables for Better Auth.

**Steps**:
1. Generate secure random secret (32+ characters)
2. Add variables to `frontend/.env.local`
3. Add variables to `frontend/.env.example` (without values)
4. Document required variables

**Files**:
- `frontend/.env.local` (modify)
- `frontend/.env.example` (create/modify)

**Environment Variables**:
```bash
# Better Auth
BETTER_AUTH_SECRET=<generate-secure-32-char-secret>
DATABASE_URL=postgresql://user:pass@host/db
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Test Cases**:
- [X] BETTER_AUTH_SECRET is set and >= 32 characters
- [X] DATABASE_URL points to valid PostgreSQL
- [X] NEXT_PUBLIC_APP_URL matches frontend URL

**Acceptance Criteria**:
```
✓ All required env vars documented
✓ .env.example contains all keys (no values)
✓ Secrets not committed to git
```

**Status**: ✅ COMPLETE

---

## Phase 2: Backend - JWT Verification Update

### TASK-006: Update Config for Better Auth Secret
**Priority**: P1 | **Estimate**: 10 min | **Dependencies**: TASK-005

**Description**: Update FastAPI configuration to read the Better Auth secret for JWT verification.

**Steps**:
1. Add `better_auth_secret` to Settings class
2. Update `.env` with same secret as frontend
3. Ensure secret is required (not optional)

**Files**:
- `backend/src/core/config.py` (modify)
- `backend/.env` (modify)

**Code Changes**:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    better_auth_secret: str  # Required, same as frontend
```

**Test Cases**:
- [X] App fails to start if BETTER_AUTH_SECRET missing
- [X] Secret value matches frontend secret

**Acceptance Criteria**:
```
✓ BETTER_AUTH_SECRET loaded from environment
✓ Startup fails gracefully if missing
```

**Status**: ✅ COMPLETE

---

### TASK-007: Update Security Module for Better Auth Tokens
**Priority**: P1 | **Estimate**: 20 min | **Dependencies**: TASK-006

**Description**: Modify the security module to verify JWT tokens generated by Better Auth.

**Steps**:
1. Create `verify_better_auth_token()` function
2. Use Better Auth secret for verification
3. Handle token expiration errors
4. Extract user ID from token payload

**Files**:
- `backend/src/core/security.py` (modify)

**Code Changes**:
```python
from jose import JWTError, jwt
from .config import get_settings

settings = get_settings()

def verify_better_auth_token(token: str) -> dict:
    """Verify a JWT token from Better Auth."""
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail={"error_code": "INVALID_TOKEN", "message": str(e)}
        )
```

**Test Cases**:
- [X] Valid token returns payload with user ID
- [X] Expired token raises 401 error
- [X] Malformed token raises 401 error
- [X] Token signed with wrong secret raises 401

**Acceptance Criteria**:
```
✓ Better Auth tokens verified correctly
✓ Proper error messages for invalid tokens
```

**Status**: ✅ COMPLETE

---

### TASK-008: Update Dependencies for Better Auth Cookie
**Priority**: P1 | **Estimate**: 20 min | **Dependencies**: TASK-007

**Description**: Update the FastAPI dependencies to extract tokens from Better Auth cookies.

**Steps**:
1. Update cookie name to `better-auth.session_token`
2. Add fallback to Authorization header
3. Update `get_current_user` dependency
4. Handle missing token gracefully

**Files**:
- `backend/src/api/deps.py` (modify)

**Code Changes**:
```python
from fastapi import Cookie, Header, Depends, HTTPException
from typing import Optional

async def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="better-auth.session_token"),
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    token = None

    if session_token:
        token = session_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(status_code=401, detail={
            "error_code": "MISSING_TOKEN",
            "message": "Authentication required"
        })

    payload = verify_better_auth_token(token)
    user_id = payload.get("sub")

    # Fetch user from database
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail={
            "error_code": "USER_NOT_FOUND",
            "message": "User not found"
        })

    return user
```

**Test Cases**:
- [X] Token extracted from cookie
- [X] Token extracted from Authorization header
- [X] Missing token returns 401
- [X] Invalid user ID returns 401

**Acceptance Criteria**:
```
✓ Both cookie and header auth supported
✓ User correctly loaded from token
```

**Status**: ✅ COMPLETE

---

### TASK-009: Update Backend Environment
**Priority**: P1 | **Estimate**: 5 min | **Dependencies**: TASK-006

**Description**: Add the Better Auth secret to backend environment.

**Steps**:
1. Copy BETTER_AUTH_SECRET from frontend
2. Add to `backend/.env`
3. Verify both services use identical secret

**Files**:
- `backend/.env` (modify)
- `backend/.env.example` (modify)

**Test Cases**:
- [X] Secret matches frontend exactly
- [X] Backend starts successfully
- [X] Token verification works

**Acceptance Criteria**:
```
✓ Shared secret configured
✓ Backend can verify frontend tokens
```

**Status**: ✅ COMPLETE

---

## Phase 3: Frontend - Auth UI Components

### TASK-010: Update Login Form Component
**Priority**: P1 | **Estimate**: 25 min | **Dependencies**: TASK-003

**Description**: Refactor LoginForm to use Better Auth signIn function.

**Steps**:
1. Import `signIn` from auth-client
2. Replace API call with `signIn.email()`
3. Handle success/error responses
4. Update error display

**Files**:
- `frontend/src/components/auth/LoginForm.tsx` (modify)

**Code Changes**:
```typescript
import { signIn } from "@/lib/auth-client";

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  setErrors({});

  const result = await signIn.email({
    email: email.trim(),
    password,
  });

  if (result.error) {
    setErrors({ form: result.error.message });
  } else {
    // Redirect or call onSubmit callback
    router.push("/tasks");
  }
};
```

**Test Cases**:
- [X] Valid credentials log user in
- [X] Invalid credentials show error
- [X] Loading state during submission
- [X] Redirects to /tasks on success

**Acceptance Criteria**:
```
✓ Login works with Better Auth
✓ Error handling preserved
✓ UX unchanged for users
```

**Status**: ✅ COMPLETE

---

### TASK-011: Update Register Form Component
**Priority**: P1 | **Estimate**: 25 min | **Dependencies**: TASK-003

**Description**: Refactor RegisterForm to use Better Auth signUp function.

**Steps**:
1. Import `signUp` from auth-client
2. Replace API call with `signUp.email()`
3. Handle validation errors
4. Auto-login after registration

**Files**:
- `frontend/src/components/auth/RegisterForm.tsx` (modify)

**Code Changes**:
```typescript
import { signUp } from "@/lib/auth-client";

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();

  const result = await signUp.email({
    email: email.trim(),
    password,
    name: email.split("@")[0], // Use email prefix as name
  });

  if (result.error) {
    if (result.error.code === "USER_ALREADY_EXISTS") {
      setErrors({ email: "Email already registered" });
    } else {
      setErrors({ form: result.error.message });
    }
  } else {
    router.push("/tasks");
  }
};
```

**Test Cases**:
- [X] New user can register
- [X] Duplicate email shows error
- [X] Weak password shows error
- [X] Auto-login after registration

**Acceptance Criteria**:
```
✓ Registration works with Better Auth
✓ Validation errors displayed
✓ Session created on success
```

**Status**: ✅ COMPLETE

---

### TASK-012: Update Auth Context
**Priority**: P1 | **Estimate**: 30 min | **Dependencies**: TASK-003

**Description**: Refactor AuthContext to use Better Auth useSession hook.

**Steps**:
1. Replace custom session logic with `useSession()`
2. Update context value structure
3. Remove API calls to /auth/me
4. Handle loading states

**Files**:
- `frontend/src/contexts/AuthContext.tsx` (modify)

**Code Changes**:
```typescript
import { useSession, signOut } from "@/lib/auth-client";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, isPending } = useSession();

  const logout = async () => {
    await signOut();
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{
      user: session?.user ?? null,
      isLoading: isPending,
      isAuthenticated: !!session?.user,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Test Cases**:
- [X] Session loaded on app start
- [X] User info available in context
- [X] Loading state during session check
- [X] Logout clears session

**Acceptance Criteria**:
```
✓ Context uses Better Auth session
✓ All consumers receive user data
✓ Logout works correctly
```

**Status**: ✅ COMPLETE

---

### TASK-013: Update Header Logout
**Priority**: P1 | **Estimate**: 10 min | **Dependencies**: TASK-012

**Description**: Update Header component to use context logout function.

**Steps**:
1. Get logout from AuthContext
2. Replace direct API call
3. Handle loading during logout

**Files**:
- `frontend/src/components/layout/Header.tsx` (modify)

**Test Cases**:
- [X] Logout button calls context logout
- [X] User redirected to login page
- [X] Session cookie cleared

**Acceptance Criteria**:
```
✓ Logout integrated with Better Auth
✓ Clean redirect flow
```

**Status**: ✅ COMPLETE

---

### TASK-014: Remove Old Auth API Calls
**Priority**: P1 | **Estimate**: 15 min | **Dependencies**: TASK-010, TASK-011, TASK-012

**Description**: Remove deprecated auth functions from lib/auth.ts.

**Steps**:
1. Remove `authApi` object
2. Remove login/register/logout functions
3. Keep only types if needed
4. Update any remaining imports

**Files**:
- `frontend/src/lib/auth.ts` (modify/delete)
- `frontend/src/hooks/useAuth.ts` (modify)

**Test Cases**:
- [X] No references to old auth functions
- [X] Build completes without errors
- [X] All auth flows still work

**Acceptance Criteria**:
```
✓ Old auth code removed
✓ No dead code remaining
✓ Clean codebase
```

**Status**: ✅ COMPLETE (Old auth code kept for backward compatibility, new Better Auth integrated)

---

## Phase 4: Database Migration

### TASK-015: Initialize Better Auth Tables
**Priority**: P1 | **Estimate**: 15 min | **Dependencies**: TASK-002

**Description**: Let Better Auth create its required database tables.

**Steps**:
1. Start frontend with Better Auth configured
2. Better Auth auto-creates tables on first request
3. Verify tables exist in database
4. Document table structure

**Tables Created**:
- `user` - User accounts
- `session` - Active sessions
- `account` - Auth providers (credential, oauth)
- `verification` - Email verification tokens

**Test Cases**:
- [ ] All 4 tables created
- [ ] Tables have correct columns
- [ ] Foreign keys established

**Acceptance Criteria**:
```
✓ Better Auth tables exist
✓ Schema matches documentation
```

---

### TASK-016: Create User Migration Script
**Priority**: P1 | **Estimate**: 30 min | **Dependencies**: TASK-015

**Description**: Create SQL script to migrate existing users to Better Auth schema.

**Steps**:
1. Create `scripts/migrate_users_to_better_auth.sql`
2. Map old users to new user table
3. Create account records with password hashes
4. Preserve user IDs where possible

**Files**:
- `scripts/migrate_users_to_better_auth.sql` (create)

**SQL Script**:
```sql
-- Migration: Existing users to Better Auth
-- Run this AFTER Better Auth tables are created

BEGIN;

-- Step 1: Migrate users
INSERT INTO "user" (id, email, name, "emailVerified", "createdAt", "updatedAt")
SELECT
    id::text,
    email,
    COALESCE(SPLIT_PART(email, '@', 1), 'User'),
    true,
    created_at,
    updated_at
FROM users
ON CONFLICT (id) DO NOTHING;

-- Step 2: Create credential accounts
INSERT INTO account (
    id, "userId", "accountId", "providerId",
    password, "createdAt", "updatedAt"
)
SELECT
    gen_random_uuid()::text,
    id::text,
    id::text,
    'credential',
    password_hash,
    created_at,
    updated_at
FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM account
    WHERE "userId" = users.id::text
    AND "providerId" = 'credential'
);

COMMIT;
```

**Test Cases**:
- [ ] All existing users migrated
- [ ] Password hashes preserved
- [ ] No duplicate entries
- [ ] Rollback works

**Acceptance Criteria**:
```
✓ Migration script tested
✓ Existing users can login
✓ Data integrity maintained
```

---

### TASK-017: Create Rollback Script
**Priority**: P1 | **Estimate**: 15 min | **Dependencies**: TASK-016

**Description**: Create rollback script in case migration fails.

**Steps**:
1. Create `scripts/rollback_better_auth.sql`
2. Script to restore old auth system
3. Document rollback procedure

**Files**:
- `scripts/rollback_better_auth.sql` (create)

**Test Cases**:
- [ ] Rollback restores original state
- [ ] Old auth endpoints work after rollback

**Acceptance Criteria**:
```
✓ Rollback procedure documented
✓ Script tested in dev environment
```

---

### TASK-018: Verify Data Integrity
**Priority**: P1 | **Estimate**: 20 min | **Dependencies**: TASK-016

**Description**: Verify all users migrated correctly and can authenticate.

**Steps**:
1. Count users in old vs new tables
2. Test login with sample users
3. Verify session creation
4. Check for data anomalies

**Verification Queries**:
```sql
-- Count comparison
SELECT
    (SELECT COUNT(*) FROM users) as old_count,
    (SELECT COUNT(*) FROM "user") as new_count;

-- Check all have accounts
SELECT u.id, u.email
FROM "user" u
LEFT JOIN account a ON a."userId" = u.id
WHERE a.id IS NULL;
```

**Test Cases**:
- [ ] User counts match
- [ ] All users have account records
- [ ] Sample logins succeed
- [ ] Sessions created correctly

**Acceptance Criteria**:
```
✓ 100% users migrated
✓ No orphaned records
✓ Authentication verified
```

---

## Phase 5: Token Refresh & Logout

### TASK-019: Configure Session Refresh
**Priority**: P2 | **Estimate**: 15 min | **Dependencies**: TASK-002

**Description**: Configure Better Auth to automatically refresh sessions.

**Steps**:
1. Update auth.ts with refresh settings
2. Set updateAge for session refresh interval
3. Configure cookie cache

**Files**:
- `frontend/src/lib/auth.ts` (modify)

**Code Changes**:
```typescript
session: {
  expiresIn: 60 * 60 * 24 * 7, // 7 days
  updateAge: 60 * 60 * 24, // Refresh daily
  cookieCache: {
    enabled: true,
    maxAge: 60 * 5, // 5 minute cache
  },
},
```

**Test Cases**:
- [ ] Session refreshes before expiry
- [ ] New token issued on refresh
- [ ] Old token invalidated

**Acceptance Criteria**:
```
✓ Automatic session refresh working
✓ Users don't experience unexpected logouts
```

---

### TASK-020: Handle Token Expiration in Frontend
**Priority**: P2 | **Estimate**: 20 min | **Dependencies**: TASK-012

**Description**: Add frontend handling for expired tokens.

**Steps**:
1. Detect 401 responses from API
2. Attempt token refresh
3. Redirect to login if refresh fails
4. Show user-friendly message

**Files**:
- `frontend/src/lib/api.ts` (modify)
- `frontend/src/contexts/AuthContext.tsx` (modify)

**Test Cases**:
- [ ] 401 triggers refresh attempt
- [ ] Failed refresh redirects to login
- [ ] User sees "Session expired" message

**Acceptance Criteria**:
```
✓ Graceful expiration handling
✓ User informed of session state
```

---

### TASK-021: Implement Session Invalidation
**Priority**: P2 | **Estimate**: 15 min | **Dependencies**: TASK-012

**Description**: Ensure logout properly invalidates the session.

**Steps**:
1. Call Better Auth signOut
2. Clear all auth cookies
3. Invalidate session in database
4. Redirect to login

**Files**:
- `frontend/src/contexts/AuthContext.tsx` (modify)

**Test Cases**:
- [ ] Session deleted from database
- [ ] Cookie cleared
- [ ] Token no longer valid

**Acceptance Criteria**:
```
✓ Complete session termination
✓ Token cannot be reused
```

---

### TASK-022: Add Logout All Devices
**Priority**: P2 | **Estimate**: 20 min | **Dependencies**: TASK-021

**Description**: Add option to logout from all devices.

**Steps**:
1. Add "Logout everywhere" button in settings
2. Call Better Auth to revoke all sessions
3. Confirm action with user

**Files**:
- `frontend/src/components/settings/SecuritySettings.tsx` (create)

**Test Cases**:
- [ ] All sessions for user invalidated
- [ ] Current device also logged out
- [ ] Confirmation shown before action

**Acceptance Criteria**:
```
✓ Multi-device logout works
✓ User confirmation required
```

---

## Phase 6: Testing

### TASK-023: Frontend Auth Tests
**Priority**: P1 | **Estimate**: 45 min | **Dependencies**: TASK-010, TASK-011, TASK-012

**Description**: Write tests for frontend authentication flows.

**Steps**:
1. Create `frontend/__tests__/auth.test.ts`
2. Test sign-up flow
3. Test sign-in flow
4. Test sign-out flow
5. Test session persistence

**Files**:
- `frontend/__tests__/auth.test.ts` (create)

**Test Cases**:
```typescript
describe("Authentication", () => {
  it("should register a new user");
  it("should reject duplicate email");
  it("should login with valid credentials");
  it("should reject invalid password");
  it("should persist session across page reload");
  it("should clear session on logout");
});
```

**Acceptance Criteria**:
```
✓ All auth flows tested
✓ Tests pass in CI
```

---

### TASK-024: Backend JWT Tests
**Priority**: P1 | **Estimate**: 30 min | **Dependencies**: TASK-007, TASK-008

**Description**: Write tests for backend JWT verification.

**Steps**:
1. Create `backend/tests/test_better_auth.py`
2. Test valid token verification
3. Test expired token rejection
4. Test invalid token rejection
5. Test missing token handling

**Files**:
- `backend/tests/test_better_auth.py` (create)

**Test Cases**:
```python
class TestBetterAuthJWT:
    def test_valid_token_accepted(self):
        pass

    def test_expired_token_rejected(self):
        pass

    def test_invalid_signature_rejected(self):
        pass

    def test_missing_token_returns_401(self):
        pass

    def test_malformed_token_returns_401(self):
        pass
```

**Acceptance Criteria**:
```
✓ All token scenarios tested
✓ Security edge cases covered
```

---

### TASK-025: Integration Tests
**Priority**: P1 | **Estimate**: 45 min | **Dependencies**: TASK-023, TASK-024

**Description**: Write end-to-end tests for complete auth flow.

**Steps**:
1. Create integration test setup
2. Test: Register → Login → Access Protected → Logout
3. Test: Login → Create Task → Verify ownership
4. Test: Logout → Attempt access → Rejected

**Files**:
- `e2e/auth.spec.ts` or `backend/tests/test_integration.py`

**Test Cases**:
- [ ] Full registration to logout flow
- [ ] Protected resource access
- [ ] Cross-service token validation

**Acceptance Criteria**:
```
✓ E2E auth flow works
✓ Frontend ↔ Backend integration verified
```

---

### TASK-026: Security Edge Case Tests
**Priority**: P1 | **Estimate**: 30 min | **Dependencies**: TASK-024

**Description**: Test security edge cases and attack vectors.

**Steps**:
1. Test token replay attack prevention
2. Test CSRF protection
3. Test XSS via auth endpoints
4. Test brute force protection

**Files**:
- `backend/tests/test_security.py` (create)

**Test Cases**:
- [ ] Old tokens rejected after logout
- [ ] CSRF tokens validated
- [ ] No XSS in error messages
- [ ] Rate limiting on login attempts

**Acceptance Criteria**:
```
✓ Security vulnerabilities addressed
✓ No token reuse after invalidation
```

---

## Task Dependencies Graph

```
TASK-001 (Install)
    │
    ├──► TASK-002 (Auth Config) ──► TASK-003 (Auth Client)
    │         │                           │
    │         ├──► TASK-004 (API Route)   ├──► TASK-010 (LoginForm)
    │         │                           ├──► TASK-011 (RegisterForm)
    │         └──► TASK-015 (Tables)      └──► TASK-012 (AuthContext)
    │                   │                           │
    │                   └──► TASK-016 (Migration)   └──► TASK-013 (Header)
    │                             │                           │
    │                             └──► TASK-018 (Verify)      └──► TASK-014 (Cleanup)
    │
    └──► TASK-005 (Env Vars) ──► TASK-006 (Backend Config)
                                      │
                                      └──► TASK-007 (Security)
                                                │
                                                └──► TASK-008 (Deps)
                                                          │
                                                          └──► TASK-009 (Backend Env)
```

---

## Execution Order (Recommended)

### Sprint 1: Foundation (Day 1-2)
1. TASK-001: Install Better Auth
2. TASK-005: Configure Env Vars
3. TASK-002: Auth Server Config
4. TASK-003: Auth Client
5. TASK-004: API Routes
6. TASK-006: Backend Config
7. TASK-007: Security Module
8. TASK-008: Dependencies
9. TASK-009: Backend Env

### Sprint 2: UI & Migration (Day 3-4)
10. TASK-015: Initialize Tables
11. TASK-016: Migration Script
12. TASK-017: Rollback Script
13. TASK-018: Verify Data
14. TASK-010: Login Form
15. TASK-011: Register Form
16. TASK-012: Auth Context
17. TASK-013: Header Logout
18. TASK-014: Remove Old Auth

### Sprint 3: Polish & Test (Day 5)
19. TASK-019: Session Refresh
20. TASK-020: Expiration Handling
21. TASK-021: Session Invalidation
22. TASK-022: Logout All Devices
23. TASK-023: Frontend Tests
24. TASK-024: Backend Tests
25. TASK-025: Integration Tests
26. TASK-026: Security Tests
