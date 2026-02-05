# AI-Assisted DevOps Guide

This guide covers using AI tools to assist with Kubernetes deployment and troubleshooting for TodoList Pro.

## Overview

Modern AI-powered tools can significantly accelerate Kubernetes operations:

| Tool | Purpose | Best For |
|------|---------|----------|
| kubectl-ai | Natural language kubectl | Quick queries, learning kubectl |
| Kagent | Diagnostics & troubleshooting | Pod failures, resource issues |
| Docker Gordon | Image optimization | Dockerfile analysis, security |

---

## kubectl-ai: Natural Language Kubernetes

### Installation

```bash
# Using Homebrew (macOS/Linux)
brew install kubectl-ai

# Using Go
go install github.com/sozercan/kubectl-ai@latest

# Verify installation
kubectl-ai --version
```

### Configuration

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Or use Azure OpenAI
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_API_KEY="your-key"
```

### Usage Examples

#### Basic Queries

```bash
# Get pod status
kubectl-ai "show me all pods in the todolist deployment"

# Check resource usage
kubectl-ai "what's the CPU and memory usage of my backend pods?"

# Find issues
kubectl-ai "why is my frontend pod not starting?"
```

#### Troubleshooting

```bash
# Diagnose crash loops
kubectl-ai "my backend pod keeps crashing, show me the logs and events"

# Check networking
kubectl-ai "can the frontend pod reach the backend service?"

# Resource constraints
kubectl-ai "is my pod being OOM killed?"
```

#### Learning kubectl

```bash
# Ask for the equivalent kubectl command
kubectl-ai "how do I scale the backend to 3 replicas? show me the command"

# Explain resources
kubectl-ai "explain what a ConfigMap is and show me mine"
```

### Fallback Manual Commands

If kubectl-ai is unavailable:

```bash
# List pods
kubectl get pods -l app=todolist

# Check pod events
kubectl describe pod -l app=todolist

# View logs
kubectl logs -l app.kubernetes.io/component=backend --tail=100

# Check resource usage
kubectl top pods -l app=todolist
```

---

## Kagent: AI-Powered Diagnostics

### Installation

```bash
# Install Kagent
pip install kagent

# Or using pipx
pipx install kagent

# Verify installation
kagent --version
```

### Configuration

```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"
# Or
export OPENAI_API_KEY="your-api-key"
```

### Usage Examples

#### Quick Diagnostics

```bash
# Diagnose a deployment
kagent diagnose deployment/todolist-backend

# Diagnose a pod
kagent diagnose pod/todolist-backend-xxxxx

# Diagnose a service
kagent diagnose service/todolist-frontend
```

#### Health Checks

```bash
# Overall cluster health
kagent health

# Specific namespace
kagent health -n default
```

#### Troubleshooting Scenarios

```bash
# Pod not starting
kagent diagnose deployment/todolist-frontend --verbose

# Service not reachable
kagent diagnose service/todolist-backend --include-endpoints

# Image pull errors
kagent diagnose pod/todolist-backend-xxxxx --include-events
```

### Fallback Manual Commands

```bash
# Describe deployment
kubectl describe deployment todolist-backend

# Check endpoints
kubectl get endpoints todolist-backend

# View events
kubectl get events --sort-by=.lastTimestamp | grep todolist
```

---

## Docker Gordon: Container Optimization

Docker Gordon (powered by Docker AI) helps optimize container images.

### Accessing Docker Gordon

```bash
# Docker Desktop 4.26+ includes Gordon
# Open Docker Desktop → AI Assistant

# Or use the CLI
docker ai "analyze my Dockerfile"
```

### Usage Examples

#### Dockerfile Analysis

```bash
# Analyze frontend Dockerfile
docker ai "analyze frontend/Dockerfile for security issues"

# Optimize for size
docker ai "how can I make my backend image smaller?"

# Multi-stage build help
docker ai "help me create a multi-stage build for my Next.js app"
```

#### Security Scanning

```bash
# Scan for vulnerabilities
docker scout cves todolist-backend:local

# Get recommendations
docker scout recommendations todolist-backend:local
```

#### Image Optimization Workflow

1. **Analyze current image:**
   ```bash
   docker ai "analyze the size and layers of todolist-frontend:local"
   ```

2. **Get optimization suggestions:**
   ```bash
   docker ai "suggest optimizations for my Dockerfile"
   ```

3. **Apply recommendations:**
   - Use multi-stage builds
   - Minimize layers
   - Use alpine base images
   - Remove unnecessary files

4. **Verify improvements:**
   ```bash
   docker images todolist-frontend:local
   ```

### Dockerfile Best Practices Checklist

- [ ] Use multi-stage builds to reduce final image size
- [ ] Use specific version tags (not `latest`)
- [ ] Run as non-root user
- [ ] Use `.dockerignore` to exclude unnecessary files
- [ ] Combine RUN commands to reduce layers
- [ ] Order commands from least to most frequently changing
- [ ] Use COPY instead of ADD for local files
- [ ] Include health checks
- [ ] Set proper signal handling (STOPSIGNAL)

### Fallback Manual Commands

```bash
# Check image size
docker images | grep todolist

# Inspect image layers
docker history todolist-backend:local

# Scan for vulnerabilities
docker scout quickview todolist-backend:local
```

---

## Common Troubleshooting Scenarios

### Scenario 1: Pod CrashLoopBackOff

**AI-Assisted:**
```bash
kubectl-ai "why is my backend pod in CrashLoopBackOff?"
kagent diagnose deployment/todolist-backend
```

**Manual:**
```bash
kubectl logs todolist-backend-xxxxx --previous
kubectl describe pod todolist-backend-xxxxx
kubectl get events --field-selector involvedObject.name=todolist-backend-xxxxx
```

### Scenario 2: Service Not Reachable

**AI-Assisted:**
```bash
kubectl-ai "is my frontend service correctly routing to pods?"
kagent diagnose service/todolist-frontend
```

**Manual:**
```bash
kubectl get endpoints todolist-frontend
kubectl get pods -l app.kubernetes.io/component=frontend -o wide
kubectl port-forward svc/todolist-frontend 3000:80
```

### Scenario 3: Image Pull Errors

**AI-Assisted:**
```bash
kubectl-ai "my pod can't pull the image, what's wrong?"
```

**Manual:**
```bash
kubectl describe pod todolist-backend-xxxxx | grep -A5 Events
# Verify image exists in Minikube's Docker
eval $(minikube docker-env)
docker images | grep todolist
```

### Scenario 4: Database Connection Failed

**AI-Assisted:**
```bash
kubectl-ai "check if my backend can connect to the database"
```

**Manual:**
```bash
# Check secret is mounted
kubectl exec -it deploy/todolist-backend -- env | grep DATABASE

# Test connection from pod
kubectl exec -it deploy/todolist-backend -- python -c "
import asyncpg
import asyncio
import os
asyncio.run(asyncpg.connect(os.environ['DATABASE_URL'].replace('+asyncpg', '')))
print('Connection successful!')
"
```

---

## Tips for AI-Assisted DevOps

1. **Be specific** - Include pod names, namespaces, and error messages
2. **Verify AI suggestions** - Always review before applying
3. **Keep fallback commands handy** - AI tools may not always be available
4. **Combine tools** - Use kubectl-ai for queries, Kagent for diagnostics
5. **Document solutions** - Add working solutions to your runbooks

---

## Resources

- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Docker AI Documentation](https://docs.docker.com/desktop/ai/)
- [Kubernetes Debugging Guide](https://kubernetes.io/docs/tasks/debug/)
