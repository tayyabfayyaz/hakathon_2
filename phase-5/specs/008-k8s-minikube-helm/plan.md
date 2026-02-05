# Implementation Plan: Kubernetes Local Deployment with Minikube and Helm

**Feature Branch**: `008-k8s-minikube-helm`
**Created**: 2026-02-01
**Status**: Ready for Implementation

## Technical Context

### Current State
- Frontend: Next.js application in `frontend/` directory
- Backend: FastAPI application in `backend/` directory with existing Dockerfile
- Database: External PostgreSQL (Neon) - no local deployment needed
- No Kubernetes or Helm configuration exists

### Target State
- Both services containerized with optimized Dockerfiles
- Helm chart for one-command deployment to Minikube
- AI-assisted tooling documentation for troubleshooting
- Makefile for common operations

### Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Container Runtime | Docker | 24.x |
| Kubernetes | Minikube | 1.30+ |
| Package Manager | Helm | 3.x |
| Frontend | Next.js | 16.x |
| Backend | FastAPI | 0.115+ |
| Database | PostgreSQL (Neon) | External |

### Dependencies
- Existing frontend application (functional)
- Existing backend application (functional)
- External Neon database (configured)
- Developer machine with 4GB+ RAM, 2+ CPU cores

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | N/A | Infrastructure feature, not library |
| CLI Interface | ✓ | Makefile provides CLI commands |
| Test-First | ✓ | Deployment verification tests planned |
| Integration Testing | ✓ | End-to-end deployment tests |
| Observability | ✓ | Health checks, logging configured |
| Simplicity | ✓ | Single Helm chart, minimal config |

---

## Phase 0: Research Summary

See `research.md` for complete findings. Key decisions:

1. **Image Strategy**: Build directly in Minikube's Docker daemon
2. **Chart Structure**: Single chart with frontend/backend templates
3. **Service Exposure**: NodePort with optional Ingress
4. **Configuration**: Helm values → ConfigMap/Secret

---

## Phase 1: Design Artifacts

### Data Model
See `data-model.md` for Kubernetes resource definitions.

### Contracts
See `contracts/` directory:
- `helm-values-schema.yaml`: Helm values contract
- `deployment-api.md`: CLI commands and health check APIs

### Quickstart
See `quickstart.md` for developer onboarding guide.

---

## Phase 2: Implementation Plan

### Component 1: Container Images

#### 1.1 Frontend Dockerfile (Priority: P1)

**Location**: `frontend/Dockerfile`

**Requirements Addressed**: FR-001

**Implementation**:
```dockerfile
# Multi-stage build for Next.js
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

**Dependencies**: None

**Acceptance Criteria**:
- Image builds successfully
- Container starts and serves frontend
- Health check endpoint responds

---

#### 1.2 Backend Dockerfile Update (Priority: P1)

**Location**: `backend/Dockerfile`

**Requirements Addressed**: FR-001, FR-007

**Implementation**:
- Update port from 7860 to 8000
- Add Kubernetes-compatible health check
- Ensure graceful shutdown handling

**Dependencies**: None

**Acceptance Criteria**:
- Image builds successfully
- Container starts with correct port
- Health endpoints respond

---

### Component 2: Helm Chart

#### 2.1 Chart Structure (Priority: P1)

**Location**: `helm/todolist/`

**Requirements Addressed**: FR-002, FR-003, FR-004, FR-005, FR-006

**Implementation**:
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
│   └── ingress.yaml
└── .helmignore
```

**Dependencies**: 1.1, 1.2

**Acceptance Criteria**:
- `helm lint` passes
- `helm template` generates valid YAML
- Chart installs without errors

---

#### 2.2 Frontend Deployment Template (Priority: P1)

**Location**: `helm/todolist/templates/frontend-deployment.yaml`

**Requirements Addressed**: FR-007, FR-011

**Implementation**:
- Deployment with configurable replicas
- Resource limits and requests
- Liveness and readiness probes
- Environment variables from ConfigMap

**Dependencies**: 2.1

**Acceptance Criteria**:
- Pod starts successfully
- Probes pass health checks
- Resources enforced correctly

---

#### 2.3 Backend Deployment Template (Priority: P1)

**Location**: `helm/todolist/templates/backend-deployment.yaml`

**Requirements Addressed**: FR-007, FR-008, FR-011

**Implementation**:
- Deployment with HPA support
- Database connection from Secret
- API key from Secret
- Graceful shutdown configuration

**Dependencies**: 2.1

**Acceptance Criteria**:
- Pod connects to database
- Health checks pass
- Scales horizontally

---

#### 2.4 Service Templates (Priority: P1)

