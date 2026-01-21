# Docker Gordon Usage Guide

Docker Gordon (also known as "Ask Gordon") is an AI assistant built into Docker Desktop that helps with Dockerfile optimization, container troubleshooting, and Docker best practices.

## Prerequisites

- Docker Desktop v4.38+ installed
- Docker Desktop running
- Internet connectivity for AI features

## Enabling Docker Gordon

### Via Docker Desktop UI

1. Open Docker Desktop
2. Click the **Settings** (gear) icon
3. Navigate to **Beta features** or **Features in development**
4. Toggle **Docker AI** or **Ask Gordon** to ON
5. Accept the terms of service
6. Click **Apply & restart**

### Verification

After enabling, you should see:
- "Ask Gordon" option in the left sidebar
- AI chat icon available in container/image views

## Usage Methods

### Method 1: Docker Desktop UI (Recommended)

1. Click **Ask Gordon** in the left sidebar
2. Type your question or paste Dockerfile content
3. Gordon will analyze and provide recommendations

### Method 2: Command Line (Preview)

```bash
# Analyze Dockerfile
docker ai "optimize my FastAPI Dockerfile for production"

# Get container recommendations
docker ai "why is my container running out of memory"

# General Docker questions
docker ai "how do I create a multi-stage build for Next.js"
```

## Dockerfile Optimization Examples

### Backend (FastAPI) Optimization

**Input Prompt:**
```
Analyze this FastAPI Dockerfile and suggest optimizations for production:

FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Gordon's Typical Recommendations:**
1. Use slim base image (`python:3.11-slim`)
2. Implement multi-stage build
3. Add non-root user for security
4. Order COPY commands for better layer caching
5. Add HEALTHCHECK instruction
6. Set Python environment variables

**Optimized Result:**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 wget && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Next.js) Optimization

**Input Prompt:**
```
Create an optimized multi-stage Dockerfile for a Next.js 16 application with standalone output
```

**Gordon's Typical Recommendations:**
1. Use alpine base images for smaller size
2. Implement 3-stage build (deps, builder, runner)
3. Copy only necessary files in final stage
4. Use standalone Next.js output
5. Add non-root user
6. Set production environment variables

**Optimized Result:**
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
RUN mkdir .next && chown nextjs:nodejs .next
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
CMD ["node", "server.js"]
```

## Security Recommendations

Gordon typically suggests these security improvements:

### 1. Non-Root User
```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser
```

### 2. Minimal Base Images
```dockerfile
# Use slim or alpine variants
FROM python:3.11-slim  # Instead of python:3.11
FROM node:20-alpine    # Instead of node:20
```

### 3. Secret Handling
```dockerfile
# Don't copy .env files
COPY . .  # BAD if .env exists
# Use .dockerignore instead:
# .env*
```

### 4. Read-Only Root Filesystem
```dockerfile
# In deployment (not Dockerfile)
# --read-only flag when running container
```

## Image Size Optimization

Gordon analyzes layers and suggests:

1. **Combine RUN commands** to reduce layers
2. **Clean up in same layer** to reduce size
3. **Use .dockerignore** to exclude unnecessary files
4. **Multi-stage builds** to exclude build tools

### Example .dockerignore suggestions:
```
# Development files
node_modules
.next
*.log
.env*
.git

# Documentation
README.md
docs/

# Tests
__tests__
*.test.*
coverage/
```

## Troubleshooting with Gordon

### Container Memory Issues
```
Ask Gordon: "Why is my container using too much memory?"

Typical suggestions:
1. Set memory limits in deployment
2. Check for memory leaks in application
3. Optimize image layers
4. Use multi-stage builds
```

### Slow Build Times
```
Ask Gordon: "How can I speed up my Docker builds?"

Typical suggestions:
1. Order Dockerfile instructions by change frequency
2. Use BuildKit for parallel builds
3. Implement layer caching strategies
4. Use .dockerignore to reduce context
```

### Image Size Analysis
```
Ask Gordon: "Analyze why my image is large"

Typical analysis:
1. Lists largest layers
2. Identifies unnecessary files
3. Suggests multi-stage build if not present
4. Recommends smaller base images
```

## Best Practices Summary

| Practice | Description |
|----------|-------------|
| Multi-stage builds | Separate build and runtime |
| Slim base images | Use -slim or alpine variants |
| Non-root users | Security hardening |
| HEALTHCHECK | Container health monitoring |
| .dockerignore | Reduce build context |
| Layer caching | Order by change frequency |
| No secrets | Never include in image |

## Limitations

- Requires internet connectivity
- May not know about very recent Docker features
- Suggestions are recommendations, not guarantees
- Always test optimizations in your environment

## References

- [Docker Documentation](https://docs.docker.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Desktop Features](https://docs.docker.com/desktop/)
- [Docker Gordon/AI Features](https://docs.docker.com/ai/gordon/)
