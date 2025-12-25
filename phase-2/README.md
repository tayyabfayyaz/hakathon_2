# TodoList Pro

A full-stack, production-ready todo management application built with Next.js and FastAPI. TodoList Pro enables authenticated users to create, manage, organize, and filter personal todo items with a modern, responsive interface.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [API Reference](#api-reference)
- [User Stories](#user-stories)
- [Testing](#testing)
- [Security](#security)
- [Contributing](#contributing)

---

## Features

### Authentication & Authorization
- User registration with email and password validation
- Secure login with JWT-based session management
- Password hashing with bcrypt
- 24-hour session expiry with automatic logout
- Protected routes requiring authentication

### Todo CRUD Operations
- **Create**: Add new todos with title (1-200 characters) and optional description (up to 2000 characters)
- **Read**: View all personal todos in a clean, organized list
- **Update**: Edit title and description of existing todos
- **Delete**: Soft delete with confirmation dialog (data preserved for audit trail)

### Status Management
- Toggle todo completion status with single click
- Visual distinction between completed and remaining items
- Real-time status persistence

### Search & Filtering
- Full-text search across title and description (case-insensitive)
- Real-time search results with 300ms debounce
- Filter by status: All, Remaining, Completed
- Combine search and filter operations
- Cursor-based pagination (20 items per page)

### User Experience
- Responsive design for desktop and mobile
- Optimistic UI updates for instant feedback
- Toast notifications for action confirmations
- Loading states and error handling
- Confirmation dialogs for destructive actions

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.0 | React framework with App Router |
| React | 18.2.0 | UI component library |
| TypeScript | 5.3 | Type-safe JavaScript |
| Tailwind CSS | 3.4.0 | Utility-first CSS framework |
| Vitest | 1.1.0 | Unit testing framework |
| React Testing Library | 14.1.2 | Component testing |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109.0 | Async Python web framework |
| Python | 3.11+ | Programming language |
| SQLModel | 0.0.14 | ORM (SQLAlchemy + Pydantic) |
| asyncpg | 0.29.0 | Async PostgreSQL driver |
| python-jose | 3.3.0 | JWT token handling |
| bcrypt | 4.1.2 | Password hashing |
| pytest | 7.4.4 | Testing framework |
| Alembic | 1.13.1 | Database migrations |
| Uvicorn | 0.27.0 | ASGI server |

### Database
| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary database |
| Neon DB | Cloud PostgreSQL provider (production) |

---

## Project Structure

```
phase-2/
├── frontend/                    # Next.js React application
│   ├── src/
│   │   ├── app/                # Next.js app router pages
│   │   │   ├── page.tsx        # Todo list (main page)
│   │   │   ├── login/          # Login page
│   │   │   └── register/       # Registration page
│   │   ├── components/         # React components
│   │   │   ├── auth/           # Authentication components
│   │   │   ├── todos/          # Todo-related components
│   │   │   ├── ui/             # Reusable UI components
│   │   │   └── layout/         # Layout components
│   │   ├── contexts/           # React Context providers
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilities and API client
│   │   └── types/              # TypeScript interfaces
│   ├── tests/                  # Frontend test files
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                    # FastAPI Python application
│   ├── src/
│   │   ├── api/
│   │   │   ├── v1/             # API v1 endpoints
│   │   │   │   ├── auth.py     # Authentication routes
│   │   │   │   ├── todos.py    # Todo CRUD routes
│   │   │   │   └── router.py   # Route aggregation
│   │   │   ├── deps.py         # Dependency injection
│   │   │   ├── exceptions.py   # Exception handlers
│   │   │   └── middleware/     # Custom middleware
│   │   ├── core/               # Core configuration
│   │   │   ├── config.py       # Settings management
│   │   │   ├── security.py     # JWT & password utils
│   │   │   ├── database.py     # Database connection
│   │   │   └── logging.py      # Logging setup
│   │   ├── models/             # SQLModel definitions
│   │   │   ├── user.py         # User entity
│   │   │   ├── todo.py         # Todo entity
│   │   │   └── errors.py       # Error models
│   │   └── services/           # Business logic
│   │       ├── user_service.py
│   │       └── todo_service.py
│   ├── tests/                  # Backend test files
│   ├── alembic/                # Database migrations
│   ├── main.py                 # FastAPI entry point
│   └── requirements.txt
│
├── specs/                      # Feature specifications
│   └── 001-todo-crud-features/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       └── tasks.md            # Task breakdown
│
├── history/                    # Development records
│   ├── prompts/                # Prompt History Records
│   └── adr/                    # Architecture Decision Records
│
└── .specify/                   # SDD framework files
    ├── memory/
    │   └── constitution.md     # Project principles
    └── templates/              # Document templates
```

---

## Getting Started

### Prerequisites

- **Node.js** 18.17 or later
- **Python** 3.11 or later
- **PostgreSQL** 14 or later (or Neon DB account)
- **pnpm** (recommended) or npm

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd phase-2
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your database URL and secrets
```

#### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

#### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
pnpm install
# or: npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL
```

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todolist_pro
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Running the Application

#### Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

#### Start Frontend Development Server

```bash
cd frontend
pnpm dev
# or: npm run dev
```

The application will be available at `http://localhost:3000`

---

## Development Workflow

### Spec-Driven Development (SDD)

This project follows Spec-Driven Development practices:

1. **Specification** (`/sp.specify`)
   - Define feature requirements in `specs/<feature>/spec.md`
   - Establish acceptance criteria and constraints

2. **Planning** (`/sp.plan`)
   - Create implementation plan in `specs/<feature>/plan.md`
   - Document architectural decisions

3. **Task Generation** (`/sp.tasks`)
   - Break down into testable tasks in `specs/<feature>/tasks.md`
   - Define test cases for each task

4. **Implementation** (`/sp.implement`)
   - Execute tasks with test-first approach
   - Maintain small, focused commits

5. **Documentation**
   - PHR (Prompt History Records) capture development context
   - ADR (Architecture Decision Records) document significant decisions

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push and create PR
git push -u origin feature/your-feature-name
```

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

---

## API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/logout` | Logout (clear session) |
| GET | `/auth/me` | Get current user info |

### Todo Endpoints (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/todos` | Create new todo |
| GET | `/todos` | List todos with filters |
| GET | `/todos/{id}` | Get specific todo |
| PATCH | `/todos/{id}` | Update todo |
| DELETE | `/todos/{id}` | Delete todo (soft delete) |
| POST | `/todos/{id}/toggle` | Toggle completion status |

### Query Parameters (GET /todos)

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search in title and description |
| `status` | enum | Filter: "all", "completed", "remaining" |
| `cursor` | string | Pagination cursor (ISO datetime) |
| `limit` | int | Items per page (1-100, default: 20) |

### Error Response Format

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "fields": [
      {
        "field": "title",
        "error": "Title must be between 1 and 200 characters"
      }
    ]
  }
}
```

---

## User Stories

### Registration & Authentication

**US-001: User Registration**
> As a new user, I want to register with my email and password so that I can create a personal account.

- Acceptance Criteria:
  - Email must be valid format
  - Password must be at least 8 characters
  - Duplicate emails show appropriate error
  - Successful registration redirects to todo list

**US-002: User Login**
> As a registered user, I want to log in with my credentials so that I can access my todos.

- Acceptance Criteria:
  - Invalid credentials show error message
  - Successful login redirects to todo list
  - Session persists for 24 hours

**US-003: User Logout**
> As a logged-in user, I want to log out so that I can secure my session.

- Acceptance Criteria:
  - Logout clears session cookie
  - User is redirected to login page

### Todo Management

**US-004: Create Todo**
> As a user, I want to create a new todo with a title and optional description so that I can track my tasks.

- Acceptance Criteria:
  - Title is required (1-200 characters)
  - Description is optional (up to 2000 characters)
  - New todos appear at the top of the list
  - New todos default to "Remaining" status

**US-005: View Todos**
> As a user, I want to see all my todos in a list so that I can review my tasks.

- Acceptance Criteria:
  - Todos display title, description, and status
  - Completed todos are visually distinct
  - List is ordered by creation date (newest first)

**US-006: Edit Todo**
> As a user, I want to edit my todo's title and description so that I can update task details.

- Acceptance Criteria:
  - Edit opens modal with current values
  - Changes save on submit
  - Cancel discards changes

**US-007: Delete Todo**
> As a user, I want to delete a todo so that I can remove tasks I no longer need.

- Acceptance Criteria:
  - Confirmation dialog prevents accidental deletion
  - Todo is removed from list after confirmation
  - Action cannot be undone from UI

**US-008: Toggle Todo Status**
> As a user, I want to toggle a todo's completion status so that I can track my progress.

- Acceptance Criteria:
  - Single click toggles between Completed/Remaining
  - Visual feedback confirms status change
  - Status persists after page refresh

### Search & Filtering

**US-009: Search Todos**
> As a user, I want to search my todos so that I can quickly find specific tasks.

- Acceptance Criteria:
  - Search matches title and description
  - Search is case-insensitive
  - Results update as I type (with debounce)

**US-010: Filter Todos**
> As a user, I want to filter todos by status so that I can focus on specific tasks.

- Acceptance Criteria:
  - Filter options: All, Remaining, Completed
  - Filter combines with search
  - Active filter is visually indicated

**US-011: Paginated Todos**
> As a user, I want to see my todos in pages so that the list loads quickly.

- Acceptance Criteria:
  - 20 todos per page
  - "Load more" or infinite scroll for additional items
  - Page loads in under 3 seconds

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_todos.py
```

### Frontend Tests

```bash
cd frontend

# Run all tests
pnpm test
# or: npm test

# Run with coverage
pnpm test:coverage

# Run in watch mode
pnpm test:watch
```

### Critical Test Paths

- User registration and login flows
- Todo CRUD operations
- Input validation (title length, email format)
- Authentication middleware
- Search and filter functionality

---

## Security

### Implemented Security Measures

- **JWT Authentication**: Secure token-based authentication
- **HttpOnly Cookies**: Tokens stored in HttpOnly cookies (XSS protection)
- **Password Hashing**: Bcrypt with salt for password storage
- **CORS Configuration**: Restricted to frontend origin
- **Rate Limiting**: Protection against brute force attacks on auth endpoints
- **Input Validation**: Pydantic validation on all API inputs
- **Soft Deletes**: Audit trail preservation
- **User Isolation**: Users can only access their own todos

### Security Headers

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

---

## Performance

### Targets

| Metric | Target |
|--------|--------|
| Page Load | < 3 seconds |
| Status Toggle | < 500 milliseconds |
| Search Results | < 1 second |
| Concurrent Users | 100+ |

### Optimizations

- Async database operations with asyncpg
- Cursor-based pagination for efficient queries
- Debounced search (300ms) to reduce API calls
- Optimistic UI updates for instant feedback
- Static asset caching (1-year max-age)
- Next.js image optimization

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the SDD workflow (spec → plan → tasks → implement)
4. Write tests for new functionality
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- Follow TypeScript strict mode for frontend
- Use Pydantic for all API validation
- Write tests for critical paths
- Keep commits small and focused
- Document architectural decisions in ADRs

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- Database by [Neon](https://neon.tech/)
