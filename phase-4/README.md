# Local Deployment Guide

This guide covers how to run the application locally for development purposes.

---

## Prerequisites

Before starting, ensure you have the following installed:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Node.js | 20+ | `node --version` |
| Python | 3.11+ | `python --version` |
| npm | Latest | `npm --version` |
| Git | Latest | `git --version` |

You will also need:
- A PostgreSQL database (Neon serverless recommended)
- A Google Gemini API key (for AI chatbot functionality)

---

## Project Structure

```
phase-4/
├── backend/                 # FastAPI backend (Python)
│   ├── app/                 # Application source code
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Backend environment variables
├── frontend/                # Next.js frontend (Node.js)
│   ├── src/                 # Application source code
│   ├── package.json         # Node.js dependencies
│   └── .env.local           # Frontend environment variables
└── README.md
```

---

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd phase-4
```

---

## Step 2: Configure Environment Variables

### Backend Configuration

Create `backend/.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require

# Authentication (must match frontend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-32-character-minimum-secret-key

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# API Configuration
API_VERSION=1.0.0
DEBUG=true

# Gemini Configuration (AI Chatbot)
GEMINI_API_KEY=your-gemini-api-key
```

### Frontend Configuration

Create `frontend/.env.local` file:

```env
# Better-Auth Configuration
BETTER_AUTH_SECRET=your-32-character-minimum-secret-key
BETTER_AUTH_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Database (for Better-Auth session storage)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

> **Important**: The `BETTER_AUTH_SECRET` value must be identical in both `backend/.env` and `frontend/.env.local` for authentication to work properly.

---

## Step 3: Setup Backend

Open a terminal and run:

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend server will start at `http://localhost:8000`

### Verify Backend is Running

```bash
# Health check
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/docs (Swagger UI)
```

---

## Step 4: Setup Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend server will start at `http://localhost:3000`

---

## Step 5: Access the Application

Once both servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:8000 | REST API endpoints |
| API Documentation | http://localhost:8000/docs | Swagger UI (interactive API docs) |
| API Schema | http://localhost:8000/redoc | ReDoc (alternative API docs) |

---

## Stopping the Servers

### Stop Backend
Press `Ctrl+C` in the backend terminal, then deactivate the virtual environment:
```bash
deactivate
```

### Stop Frontend
Press `Ctrl+C` in the frontend terminal.

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError`
```bash
# Ensure virtual environment is activated
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Error**: Database connection failed
- Verify `DATABASE_URL` in `backend/.env` is correct
- Ensure your database server is accessible
- Check that SSL settings match your database provider

### Frontend won't start

**Error**: `npm install` fails
```bash
# Clear npm cache and node_modules
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Error**: Cannot connect to backend API
- Ensure backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`

### Authentication not working

- Ensure `BETTER_AUTH_SECRET` is identical in both `.env` files
- The secret must be at least 32 characters long
- Restart both servers after changing environment variables

### Port already in use

**Backend (port 8000)**:
```bash
# Find and kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

**Frontend (port 3000)**:
```bash
# Find and kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :3000
kill -9 <PID>
```

---

## Quick Start Commands Summary

```bash
# Terminal 1 - Backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (asyncpg format) |
| `BETTER_AUTH_SECRET` | Yes | Shared authentication secret (min 32 chars) |
| `CORS_ORIGINS` | Yes | Allowed CORS origins (comma-separated) |
| `API_VERSION` | No | API version string (default: 1.0.0) |
| `DEBUG` | No | Enable debug mode (default: false) |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI chatbot |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `BETTER_AUTH_SECRET` | Yes | Shared authentication secret (must match backend) |
| `BETTER_AUTH_URL` | Yes | Better-Auth base URL |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | Public Better-Auth URL |
| `DATABASE_URL` | Yes | PostgreSQL connection string (pg format) |

> **Note**: Backend uses `postgresql+asyncpg://` prefix while frontend uses `postgresql://` prefix for the database URL.
