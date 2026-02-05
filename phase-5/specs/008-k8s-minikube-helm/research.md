# Research: Kubernetes Local Deployment with Minikube and Helm

**Feature**: 008-k8s-minikube-helm
**Date**: 2026-02-01
**Status**: Complete

## Research Tasks

### 1. Container Image Strategy for Minikube

**Context**: How to build and load images into Minikube's Docker environment

**Decision**: Use `minikube docker-env` to build images directly in Minikube's Docker daemon

**Rationale**:
- Avoids need for a container registry
- Images are immediately available to Kubernetes
- Faster iteration during development
- No network overhead for image pulls

**Alternatives Considered**:
- Push to Docker Hub: Requires network, slower iteration
- Use Minikube's built-in registry: More complex setup
- Load images via `minikube image load`: Works but slower than direct build

**Implementation**:
```bash
eval $(minikube docker-env)
docker build -t todolist-frontend:local ./frontend
docker build -t todolist-backend:local ./backend
```

---

### 2. Frontend Dockerfile Strategy (Next.js)

**Context**: Next.js requires specific build configuration for containerization

**Decision**: Multi-stage build with standalone output mode

**Rationale**:
- Next.js standalone mode creates minimal production bundle
- Multi-stage reduces final image size (from ~1GB to ~150MB)
- Node.js alpine base for security and size

**Key Configuration**:
- `next.config.js`: `output: 'standalone'`
- Runtime environment variables via NEXT_PUBLIC_* prefix
- Health check via `/api/health` endpoint

---

### 3. Backend Dockerfile Optimization

**Context**: Existing Dockerfile is functional but can be optimized for Kubernetes

**Decision**: Adapt existing Dockerfile with Kubernetes-specific configurations

**Rationale**:
- Existing Dockerfile already follows best practices (non-root user, healthcheck)
- Change port from 7860 to 8000 (standard FastAPI port)
- Add Kubernetes-compatible probes

**Changes Required**:
- Update port to 8000
- Add readiness probe endpoint
- Configure graceful shutdown

---

### 4. Helm Chart Structure

**Context**: Organize Helm chart for multi-service deployment

**Decision**: Single chart with subcharts for frontend and backend

**Rationale**:
- Simpler installation (one command)
- Shared values for common configuration
- Can still scale services independently

**Structure**:
```
helm/todolist/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── ingress.yaml (optional)
```

---

### 5. Service Exposure Strategy

**Context**: How to expose frontend for local access

**Decision**: NodePort with optional Ingress

**Rationale**:
- NodePort works immediately with Minikube
- `minikube service` command provides easy access
- Ingress available for more production-like setup

**Access Methods**:
1. `minikube service todolist-frontend --url`
2. `kubectl port-forward svc/todolist-frontend 3000:3000`
3. Ingress with `minikube addons enable ingress`

---

### 6. Configuration Management

**Context**: Managing environment-specific settings

**Decision**: Helm values with ConfigMap/Secret generation

**Rationale**:
- Single source of truth in values.yaml
- Helm templating for environment flexibility
- Secrets encoded with base64 (Helm handles this)

**Configuration Layers**:
1. `values.yaml`: Default development values
2. `values-local.yaml`: Override for specific needs
3. Environment variables in deployments

---

### 7. AI-Assisted Tools Integration

**Context**: How to integrate kubectl-ai, Kagent, Docker Gordon

**Decision**: Document as optional enhancements with install scripts

**Rationale**:
- Tools are optional, not required for deployment
- Each tool serves different purpose
- Provide fallback manual commands

**Tool Purposes**:
- **kubectl-ai**: Natural language Kubernetes queries
- **Kagent**: Kubernetes agent for diagnostics
- **Docker Gordon**: AI-assisted Dockerfile optimization

---

### 8. Health Check Strategy

**Context**: Kubernetes probe configuration

**Decision**: Separate liveness and readiness probes

**Rationale**:
- Liveness: Restart if application hangs
- Readiness: Only route traffic when ready
- Different endpoints for different concerns

**Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

### 9. Resource Management

**Context**: CPU/Memory limits for Minikube constraints

**Decision**: Conservative defaults suitable for local development

**Rationale**:
- Minikube has limited resources
- Allow headroom for other services
- Can be overridden in values.yaml

**Default Resources**:
- Frontend: 128Mi-256Mi memory, 100m-200m CPU
- Backend: 256Mi-512Mi memory, 200m-500m CPU

---

### 10. Database Connection

**Context**: Connecting to external Neon PostgreSQL

**Decision**: Use Kubernetes Secret for connection string

**Rationale**:
- Database is external, not deployed in cluster
- Connection string contains sensitive data
- Environment variable injection from Secret

**Configuration**:
- Secret: `database-credentials`
- Key: `DATABASE_URL`
- Injected via `envFrom` or `valueFrom`

---

## Summary

All research tasks completed. No NEEDS CLARIFICATION items remain. Ready for Phase 1 design artifacts.
