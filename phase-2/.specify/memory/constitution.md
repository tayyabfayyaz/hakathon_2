<!--
  Sync Impact Report
  ===================
  Version change: 0.0.0 → 1.0.0 (MAJOR - initial ratification)

  Modified principles: N/A (initial creation)

  Added sections:
  - I. Input Validation & Type Safety
  - II. API Design Standards
  - III. Data Integrity
  - IV. Error Handling
  - V. Testing Discipline
  - VI. Simplicity & YAGNI
  - Input Data Types Reference
  - Development Workflow
  - Governance

  Removed sections: N/A (initial creation)

  Templates requiring updates:
  - plan-template.md: ✅ Compatible (Constitution Check references this file)
  - spec-template.md: ✅ Compatible (FR requirements align with principles)
  - tasks-template.md: ✅ Compatible (test phases align with testing discipline)

  Follow-up TODOs: None
-->

# TodoList Pro Constitution

## Core Principles

### I. Input Validation & Type Safety

All user input MUST be validated at the API layer before processing. This is NON-NEGOTIABLE for a web application handling user data.

**Rules:**
- String inputs: MUST be trimmed, length-validated (min/max), and sanitized for XSS
- Integer inputs: MUST be parsed with strict type checking; reject non-numeric strings
- Float inputs: MUST validate decimal precision and range boundaries
- Boolean inputs: MUST accept only explicit boolean values (`true`/`false`), not truthy/falsy strings
- All validation errors MUST return structured error responses with field-level details

**Rationale:** User input is untrusted by definition. API-level validation provides a single enforcement point, reducing complexity while ensuring data integrity before database operations.

### II. API Design Standards

All API endpoints MUST follow REST conventions with OpenAPI documentation.

**Rules:**
- Endpoints MUST use proper HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- Request/response bodies MUST use JSON format with consistent field naming (snake_case)
- All endpoints MUST be documented in OpenAPI/Swagger specification
- API versioning MUST be implemented via URL path (e.g., `/api/v1/`)
- Pagination MUST be implemented for list endpoints returning more than 20 items

**Rationale:** Consistent API design reduces cognitive load for frontend developers and enables automatic client generation from OpenAPI specs.

### III. Data Integrity

All data operations MUST preserve database integrity and follow SQLModel/Pydantic patterns.

**Rules:**
- All database models MUST use SQLModel with explicit type annotations
- Required fields MUST NOT allow null values unless business logic demands it
- Foreign key relationships MUST use proper constraints with ON DELETE behavior defined
- Timestamps (created_at, updated_at) MUST be automatically managed
- Soft deletes SHOULD be preferred over hard deletes for todo items

**Rationale:** Neon DB (PostgreSQL) provides strong integrity guarantees; the application layer must not bypass these protections.

### IV. Error Handling

All errors MUST return structured JSON responses with consistent format.

**Rules:**
- Error responses MUST include: `error_code` (string), `message` (string), `details` (object, optional)
- Validation errors MUST include field-level error details in `details.fields` array
- HTTP status codes MUST be appropriate: 400 (validation), 401 (auth), 404 (not found), 500 (server)
- Internal errors MUST NOT expose stack traces or internal details to clients
- All errors MUST be logged server-side with request context

**Error Response Format:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "fields": [
      {"field": "title", "error": "Title must be between 1 and 200 characters"}
    ]
  }
}
```

**Rationale:** Structured errors enable frontend to display meaningful messages and programmatically handle error states.

### V. Testing Discipline

Tests MUST exist for critical paths; implementation may proceed without TDD.

**Critical paths requiring tests:**
- Todo CRUD operations (create, read, update, delete)
- Input validation logic for all data types
- Authentication/authorization flows (if implemented)
- Data integrity constraints

**Rules:**
- Critical path tests MUST exist before feature is considered complete
- Tests MAY be written alongside or after implementation
- Integration tests preferred for API endpoints
- Unit tests required for validation logic

**Rationale:** Critical path testing ensures core functionality works reliably while avoiding test overhead for trivial code paths.

### VI. Simplicity & YAGNI

Start simple; complexity MUST be justified.

**Rules:**
- No abstractions until proven necessary (minimum 3 use cases)
- No external libraries for functionality achievable with stdlib
- No premature optimization; measure first
- Features MUST map directly to user requirements
- Configuration SHOULD use environment variables via `.env`

**Rationale:** Complexity is the enemy of maintainability. A todo application should remain simple and focused.

## Input Data Types Reference

This section defines the accepted input types for the TodoList Pro application.

| Type | Validation Rules | Example |
|------|-----------------|---------|
| `string` | Trim whitespace, min 1 char, max per field, XSS sanitized | `"Buy groceries"` |
| `int` | Strict integer parsing, no decimals, range validated | `1`, `100` |
| `float` | Decimal allowed, precision max 2 places for scores/priorities | `0.5`, `3.14` |
| `bool` | Explicit `true`/`false` only, no string coercion | `true`, `false` |
| `datetime` | ISO 8601 format required | `"2025-12-24T10:30:00Z"` |
| `uuid` | Valid UUID v4 format | `"550e8400-e29b-41d4-a716-446655440000"` |

**Field-Specific Constraints:**

| Field | Type | Min | Max | Notes |
|-------|------|-----|-----|-------|
| `title` | string | 1 | 200 | Required, cannot be whitespace-only |
| `description` | string | 0 | 2000 | Optional |
| `completed` | bool | - | - | Default: `false` |
| `priority` | int | 1 | 5 | Default: `3` (medium) |
| `due_date` | datetime | - | - | Optional, must be future date if set |

## Development Workflow

### Code Review Requirements
- All changes MUST be reviewed before merge (self-review acceptable for solo development)
- Validation logic changes require explicit test coverage verification

### Deployment
- Environment variables MUST NOT be committed to repository
- Database migrations MUST be reviewed before production deployment

### Technology Stack
- **Frontend**: Next.js
- **Backend API**: FastAPI with SQLModel
- **Database**: Neon DB (PostgreSQL)
- **Runtime**: Node.js (frontend), Python (backend)

## Governance

This constitution supersedes all other development practices for the TodoList Pro project.

**Amendment Process:**
1. Propose change with rationale
2. Document impact on existing code
3. Update constitution version
4. Update dependent artifacts if principles change

**Versioning Policy:**
- MAJOR: Principle removal or fundamental redefinition
- MINOR: New principle added or significant expansion
- PATCH: Clarifications, typo fixes, non-semantic changes

**Compliance:**
- All pull requests MUST verify compliance with these principles
- Violations require explicit justification in PR description

**Version**: 1.0.0 | **Ratified**: 2025-12-24 | **Last Amended**: 2025-12-24
