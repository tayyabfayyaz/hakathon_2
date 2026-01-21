# Tasks: Kubernetes Local Deployment with Agentic DevOps

**Input**: Design documents from `/specs/006-k8s-minikube-deploy/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual E2E validation via browser, `helm lint`, `kubectl --dry-run` - no automated tests required.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app with K8s**: `frontend/`, `backend/`, `charts/`, `docs/`
- Paths are relative to repository root (`phase-4/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite verification

- [x] T001 Verify Docker Desktop is installed and running with sufficient resources
- [x] T002 Verify Minikube is installed (`minikube version` returns v1.30+)
- [x] T003 [P] Verify Helm 3.x is installed (`helm version`)
- [x] T004 [P] Verify kubectl is installed and configured (`kubectl version`)
- [x] T005 Start Minikube cluster with recommended resources: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [x] T006 Configure Docker CLI to use Minikube's Docker daemon: `eval $(minikube docker-env)` or PowerShell equivalent

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Dockerfile (Modified for K8s)

- [x] T007 Update backend Dockerfile in backend/Dockerfile with multi-stage build for K8s optimization
- [x] T008 [P] Create backend/.dockerignore with exclusions: `__pycache__, *.pyc, .git, .env*, tests/, hf-deploy/`
- [x] T009 [P] Verify backend Dockerfile builds successfully: `docker build -t todolist-backend:local ./backend`

### Frontend Dockerfile (New)

- [x] T010 Create frontend Dockerfile in frontend/Dockerfile with multi-stage Next.js build
- [x] T011 [P] Create frontend/.dockerignore with exclusions: `node_modules, .next, .git, .env*, *.md`
- [x] T012 [P] Verify frontend Dockerfile builds successfully: `docker build -t todolist-frontend:local ./frontend`

### Helm Chart Structure

- [x] T013 Create charts/todolist-pro/Chart.yaml umbrella chart definition
- [x] T014 [P] Create charts/todolist-pro/templates/_helpers.tpl with common template helpers
- [x] T015 [P] Create charts/todolist-pro/templates/NOTES.txt with post-install instructions

**Checkpoint**: Foundation ready - Docker images build, Helm structure initialized

---

## Phase 3: User Story 1 - Developer Deploys Application Locally (Priority: P1) 🎯 MVP

**Goal**: Enable developers to deploy the complete TodoList Pro stack to Minikube using a single Helm command

**Independent Test**: Run `helm install todolist-pro ./charts/todolist-pro` and verify:
- Both pods reach Running state within 3 minutes
- Frontend accessible via `minikube service todolist-pro-frontend`
- Login/register and task CRUD operations work

### Backend Subchart Implementation

- [x] T016 [P] [US1] Create charts/todolist-pro/charts/backend/Chart.yaml subchart definition
- [x] T017 [P] [US1] Create charts/todolist-pro/charts/backend/values.yaml with default backend settings
- [x] T018 [US1] Create charts/todolist-pro/charts/backend/templates/deployment.yaml with container spec, probes, resources
- [x] T019 [US1] Create charts/todolist-pro/charts/backend/templates/service.yaml as ClusterIP on port 8000
- [x] T020 [US1] Create charts/todolist-pro/charts/backend/templates/configmap.yaml for API_VERSION, DEBUG, PORT

### Frontend Subchart Implementation

- [x] T021 [P] [US1] Create charts/todolist-pro/charts/frontend/Chart.yaml subchart definition
- [x] T022 [P] [US1] Create charts/todolist-pro/charts/frontend/values.yaml with default frontend settings
- [x] T023 [US1] Create charts/todolist-pro/charts/frontend/templates/deployment.yaml with container spec, probes, resources
- [x] T024 [US1] Create charts/todolist-pro/charts/frontend/templates/service.yaml as NodePort on port 3000
- [x] T025 [US1] Create charts/todolist-pro/charts/frontend/templates/configmap.yaml for NEXT_PUBLIC_API_URL, BETTER_AUTH_URL

