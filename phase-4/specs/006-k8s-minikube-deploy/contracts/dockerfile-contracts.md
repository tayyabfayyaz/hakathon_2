# Dockerfile Contracts: TodoList Pro

**Feature**: 006-k8s-minikube-deploy
**Date**: 2026-01-19

## Overview

This document defines the contracts (requirements and specifications) for the Docker images used in the TodoList Pro Kubernetes deployment.

---

## 1. Frontend Dockerfile Contract

### Image Specification

| Property | Requirement |
|----------|-------------|
| Base Image | node:20-alpine or node:20-slim |
| Final Image Size | < 500MB |
| Exposed Port | 3000 |
| User | Non-root (node or custom) |
| Working Directory | /app |

### Required Build Arguments

| ARG | Description | Default |
|-----|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

### Required Environment Variables (Runtime)

| Variable | Description | Source |
|----------|-------------|--------|
| BETTER_AUTH_SECRET | JWT secret | Kubernetes Secret |
| BETTER_AUTH_URL | Auth callback URL | Kubernetes ConfigMap |
| DATABASE_URL | PostgreSQL connection | Kubernetes Secret |
| NEXT_PUBLIC_API_URL | Backend URL | Build-time ARG |

### Build Stages (Multi-stage)

1. **deps** - Install dependencies
2. **builder** - Build Next.js application
3. **runner** - Production runtime (minimal)

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
```

### Security Requirements

- [ ] Run as non-root user
- [ ] No development dependencies in final image
- [ ] .dockerignore excludes: node_modules, .git, .env*, *.md
- [ ] No secrets baked into image

---

## 2. Backend Dockerfile Contract

### Image Specification

| Property | Requirement |
|----------|-------------|
| Base Image | python:3.11-slim |
| Final Image Size | < 300MB |
| Exposed Port | 8000 |
| User | Non-root (appuser) |
| Working Directory | /app |

### Required Environment Variables (Runtime)

| Variable | Description | Source |
|----------|-------------|--------|
| DATABASE_URL | PostgreSQL connection | Kubernetes Secret |
| BETTER_AUTH_SECRET | JWT validation secret | Kubernetes Secret |
| GEMINI_API_KEY | Gemini AI API key | Kubernetes Secret |
| CORS_ORIGINS | Allowed CORS origins | Kubernetes Secret |
| PORT | Server port | Kubernetes ConfigMap |
| API_VERSION | API version string | Kubernetes ConfigMap |
| DEBUG | Debug mode flag | Kubernetes ConfigMap |

### Build Stages (Multi-stage)

1. **builder** - Install dependencies with build tools
2. **runtime** - Production runtime (minimal)

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### Security Requirements

- [ ] Run as non-root user (UID 1000)
- [ ] No development dependencies (pytest, etc.)
- [ ] .dockerignore excludes: __pycache__, .git, .env*, *.pyc, tests/
- [ ] No secrets baked into image
- [ ] Use --no-cache-dir for pip

---

## 3. Image Naming Convention

### For Minikube (Local Development)

```
todolist-frontend:local
todolist-backend:local
```

### For Production (Future)

```
ghcr.io/[org]/todolist-frontend:v1.0.0
ghcr.io/[org]/todolist-backend:v1.0.0
```

---

## 4. Build Commands Contract

### Frontend Build

```bash
# From repository root, with Minikube docker-env
eval $(minikube docker-env)

docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://todolist-pro-backend:8000 \
  -t todolist-frontend:local \
  -f frontend/Dockerfile \
  ./frontend
```

### Backend Build

```bash
# From repository root, with Minikube docker-env
eval $(minikube docker-env)

docker build \
  -t todolist-backend:local \
  -f backend/Dockerfile \
  ./backend
```

---

## 5. Image Validation Tests

### Frontend Image Tests

```bash
# 1. Image size check
docker images todolist-frontend:local --format "{{.Size}}" | grep -E "^[0-4][0-9]{2}MB$"

# 2. Non-root user check
docker run --rm todolist-frontend:local whoami | grep -v root

# 3. Port exposure check
docker inspect todolist-frontend:local | grep -q '"3000/tcp"'

# 4. Health check presence
docker inspect todolist-frontend:local | grep -q "HEALTHCHECK"
```

### Backend Image Tests

```bash
# 1. Image size check
docker images todolist-backend:local --format "{{.Size}}" | grep -E "^[0-2][0-9]{2}MB$"

# 2. Non-root user check
docker run --rm todolist-backend:local whoami | grep -v root

# 3. Port exposure check
docker inspect todolist-backend:local | grep -q '"8000/tcp"'

# 4. Health check presence
docker inspect todolist-backend:local | grep -q "HEALTHCHECK"
```

---

## 6. .dockerignore Contract

### Frontend .dockerignore

```
node_modules
.next
.git
.gitignore
*.md
.env*
.vercel
coverage
.nyc_output
*.log
```

### Backend .dockerignore

```
__pycache__
*.pyc
*.pyo
.git
.gitignore
*.md
.env*
.pytest_cache
.coverage
htmlcov
tests
hf-deploy
alembic/versions/__pycache__
```

---

## 7. Acceptance Criteria

### Frontend Dockerfile

- [ ] Uses multi-stage build with at least 2 stages
- [ ] Final image < 500MB
- [ ] Runs as non-root user
- [ ] Exposes port 3000
- [ ] Includes HEALTHCHECK instruction
- [ ] Accepts NEXT_PUBLIC_API_URL as build argument
- [ ] Production dependencies only in final stage

### Backend Dockerfile

- [ ] Uses python:3.11-slim base
- [ ] Final image < 300MB (target: ~200MB)
- [ ] Runs as non-root user (appuser, UID 1000)
- [ ] Exposes port 8000
- [ ] Includes HEALTHCHECK instruction
- [ ] Uses uvicorn as production server
- [ ] No test dependencies in final image
