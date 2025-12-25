# Quickstart Guide: TodoList Pro

**Branch**: `001-todo-crud-features`
**Date**: 2025-12-24

This guide helps you set up and run TodoList Pro locally for development.

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **pnpm** (recommended) or npm
- **PostgreSQL** or Neon DB account

## Project Structure

```
todolist-pro/
├── backend/                 # FastAPI application
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── models/         # SQLModel entities
│   │   ├── services/       # Business logic
│   │   └── core/           # Config, security, db
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/                # Next.js application
│   ├── src/
│   │   ├── app/            # App router pages
│   │   ├── components/     # React components
│   │   └── lib/            # Utilities, API client
│   ├── package.json
│   └── next.config.js
└── specs/                   # Feature specifications
```

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd todolist-pro

# Switch to feature branch
git checkout 001-todo-crud-features
```

## Step 2: Database Setup

### Option A: Neon DB (Recommended)

1. Create a free account at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string

### Option B: Local PostgreSQL

```bash
# Create database
createdb todolist_pro

# Connection string
postgresql://localhost/todolist_pro
```

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

Run database migrations:

```bash
# Run migrations
alembic upgrade head
```

Start the backend:

```bash
# Development server with auto-reload
uvicorn main:app --reload --port 8000
```

Backend is now running at: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install
# or: npm install

# Create .env.local file
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Start the frontend:

```bash
# Development server
pnpm dev
# or: npm run dev
```

Frontend is now running at: `http://localhost:3000`

## Step 5: Verify Installation

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Create a todo item
4. Verify it appears in the list

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
pnpm test
# or: npm test
```

## Common Issues

### Database Connection Error

- Verify `DATABASE_URL` in `.env`
- Ensure PostgreSQL/Neon is running
- Check firewall settings for remote DB

### CORS Errors

- Ensure `CORS_ORIGINS` includes frontend URL
- Clear browser cache after config changes

### Auth Not Working

- Verify `JWT_SECRET` is set
- Check that cookies are enabled in browser
- Ensure same-site cookie settings match environment

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/auth/me` | Get current user |
| GET | `/api/v1/todos` | List todos |
| POST | `/api/v1/todos` | Create todo |
| GET | `/api/v1/todos/{id}` | Get todo |
| PATCH | `/api/v1/todos/{id}` | Update todo |
| DELETE | `/api/v1/todos/{id}` | Delete todo |
| POST | `/api/v1/todos/{id}/toggle` | Toggle status |

## Next Steps

1. Review the [spec.md](./spec.md) for feature requirements
2. Check [data-model.md](./data-model.md) for entity definitions
3. See [contracts/openapi.yaml](./contracts/openapi.yaml) for API details
4. Run `/sp.tasks` to generate implementation tasks
