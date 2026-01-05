---
title: TodoList Pro API
emoji: ✅
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# TodoList Pro API

FastAPI backend for TodoList Pro task management application.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better-Auth JWT tokens
- **Async Driver**: asyncpg

## Quick Start

### Prerequisites

- Python 3.11+
- Neon PostgreSQL account
- Better-Auth configured on frontend

### Setup

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Neon database URL and Better-Auth secret
   ```

4. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start development server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | No |
| GET | /docs | Swagger UI | No |
| GET | /tasks | List user's tasks | Yes |
| POST | /tasks | Create task | Yes |
| GET | /tasks/{id} | Get task | Yes |
| PUT | /tasks/{id} | Full update | Yes |
| PATCH | /tasks/{id} | Partial update | Yes |
| DELETE | /tasks/{id} | Delete task | Yes |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Yes |
| `BETTER_AUTH_SECRET` | Shared secret with Better-Auth | Yes |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | No |
| `API_VERSION` | API version string | No |
| `DEBUG` | Enable debug mode | No |

## Authentication

The API uses JWT Bearer tokens issued by Better-Auth. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

The JWT must contain:
- `sub`: User ID
- `email`: User email (optional)
- `name`: User name (optional)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   ├── models/           # SQLModel entities
│   ├── schemas/          # Pydantic schemas
│   └── api/
│       ├── deps.py       # Dependencies
│       └── routes/       # Endpoints
├── tests/                # Test files
├── alembic/              # Migrations
└── pyproject.toml        # Dependencies
```

## License

MIT - Tayyab Fayyaz