### Umbrella Chart Configuration

- [x] T026 [US1] Create charts/todolist-pro/templates/secrets.yaml for DATABASE_URL, GEMINI_API_KEY, BETTER_AUTH_SECRET, CORS_ORIGINS
- [x] T027 [US1] Create charts/todolist-pro/values.yaml with default values for both subcharts
- [x] T028 [US1] Create charts/todolist-pro/values-local.yaml with Minikube-specific overrides
- [x] T029 [US1] Validate Helm chart with `helm lint ./charts/todolist-pro`

### Deployment Validation

- [x] T030 [US1] Build Docker images with Minikube docker-env: `docker build -t todolist-frontend:local ./frontend && docker build -t todolist-backend:local ./backend`
- [x] T031 [US1] Deploy with Helm: `helm install todolist-pro ./charts/todolist-pro -f values-local.yaml --set secrets.databaseUrl=... --set secrets.betterAuthSecret=... --set secrets.geminiApiKey=...`
- [x] T032 [US1] Verify pods reach Running state: `kubectl get pods -l app.kubernetes.io/instance=todolist-pro`
- [x] T033 [US1] Access frontend and test login/register workflow: `minikube service todolist-pro-frontend`
- [x] T034 [US1] Test task CRUD operations through UI

**Checkpoint**: User Story 1 complete - Developer can deploy and use TodoList Pro on Minikube

---

## Phase 4: User Story 4 - Environment Configuration Management (Priority: P2)

**Goal**: Enable environment-specific configuration through Helm values without code changes

**Independent Test**: Deploy with different values files and verify correct database/API connections

### Implementation

- [x] T035 [P] [US4] Update charts/todolist-pro/values.yaml with comprehensive configuration documentation
- [x] T036 [P] [US4] Create charts/todolist-pro/values.schema.json from contracts/helm-values-schema.yaml for validation
- [x] T037 [US4] Verify secrets are not visible in ConfigMaps: `kubectl get configmap -o yaml | grep -v DATABASE_URL`
- [x] T038 [US4] Verify secret mounting works: `kubectl exec deploy/todolist-pro-backend -- env | grep DATABASE_URL` (should show value)
- [x] T039 [US4] Test helm upgrade with changed values: `helm upgrade todolist-pro ./charts/todolist-pro -f values-local.yaml --set frontend.replicaCount=2`
- [x] T040 [US4] Verify CORS_ORIGINS configuration allows frontend-to-backend communication

**Checkpoint**: User Story 4 complete - Configuration management works with proper secret handling

---

## Phase 5: User Story 2 - AI-Assisted Helm Chart Generation (Priority: P2)

**Goal**: Document and demonstrate AI-assisted DevOps workflow with kubectl-ai and Kagent

**Independent Test**: Run AI tools to generate/validate manifests and verify output passes `helm lint`

### kubectl-ai Documentation

- [x] T041 [P] [US2] Create docs/agentic-devops/kubectl-ai-setup.md with installation instructions (Krew and manual)
- [x] T042 [P] [US2] Add kubectl-ai configuration section for API key setup (OpenAI/Gemini)
- [x] T043 [US2] Document kubectl-ai usage examples for deployment, service, configmap generation
- [ ] T044 [US2] Test kubectl-ai generates valid deployment: `kubectl ai "create deployment for fastapi" | kubectl apply --dry-run=client -f -`

### Kagent Documentation

- [x] T045 [P] [US2] Create docs/agentic-devops/kagent-setup.md with CRD and CLI installation
- [x] T046 [US2] Document Kagent helm-agent usage for chart validation and deployment
- [ ] T047 [US2] Test Kagent validates chart: `kagent invoke -t "validate ./charts/todolist-pro" --agent helm-agent`

### AI Prompt Examples

- [ ] T048 [US2] Add AI prompt examples to plan.md Appendix with documented outputs
- [ ] T049 [US2] Create comparison section: AI-generated vs manual manifest quality

