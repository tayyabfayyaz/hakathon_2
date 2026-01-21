# Implementation Plan: Kubernetes Local Deployment with Agentic DevOps

**Branch**: `006-k8s-minikube-deploy` | **Date**: 2026-01-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-k8s-minikube-deploy/spec.md`

## Summary

Deploy TodoList Pro (Next.js frontend + FastAPI backend) to a local Minikube Kubernetes cluster using Helm Charts. The implementation leverages AI-assisted DevOps tools (kubectl-ai, Kagent, Docker Gordon) to generate and optimize Kubernetes manifests and Docker images following cloud-native best practices.

## Technical Context

**Language/Version**:
- Frontend: TypeScript/Next.js 16.x (Node.js 20.x runtime)
- Backend: Python 3.11 (FastAPI)
- Infrastructure: YAML (Helm Charts, Kubernetes manifests)

**Primary Dependencies**:
- Docker Desktop (container runtime)
- Minikube v1.30+ (local K8s cluster)
- Helm 3.x (package manager)
- kubectl-ai (AI manifest generation)
- Kagent (AI Helm agent)

**Storage**: External Neon PostgreSQL (no local database)

**Testing**:
- `helm lint` for chart validation
- `kubectl --dry-run` for manifest validation
- Manual E2E testing via browser

**Target Platform**: Windows/macOS with Docker Desktop + Minikube

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Pods ready within 3 minutes
- Full deployment in under 5 minutes
- Health checks respond within 5 seconds

**Constraints**:
- Memory: 512Mi per container maximum
- CPU: 500m per container maximum
- Network: HTTP only (no TLS for local dev)

**Scale/Scope**: Single developer local environment, 1 replica per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | N/A | Infrastructure deployment, not library code |
| CLI Interface | PASS | Helm CLI provides text in/out interface |
| Test-First | PASS | `helm lint`, `kubectl --dry-run` before deployment |
| Integration Testing | PASS | E2E validation of deployed services |
| Observability | PASS | Health probes, kubectl logs |
| Simplicity | PASS | Minimal viable Helm chart structure |

**Re-check after Phase 1**: All gates remain PASS. No complexity violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-k8s-minikube-deploy/
├── spec.md                         # Feature specification
├── plan.md                         # This file
├── research.md                     # Phase 0 output
├── data-model.md                   # Kubernetes resource entities
├── quickstart.md                   # Developer quickstart guide
├── contracts/
│   ├── helm-values-schema.yaml     # Helm values JSON schema
│   └── dockerfile-contracts.md     # Docker image specifications
├── checklists/
│   └── requirements.md             # Spec validation checklist
└── tasks.md                        # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Existing application structure
frontend/
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   └── lib/              # Utilities
├── Dockerfile            # NEW: Production Dockerfile
├── .dockerignore         # NEW: Docker build exclusions
└── package.json

backend/
├── app/
│   ├── api/              # FastAPI routes
│   ├── models/           # SQLModel entities
│   └── services/         # Business logic
├── Dockerfile            # MODIFIED: K8s-optimized
├── .dockerignore         # NEW: Docker build exclusions
└── requirements.txt

# NEW: Kubernetes deployment
charts/
└── todolist-pro/
    ├── Chart.yaml            # Umbrella chart
    ├── values.yaml           # Default values
    ├── values-local.yaml     # Minikube overrides
    ├── templates/
    │   ├── _helpers.tpl      # Template helpers
    │   ├── secrets.yaml      # Shared secrets
    │   └── NOTES.txt         # Post-install notes
    └── charts/
        ├── frontend/
        │   ├── Chart.yaml
        │   ├── values.yaml
        │   └── templates/
        │       ├── deployment.yaml
        │       ├── service.yaml
        │       └── configmap.yaml
        └── backend/
            ├── Chart.yaml
            ├── values.yaml
            └── templates/
                ├── deployment.yaml
                ├── service.yaml
                └── configmap.yaml

# NEW: AI-DevOps documentation
docs/
└── agentic-devops/
    ├── kubectl-ai-setup.md       # kubectl-ai installation guide
    ├── kagent-setup.md           # Kagent installation guide
    └── docker-gordon-guide.md    # Docker Gordon usage guide
```

**Structure Decision**: Web application structure with dedicated `charts/` directory for Helm deployment. Existing frontend/backend directories remain unchanged except for Dockerfile additions.

## Complexity Tracking

No constitution violations requiring justification. Implementation follows simplest viable approach:
- Umbrella chart with 2 subcharts (standard Helm pattern)
- NodePort services (simplest external access for Minikube)
- External database (no local PostgreSQL complexity)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Developer Machine                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     Docker Desktop                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    Minikube                          │  │  │
│  │  │                                                      │  │  │
│  │  │   ┌──────────────┐      ┌──────────────┐           │  │  │
│  │  │   │   Frontend   │      │   Backend    │           │  │  │
│  │  │   │   (Next.js)  │─────▶│  (FastAPI)   │           │  │  │
│  │  │   │   NodePort   │ HTTP │  ClusterIP   │           │  │  │
│  │  │   └──────────────┘      └──────┬───────┘           │  │  │
│  │  │                                │                    │  │  │
│  │  └────────────────────────────────┼────────────────────┘  │  │
│  └───────────────────────────────────┼────────────────────────┘  │
└──────────────────────────────────────┼───────────────────────────┘
                                       │ HTTPS
                                       ▼
                            ┌──────────────────┐
                            │  Neon PostgreSQL │
                            │    (External)    │
                            └──────────────────┘
