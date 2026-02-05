---
title: TodoList Pro API
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# TodoList Pro API

FastAPI backend for TodoList Pro task management application with AI-powered chatbot.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better-Auth JWT tokens
- **Async Driver**: asyncpg
- **Task Reminders**: Celery + Redis for scheduled notifications
- **WhatsApp Integration**: Twilio API for SMS/WhatsApp notifications
- **Voice/Chat Agents**: Model Context Protocol (MCP) SDK for AI integration

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
| PUT | /tasks/{id}/deadline | Set task deadline | Yes |
| DELETE | /tasks/{id}/deadline | Remove task deadline | Yes |
| GET | /users/me/whatsapp | Get WhatsApp registration status | Yes |
| POST | /users/me/whatsapp | Register WhatsApp number | Yes |
| DELETE | /users/me/whatsapp | Delete WhatsApp registration | Yes |
| POST | /users/me/whatsapp/verify | Verify WhatsApp number with OTP | Yes |
| POST | /users/me/whatsapp/resend | Resend verification code | Yes |
| GET | /users/me/reminder-preferences | Get reminder preferences | Yes |
| PUT | /users/me/reminder-preferences | Update reminder preferences | Yes |
| GET | /users/me/reminders/history | Get reminder history | Yes |
| GET | /tasks/{id}/reminders | Get reminders for a specific task | Yes |

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

## Task Reminder Features

The application includes advanced task reminder capabilities:

### Deadlines
- Users can set deadlines on tasks with `/tasks/{id}/deadline` endpoints
- Deadline information is included in task responses
- Supports both setting and removing deadlines

### WhatsApp Notifications
- Users can register WhatsApp numbers for reminders
- OTP-based verification system for security
- Automated reminder delivery via Twilio WhatsApp API
- Rate limiting for verification attempts (3 per 5 minutes)

### Reminder Scheduling
- Automatic scheduling of reminders based on user preferences
- Configurable reminder intervals (e.g., 1 day before, 1 hour before)
- Timezone-aware scheduling
- Failed reminder retry logic with exponential backoff

### Preferences & History
- User-configurable reminder preferences
- Complete reminder history and delivery status tracking
- Audit trail for all reminder communications

### MCP/Agent Integration
- Voice and chat agents can manage deadlines using MCP tools
- Available tools: `set_deadline`, `remove_deadline`, `get_task_deadline`, `list_tasks` (includes deadline)
- Enables hands-free task management via voice assistants

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
