# Research: Better Auth with JWT Token Authentication

## Phase 0: Research Findings

### Decision 1: Authentication Architecture

**Decision**: Use Better Auth on the Next.js frontend with JWT tokens that are verified by the FastAPI backend.

**Rationale**:
- Better Auth is a TypeScript-only library designed for JavaScript frameworks (Next.js, React, etc.)
- It does NOT have native Python/FastAPI support
- The recommended architecture is:
  1. Better Auth handles authentication on the Next.js frontend
  2. Better Auth generates JWT tokens after successful authentication
  3. FastAPI backend verifies these JWT tokens for protected endpoints
  4. Session state is managed by Better Auth on the frontend

**Alternatives Considered**:
1. **Auth.js (NextAuth v5)**: More mature, similar architecture. Better Auth is newer but more comprehensive.
2. **Keep current python-jose implementation**: Works but doesn't leverage Better Auth features.
3. **fastapi-nextauth-jwt**: Library for using NextAuth tokens in FastAPI - could work with Better Auth too.

### Decision 2: Token Strategy

**Decision**: Use stateless JWT tokens with httpOnly cookies for session management.

**Rationale**:
- JWT tokens are self-contained and can be verified without database lookups
- httpOnly cookies prevent XSS attacks from accessing tokens
- Better Auth supports JWT mode via configuration: `session: { type: "jwt" }`
- FastAPI can verify tokens using the same secret/algorithm

**Token Configuration**:
- Access Token Expiry: 15 minutes (short-lived for security)
- Session Token Expiry: 7 days (managed by Better Auth)
- Token Algorithm: HS256 (symmetric, shared secret between Next.js and FastAPI)

### Decision 3: Database Schema

**Decision**: Let Better Auth manage its own session/account tables, keep existing User table.

**Rationale**:
- Better Auth requires specific tables: `user`, `session`, `account`, `verification`
- Current User table can be adapted or Better Auth can create its own
- Recommended approach: Use Better Auth's database adapter with existing Neon PostgreSQL

**Tables Required by Better Auth**:
```sql
-- Better Auth creates these tables automatically
user (id, name, email, emailVerified, image, createdAt, updatedAt)
session (id, expiresAt, token, createdAt, updatedAt, ipAddress, userAgent, userId)
account (id, accountId, providerId, userId, accessToken, refreshToken, ...)
verification (id, identifier, value, expiresAt, createdAt, updatedAt)
```

### Decision 4: Integration Points

**Decision**: Frontend-managed auth with backend token verification.

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     Better Auth Client                       ││
│  │  - Sign up / Sign in UI                                     ││
│  │  - Session management                                       ││
│  │  - JWT token generation                                     ││
│  │  - Token storage (httpOnly cookies)                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ JWT Token in Cookie/Header
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   JWT Verification Middleware                ││
│  │  - Verify JWT signature using shared secret                 ││
│  │  - Extract user ID from token payload                       ││
│  │  - Inject user context into request                         ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Protected API Endpoints                    ││
│  │  - /api/v1/tasks (CRUD operations)                          ││
│  │  - /api/v1/auth/me (user info)                              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Decision 5: Shared Secret Management

**Decision**: Use environment variables for JWT secret, shared between Next.js and FastAPI.

**Configuration**:
```bash
# .env (both services must use the same values)
BETTER_AUTH_SECRET=<random-32-char-secret>
JWT_SECRET=<same-as-better-auth-secret>  # For FastAPI
```

**Rationale**:
- Both services need the same secret to sign/verify JWTs
- Environment variables are secure and follow 12-factor app principles
- Better Auth uses BETTER_AUTH_SECRET for JWT signing

## Technology Stack Updates

### Frontend (Next.js)
- **Add**: `better-auth` - Main authentication library
- **Add**: `better-auth/react` - React hooks for auth
- **Keep**: Existing UI components, adapt for Better Auth

### Backend (FastAPI)
- **Keep**: `python-jose[cryptography]` - JWT verification
- **Keep**: `passlib[bcrypt]` - Password hashing (Better Auth handles this now)
- **Modify**: Security middleware to verify Better Auth tokens
- **Remove**: Registration/login endpoints (moved to Better Auth)

### Database
- **Add**: Better Auth required tables (user, session, account, verification)
- **Migrate**: Existing users to new schema or add compatibility layer

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Secret key mismatch | Auth fails completely | Use same env var reference, add startup validation |
| Token format incompatibility | JWT verification fails | Test token structure, ensure algorithm match |
| Database schema conflicts | Data loss | Careful migration, backup first |
| Session cookie issues | CORS/SameSite errors | Configure proper cookie settings for dev/prod |

## Sources

- [Better Auth Official](https://www.better-auth.com/)
- [BetterAuth vs NextAuth Comparison](https://www.devtoolsacademy.com/blog/betterauth-vs-nextauth/)
- [FastAPI + Next.js JWT Authentication](https://medium.com/@sl_mar/building-a-secure-jwt-authentication-system-with-fastapi-and-next-js-301e749baec2)
- [NextAuth with FastAPI Discussion](https://github.com/nextauthjs/next-auth/discussions/8064)