```

## Implementation Phases

### Phase 1: Docker Image Preparation

**Objective**: Create production-ready Docker images for frontend and backend.

**Tasks**:
1. Create/update frontend Dockerfile with multi-stage build
2. Create/update backend Dockerfile optimized for K8s
3. Create .dockerignore files for both services
4. Validate images build successfully with Minikube docker-env

**Deliverables**:
- `frontend/Dockerfile` (multi-stage, < 500MB)
- `backend/Dockerfile` (python:3.11-slim, < 300MB)
- `frontend/.dockerignore`
- `backend/.dockerignore`

**AI-DevOps Integration**:
- Use Docker Gordon to analyze and optimize Dockerfiles
- Document optimization suggestions received

### Phase 2: Helm Chart Creation

**Objective**: Create Helm umbrella chart with frontend and backend subcharts.

**Tasks**:
1. Initialize umbrella chart structure (`charts/todolist-pro/`)
2. Create frontend subchart with deployment, service, configmap
3. Create backend subchart with deployment, service, configmap
4. Create shared secrets template in umbrella chart
5. Configure values.yaml and values-local.yaml
6. Validate with `helm lint`

**Deliverables**:
- Complete Helm chart structure as defined in Project Structure
- `helm lint ./charts/todolist-pro` passes with no errors

**AI-DevOps Integration**:
- Use kubectl-ai to generate initial deployment/service manifests
- Use Kagent helm-agent to validate chart structure
- Document AI-generated content and manual modifications

### Phase 3: AI-DevOps Tooling Setup

**Objective**: Document and test AI-assisted DevOps tool installation.

**Tasks**:
1. Create kubectl-ai installation guide
2. Create Kagent installation guide
3. Create Docker Gordon usage guide
4. Test each tool with TodoList Pro deployment

**Deliverables**:
- `docs/agentic-devops/kubectl-ai-setup.md`
- `docs/agentic-devops/kagent-setup.md`
- `docs/agentic-devops/docker-gordon-guide.md`

### Phase 4: Integration and Validation

**Objective**: Deploy and validate complete stack on Minikube.

**Tasks**:
1. Start Minikube with required resources
2. Build Docker images in Minikube context
3. Deploy with Helm install
4. Verify all pods reach Running state
5. Test frontend accessibility
6. Test full user workflow (login, create task, verify persistence)
7. Test AI chat functionality with Gemini API

**Validation Checklist**:
- [ ] `helm lint` passes
- [ ] `kubectl get pods` shows all Running (1/1)
- [ ] Frontend accessible via `minikube service`
- [ ] Login/register functionality works
- [ ] Task CRUD operations work
- [ ] AI chat returns Gemini responses
- [ ] Logs show no errors (`kubectl logs`)

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Minikube resource constraints | Medium | High | Document minimum requirements, provide resource limit guidance |
| Neon database connectivity | Low | High | Validate connection string format, test before deployment |
| Image build failures | Low | Medium | Provide troubleshooting guide, test on clean environment |
| AI tool unavailability | Medium | Low | All AI tools are optional, provide manual alternatives |

## Dependencies

### External Services (Required)
- Neon PostgreSQL database (existing, with migrations applied)
- Gemini API (valid API key required)

### Tools (Required)
- Docker Desktop v4.38+
- Minikube v1.30+
- Helm v3.x
- kubectl

### Tools (Optional, for Agentic DevOps)
- kubectl-ai
- Kagent
- Docker Gordon (built into Docker Desktop)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment time | < 5 minutes | Time from `helm install` to all pods Running |
| Pod startup time | < 3 minutes | Time from pod creation to Ready state |
| Health check latency | < 5 seconds | Time for /health endpoint to respond |
| Image size (frontend) | < 500MB | `docker images` output |
| Image size (backend) | < 300MB | `docker images` output |
| Helm lint | 0 errors | `helm lint` exit code |

## Next Steps

After plan approval:
1. Run `/sp.tasks` to generate detailed implementation tasks
2. Execute Phase 1 (Docker images)
3. Execute Phase 2 (Helm charts)
4. Execute Phase 3 (AI-DevOps documentation)
5. Execute Phase 4 (Integration validation)

## Appendix: AI Prompts for Chart Generation

### kubectl-ai Prompts

```bash
# Frontend deployment
kubectl ai "create a kubernetes deployment named todolist-frontend with image todolist-frontend:local, 1 replica, port 3000, memory limit 512Mi, cpu limit 500m, liveness probe on / with 30s initial delay"

# Backend deployment
kubectl ai "create a kubernetes deployment named todolist-backend with image todolist-backend:local, 1 replica, port 8000, memory limit 512Mi, cpu limit 500m, liveness probe on /health with 10s initial delay"

# Frontend service
kubectl ai "create a NodePort service named todolist-frontend for deployment todolist-frontend on port 3000"

# Backend service
kubectl ai "create a ClusterIP service named todolist-backend for deployment todolist-backend on port 8000"
```

### Kagent Prompts

```bash
# Chart validation
kagent invoke -t "Validate the Helm chart at ./charts/todolist-pro for best practices" --agent helm-agent

# Deployment
kagent invoke -t "Install the todolist-pro chart from ./charts/todolist-pro with values from values-local.yaml" --agent helm-agent
```