**Location**: `helm/todolist/templates/*-service.yaml`

**Requirements Addressed**: FR-003, FR-004

**Implementation**:
- Frontend: NodePort service (external access)
- Backend: ClusterIP service (internal only)
- Configurable ports

**Dependencies**: 2.2, 2.3

**Acceptance Criteria**:
- Frontend accessible via NodePort
- Backend accessible only within cluster
- Service discovery works

---

#### 2.5 ConfigMap and Secret Templates (Priority: P1)

**Location**: `helm/todolist/templates/configmap.yaml`, `secret.yaml`

**Requirements Addressed**: FR-005, FR-006

**Implementation**:
- ConfigMap for non-sensitive config
- Secret for credentials (base64 encoded)
- Templated from values.yaml

**Dependencies**: 2.1

**Acceptance Criteria**:
- Values injected into pods
- Secrets not exposed in logs
- Config changes trigger pod restarts

---

#### 2.6 Ingress Template (Priority: P3)

**Location**: `helm/todolist/templates/ingress.yaml`

**Requirements Addressed**: FR-004 (optional)

**Implementation**:
- Optional Ingress resource
- Path-based routing
- Nginx ingress class

**Dependencies**: 2.4

**Acceptance Criteria**:
- Ingress routes traffic correctly
- Works with `minikube addons enable ingress`

---

### Component 3: Deployment Automation

#### 3.1 Makefile (Priority: P1)

**Location**: `Makefile`

**Requirements Addressed**: FR-010, FR-012

**Implementation**:
```makefile
.PHONY: check build deploy status logs-frontend logs-backend scale-backend cleanup

check:
	@./scripts/check-prereqs.sh

build:
	@./scripts/build-images.sh

deploy:
	helm install todolist ./helm/todolist -f values-local.yaml

status:
	kubectl get all -l app=todolist

cleanup:
	helm uninstall todolist
```

**Dependencies**: All previous components

**Acceptance Criteria**:
- All make targets work
- Single command deployment
- Clean uninstall

---

#### 3.2 Helper Scripts (Priority: P2)

**Location**: `scripts/`

**Requirements Addressed**: FR-010

**Implementation**:
- `check-prereqs.sh`: Verify Docker, Minikube, Helm, kubectl
- `build-images.sh`: Build images in Minikube Docker
- `wait-for-pods.sh`: Wait for deployment completion

**Dependencies**: None

**Acceptance Criteria**:
- Scripts are idempotent
- Clear error messages
- Exit codes for automation

---

### Component 4: Documentation

#### 4.1 AI Tools Documentation (Priority: P2)

**Location**: `docs/ai-assisted-devops.md`

**Requirements Addressed**: FR-009

**Implementation**:
- kubectl-ai installation and usage
- Kagent setup and commands
- Docker Gordon overview
- Common troubleshooting scenarios

**Dependencies**: None

**Acceptance Criteria**:
- Installation steps verified
- Examples work as documented
- Fallback commands provided

---

#### 4.2 Deployment README (Priority: P2)

**Location**: `README-K8S.md`

**Requirements Addressed**: Documentation

**Implementation**:
- Quick start guide
- Architecture diagram
- Configuration reference
- Troubleshooting guide

**Dependencies**: All components

**Acceptance Criteria**:
- New developer can deploy in 10 minutes
- All commands work as documented

---

## Implementation Order

```
Week 1: Core Infrastructure
├── 1.1 Frontend Dockerfile
├── 1.2 Backend Dockerfile Update
├── 2.1 Chart Structure
├── 2.2 Frontend Deployment
├── 2.3 Backend Deployment
├── 2.4 Service Templates
└── 2.5 ConfigMap/Secret

Week 2: Automation & Polish
├── 3.1 Makefile
├── 3.2 Helper Scripts
├── 2.6 Ingress Template (optional)
├── 4.1 AI Tools Documentation
└── 4.2 Deployment README
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Minikube resource constraints | High | Document minimum requirements, provide tuning guide |
| Image build failures | Medium | Use multi-stage builds, cache layers |
| Database connectivity issues | High | Provide connection testing script |
| Port conflicts | Low | Use non-standard NodePorts, document conflicts |

---

## Verification Checklist

- [ ] Images build successfully in Minikube
- [ ] Helm chart passes linting
- [ ] Pods start and pass health checks
- [ ] Frontend accessible via browser
- [ ] Backend API responds to requests
- [ ] Tasks can be created through UI
- [ ] Scaling works correctly
- [ ] Cleanup removes all resources
- [ ] Documentation is accurate

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task list
2. Begin with Component 1 (Container Images)
3. Test each component before proceeding
4. Document any deviations from plan