**Checkpoint**: User Story 2 complete - AI-DevOps tooling documented and tested

---

## Phase 6: User Story 5 - Health Monitoring and Service Discovery (Priority: P3)

**Goal**: Ensure all services have proper health checks and can communicate via K8s DNS

**Independent Test**: Verify pods show READY state and health endpoints respond within 5 seconds

### Health Probe Verification

- [x] T050 [P] [US5] Verify backend liveness probe: `kubectl describe pod -l app.kubernetes.io/name=backend | grep -A5 "Liveness:"`
- [x] T051 [P] [US5] Verify backend readiness probe: `kubectl describe pod -l app.kubernetes.io/name=backend | grep -A5 "Readiness:"`
- [x] T052 [US5] Test backend /health endpoint returns 200: `kubectl exec deploy/todolist-pro-backend -- wget -qO- http://localhost:8000/health`
- [x] T053 [US5] Verify frontend probes work: pods should not restart unnecessarily

### Service Discovery Verification

- [x] T054 [US5] Verify K8s DNS resolves backend service: `kubectl exec deploy/todolist-pro-frontend -- nslookup todolist-pro-backend`
- [x] T055 [US5] Verify frontend can reach backend via service DNS: test API call from frontend pod
- [x] T056 [US5] Verify rolling update works: `helm upgrade` with new image tag, no downtime

**Checkpoint**: User Story 5 complete - Health monitoring and service discovery validated

---

## Phase 7: User Story 3 - Docker Image Build with AI Assistance (Priority: P3)

**Goal**: Document Docker Gordon AI integration for Dockerfile optimization

**Independent Test**: Use Docker Gordon to analyze Dockerfiles and verify suggestions improve image size/security

### Docker Gordon Documentation

- [x] T057 [P] [US3] Create docs/agentic-devops/docker-gordon-guide.md with enablement instructions
- [x] T058 [US3] Document Docker Gordon usage for Dockerfile optimization prompts
- [x] T059 [US3] Add example optimization session: before/after Dockerfile comparison
- [x] T060 [US3] Document security recommendations from Gordon (non-root user, minimal base)

### Image Optimization Verification

- [x] T061 [US3] Verify frontend image size < 500MB: `docker images todolist-frontend:local --format "{{.Size}}"`
- [x] T062 [US3] Verify backend image size < 300MB: `docker images todolist-backend:local --format "{{.Size}}"`
- [x] T063 [P] [US3] Verify images run as non-root: `docker run --rm todolist-backend:local whoami | grep appuser`
- [x] T064 [P] [US3] Verify images have HEALTHCHECK: `docker inspect todolist-backend:local | grep HEALTHCHECK`

**Checkpoint**: User Story 3 complete - Docker AI integration documented and images optimized

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T065 [P] Update quickstart.md with complete deployment walkthrough
- [ ] T066 [P] Update README.md with K8s deployment section
- [ ] T067 Verify complete deployment scenario from clean state (minikube delete, start, deploy)
- [x] T068 [P] Create troubleshooting section in quickstart.md for common issues
- [x] T069 Run final helm lint and kubectl --dry-run validation
- [x] T070 Document resource utilization: `kubectl top pods`
- [x] T071 Verify application survives pod restart: delete pod, verify data persists

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core deployment (MVP)
- **User Story 4 (Phase 4)**: Depends on US1 - Configuration management
- **User Story 2 (Phase 5)**: Can run in parallel with US4 after US1 - AI tooling docs
- **User Story 5 (Phase 6)**: Depends on US1 - Health monitoring validation
- **User Story 3 (Phase 7)**: Can run in parallel with US5 after Foundational - Docker AI docs
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    │
    ▼
Foundational (Phase 2) ─────────────────────────────┐
    │                                               │
    ▼                                               ▼
