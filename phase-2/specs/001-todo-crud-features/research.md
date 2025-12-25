# Research: TodoList Pro Core Features

**Branch**: `001-todo-crud-features`
**Date**: 2025-12-24
**Status**: Complete

## Technology Stack Decisions

### Backend Framework: FastAPI

**Decision**: Use FastAPI with Python 3.11+

**Rationale**:
- Constitution mandates FastAPI with SQLModel (Technology Stack section)
- Automatic OpenAPI documentation generation (aligns with Constitution II: API Design Standards)
- Native Pydantic integration for request/response validation (aligns with Constitution I: Input Validation)
- Async support for better concurrency with database operations
- Type hints provide self-documenting code

**Alternatives Considered**:
- Django REST Framework: More batteries-included but heavier; FastAPI is specified in constitution
- Flask: Lighter but lacks built-in validation and OpenAPI; would require more dependencies

### ORM: SQLModel

**Decision**: Use SQLModel for database models and Pydantic schemas

**Rationale**:
- Constitution mandates SQLModel (Principle III: Data Integrity)
- Single model definition serves both database and API validation
- Built on SQLAlchemy for robust PostgreSQL support
- Integrates seamlessly with FastAPI

**Alternatives Considered**:
- Raw SQLAlchemy: More verbose; would require separate Pydantic models
- Tortoise ORM: Async-native but less mature; SQLModel is specified

### Database: Neon DB (PostgreSQL)

**Decision**: Use Neon DB (serverless PostgreSQL)

**Rationale**:
- Constitution mandates Neon DB (Technology Stack section)
- Serverless scales to zero when inactive (cost-effective for development)
- Full PostgreSQL compatibility for ACID transactions
- Connection pooling built-in

**Alternatives Considered**:
- Local PostgreSQL: Requires infrastructure management
- SQLite: Not suitable for production web app with concurrent users

### Frontend Framework: Next.js 14

**Decision**: Use Next.js 14 with App Router

**Rationale**:
- Constitution mandates Next.js (Technology Stack section)
- Server-side rendering for better initial load (SC-008: <3s page load)
- Built-in API routes for BFF pattern if needed
- React 18 with Server Components for optimized rendering

**Alternatives Considered**:
- React SPA: Slower initial load; SSR benefits missed
- Vue/Nuxt: Not specified in constitution

### Authentication: JWT with HTTP-only Cookies

**Decision**: Use JWT tokens stored in HTTP-only cookies

**Rationale**:
- Constitution requires minimal security (user preference)
- Stateless authentication scales easily
- HTTP-only cookies prevent XSS token theft
- Works well with Next.js middleware for protected routes

**Alternatives Considered**:
- Session-based with Redis: More complex; requires session store
- OAuth2 providers: Over-engineering for simple email/password auth
- JWT in localStorage: Vulnerable to XSS attacks

### Password Hashing: bcrypt

**Decision**: Use bcrypt for password hashing

**Rationale**:
- FR-004 mandates secure password storage
- Industry standard with built-in salt
- Configurable work factor for future-proofing
- `passlib` library provides Python implementation

**Alternatives Considered**:
- Argon2: More modern but bcrypt is sufficient for this use case
- PBKDF2: Older; bcrypt preferred for new applications

### API Validation: Pydantic v2

**Decision**: Use Pydantic v2 for all request/response validation

**Rationale**:
- Constitution I mandates API-level validation
- Pydantic v2 is 5-17x faster than v1
- Automatic field-level error details (Constitution IV: Error Handling)
- Native integration with FastAPI and SQLModel

### Testing: pytest + httpx

**Decision**: Use pytest for backend tests, httpx for API testing

**Rationale**:
- Constitution V requires critical path tests
- pytest is Python's de facto test framework
- httpx provides async HTTP client for FastAPI testing
- pytest-asyncio for async test support

**Alternatives Considered**:
- unittest: More verbose; pytest preferred
- requests: Doesn't support async; httpx does

### Frontend Testing: Vitest + React Testing Library

**Decision**: Use Vitest for frontend tests

**Rationale**:
- Fast test execution with Vite's esbuild
- Compatible with React Testing Library
- Jest-compatible API for easy migration

## Architecture Decisions

### Separation of Concerns

**Decision**: Strict frontend/backend separation

```
frontend/     # Next.js application (UI only)
backend/      # FastAPI application (API + business logic)
```

**Rationale**:
- Clear boundaries improve maintainability
- Frontend can be deployed to Vercel/Netlify
- Backend can be deployed to any Python hosting (Railway, Render, etc.)
- Independent scaling and deployment

### API Versioning

**Decision**: Version via URL path `/api/v1/`

**Rationale**:
- Constitution II mandates API versioning via URL path
- Simple and explicit
- Easy to maintain multiple versions if needed

### Soft Delete Strategy

**Decision**: Implement soft deletes for todos

**Rationale**:
- Constitution III recommends soft deletes for todos
- Allows recovery of accidentally deleted items
- Add `deleted_at` timestamp field (NULL = active)

### Search Implementation

**Decision**: PostgreSQL ILIKE for search

**Rationale**:
- FR-022 requires case-insensitive search
- PostgreSQL ILIKE is simple and effective for MVP
- No external search service needed (Constitution VI: Simplicity)

**Alternatives Considered**:
- Full-text search (tsvector): Over-engineering for todo titles/descriptions
- Elasticsearch: Unnecessary complexity for this scale

### Pagination Strategy

**Decision**: Cursor-based pagination with 20 items per page

**Rationale**:
- Constitution II mandates pagination for 20+ items
- Cursor-based is more consistent than offset for real-time data
- Uses `created_at` timestamp as cursor

## Security Decisions

### Input Sanitization

**Decision**: HTML escape all user input on output

**Rationale**:
- Constitution I requires XSS sanitization
- Sanitize on output, not input (preserve original data)
- Next.js JSX auto-escapes by default
- Backend returns raw text; frontend handles display

### Rate Limiting

**Decision**: Basic rate limiting on auth endpoints only

**Rationale**:
- User requested minimal security
- Protects against brute-force login attempts
- 10 attempts per minute per IP on login/register

### CORS Configuration

**Decision**: Allow only specific frontend origin

**Rationale**:
- Prevent cross-origin attacks
- Configure based on environment (localhost for dev, production domain for prod)

## Performance Decisions

### Database Connection Pooling

**Decision**: Use Neon's built-in connection pooling

**Rationale**:
- Neon provides pooling out of the box
- Handles concurrent connections efficiently
- No additional infrastructure needed

### Search Debouncing

**Decision**: 300ms debounce on frontend

**Rationale**:
- Assumption 5 from spec: 300ms debounce
- Reduces unnecessary API calls
- Balances responsiveness with server load

### Client-Side Filtering

**Decision**: Filter and search on client for small datasets

**Rationale**:
- SC-010 requires <100ms filter operations
- For typical user (< 100 todos), client-side is instant
- Falls back to server-side for larger datasets

## Resolved Clarifications

All technical decisions have been made based on:
1. Constitution requirements (mandatory)
2. User preferences from specification phase
3. Industry best practices for todo applications

No outstanding clarifications remain.