US1: Deploy (P1) ───────┬───────────────► US3: Docker AI (P3)
    │                   │
    ├───────────────────┼────────────────┐
    │                   │                │
    ▼                   ▼                ▼
US4: Config (P2)   US2: kubectl-ai (P2)  US5: Health (P3)
    │                   │                │
    └───────────────────┴────────────────┘
                        │
                        ▼
                  Polish (Phase 8)
```

### Within Each User Story

- Charts before deployment
- Subcharts before umbrella
- Build before deploy
- Deploy before validate

### Parallel Opportunities

**Phase 2 (Foundational):**
```
# All these can run in parallel:
T008 (backend .dockerignore), T009 (verify backend build)
T011 (frontend .dockerignore), T012 (verify frontend build)
T014 (_helpers.tpl), T015 (NOTES.txt)
```

**Phase 3 (User Story 1):**
```
# Backend subchart files can run in parallel:
T016 (Chart.yaml), T017 (values.yaml)

# Frontend subchart files can run in parallel:
T021 (Chart.yaml), T022 (values.yaml)
```

**Phase 5 (User Story 2):**
```
# Documentation files can run in parallel:
T041 (kubectl-ai-setup.md), T045 (kagent-setup.md)
```

---

## Parallel Example: User Story 1 MVP

```bash
# Step 1: Backend subchart files in parallel
Task: "Create charts/todolist-pro/charts/backend/Chart.yaml"
Task: "Create charts/todolist-pro/charts/backend/values.yaml"

# Step 2: Frontend subchart files in parallel
Task: "Create charts/todolist-pro/charts/frontend/Chart.yaml"
Task: "Create charts/todolist-pro/charts/frontend/values.yaml"

# Step 3: Sequential - templates depend on Chart.yaml
Task: "Create backend/templates/deployment.yaml"
Task: "Create backend/templates/service.yaml"
Task: "Create frontend/templates/deployment.yaml"
Task: "Create frontend/templates/service.yaml"

# Step 4: Umbrella chart configuration
Task: "Create charts/todolist-pro/values.yaml"
Task: "Create charts/todolist-pro/values-local.yaml"

# Step 5: Validation
Task: "helm lint ./charts/todolist-pro"
Task: "helm install todolist-pro ./charts/todolist-pro ..."
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Dockerfiles + chart structure)
3. Complete Phase 3: User Story 1 (full deployment)
4. **STOP and VALIDATE**: Test deployment independently
5. Deploy/demo if ready - Application runs on Minikube!

### Incremental Delivery

1. Complete Setup + Foundational → Docker images build, Helm initialized
2. Add User Story 1 → Test deployment → **Deploy/Demo (MVP!)**
3. Add User Story 4 → Test config management → Deploy/Demo
4. Add User Story 2 → Test AI tooling → Deploy/Demo
5. Add User Story 5 → Test health monitoring → Deploy/Demo
6. Add User Story 3 → Test Docker AI → Deploy/Demo
7. Each story adds value without breaking previous stories

### Suggested MVP Scope

**For immediate deployment capability**: Complete Phases 1-3 (Setup, Foundational, User Story 1)

**Total: 34 tasks** for full MVP deployment

---

## Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| 1 | Setup | 6 | 2 |
| 2 | Foundational | 9 | 6 |
| 3 | US1 (P1) MVP | 19 | 4 |
| 4 | US4 (P2) | 6 | 2 |
| 5 | US2 (P2) | 9 | 3 |
| 6 | US5 (P3) | 7 | 2 |
| 7 | US3 (P3) | 8 | 4 |
| 8 | Polish | 7 | 3 |
| **Total** | | **71** | **26** |

### Tasks per User Story

- **US1 (P1)**: 19 tasks - Core deployment (MVP)
- **US2 (P2)**: 9 tasks - AI Helm tooling documentation
- **US3 (P3)**: 8 tasks - Docker AI documentation
- **US4 (P2)**: 6 tasks - Configuration management
- **US5 (P3)**: 7 tasks - Health monitoring validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
