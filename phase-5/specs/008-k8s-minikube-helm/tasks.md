# Tasks: Kubernetes Local Deployment with Minikube and Helm

**Feature Branch**: `008-k8s-minikube-helm`
**Input**: Design documents from `specs/008-k8s-minikube-helm/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - omitted from task list

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for Kubernetes deployment

- [x] T001 Create k8s directory structure: `helm/todolist/`, `helm/todolist/templates/`, `scripts/`, `docs/`
- [x] T002 [P] Create `.helmignore` file in `helm/todolist/.helmignore`
- [x] T003 [P] Create `values-local.yaml.example` template in `helm/todolist/values-local.yaml.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Container Images

- [x] T004 [P] Create frontend Dockerfile with multi-stage build in `frontend/Dockerfile`
- [x] T005 [P] Update Next.js config for standalone output in `frontend/next.config.ts` (add `output: 'standalone'`)
- [x] T006 [P] Create frontend health check API endpoint in `frontend/src/app/api/health/route.ts`
- [x] T007 [P] Update backend Dockerfile with port 8000 in `backend/Dockerfile`
- [x] T008 [P] Verify backend health endpoint exists at `/health` in `backend/app/api/routes/health.py`

### Helm Chart Base

- [x] T009 Create Chart.yaml with metadata in `helm/todolist/Chart.yaml`
- [x] T010 Create values.yaml with default configuration in `helm/todolist/values.yaml`
- [x] T011 Create helper templates in `helm/todolist/templates/_helpers.tpl`

### Configuration Resources

- [x] T012 [P] Create ConfigMap template in `helm/todolist/templates/configmap.yaml`
- [x] T013 [P] Create Secret template in `helm/todolist/templates/secret.yaml`

**Checkpoint**: Foundation ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Developer Deploys Application Locally (Priority: P1) 🎯 MVP

**Goal**: Deploy complete TodoList Pro application to local Kubernetes with single command

**Independent Test**: Run `make deploy` and access application through `minikube service todolist-frontend --url`

### Deployment Templates

- [x] T014 [P] [US1] Create frontend Deployment template in `helm/todolist/templates/frontend-deployment.yaml`
- [x] T015 [P] [US1] Create backend Deployment template in `helm/todolist/templates/backend-deployment.yaml`
- [x] T016 [P] [US1] Create frontend Service (NodePort) template in `helm/todolist/templates/frontend-service.yaml`
- [x] T017 [P] [US1] Create backend Service (ClusterIP) template in `helm/todolist/templates/backend-service.yaml`

### Automation Scripts

- [x] T018 [P] [US1] Create prerequisites check script in `scripts/check-prereqs.sh`
- [x] T019 [P] [US1] Create image build script in `scripts/build-images.sh`
- [x] T020 [P] [US1] Create pod wait script in `scripts/wait-for-pods.sh`
- [x] T021 [US1] Create Makefile with build/deploy/status/cleanup targets in `Makefile`

### Validation

- [x] T022 [US1] Validate Helm chart with `helm lint helm/todolist/`
- [x] T023 [US1] Test full deployment cycle: build → deploy → access → cleanup

**Checkpoint**: User Story 1 complete - developers can deploy with single command ✅

---

## Phase 4: User Story 2 - AI-Assisted Troubleshooting (Priority: P2)

**Goal**: Provide documentation for using AI tools to diagnose deployment issues

**Independent Test**: Simulate a pod failure and use documented commands to diagnose

### Documentation

- [x] T024 [P] [US2] Create AI-assisted DevOps guide in `docs/ai-assisted-devops.md`
- [x] T025 [P] [US2] Document kubectl-ai installation and usage examples in `docs/ai-assisted-devops.md`
- [x] T026 [P] [US2] Document Kagent setup and diagnostic commands in `docs/ai-assisted-devops.md`
- [x] T027 [US2] Add troubleshooting scenarios with AI tool examples in `docs/ai-assisted-devops.md`
- [x] T028 [US2] Add fallback manual commands for each AI tool scenario

**Checkpoint**: User Story 2 complete - AI troubleshooting documentation available

---

## Phase 5: User Story 3 - Container Image Building with AI Assistance (Priority: P2)

**Goal**: Document Docker Gordon usage for optimizing container images

**Independent Test**: Use documented commands to analyze and optimize Dockerfiles

### Documentation

- [x] T029 [P] [US3] Add Docker Gordon section to `docs/ai-assisted-devops.md`
- [x] T030 [US3] Document image optimization workflow with Docker Gordon
- [x] T031 [US3] Add Dockerfile best practices checklist to documentation

**Checkpoint**: User Story 3 complete - Docker Gordon documentation available

---

## Phase 6: User Story 4 - Configuration Management (Priority: P3)

**Goal**: Enable environment-specific configuration via ConfigMaps and Secrets

**Independent Test**: Deploy with modified values.yaml and verify pods pick up new config

### Implementation

- [x] T032 [P] [US4] Add environment-specific values files: `helm/todolist/values-dev.yaml`
- [x] T033 [US4] Document configuration override workflow in `docs/configuration.md`
- [x] T034 [US4] Add ConfigMap hot-reload annotation to deployments (if applicable)
- [x] T035 [US4] Add Makefile target for config-only updates: `make update-config`

**Checkpoint**: User Story 4 complete - configuration management documented and working

---

## Phase 7: User Story 5 - Service Scaling (Priority: P3)

**Goal**: Enable horizontal scaling of backend pods

**Independent Test**: Scale backend to 3 replicas and verify all pods receive traffic

### Implementation

- [x] T036 [P] [US5] Configure backend Deployment for HPA support in `helm/todolist/templates/backend-deployment.yaml`
- [x] T037 [P] [US5] Create HorizontalPodAutoscaler template in `helm/todolist/templates/hpa.yaml` (optional)
- [x] T038 [US5] Add Makefile target for scaling: `make scale-backend REPLICAS=3`
- [x] T039 [US5] Document scaling procedures in `docs/scaling.md`

**Checkpoint**: User Story 5 complete - backend scaling functional

---

## Phase 8: Optional Enhancements

**Purpose**: Additional features that enhance but are not required for core functionality

### Ingress (Optional)

- [x] T040 [P] Create Ingress template in `helm/todolist/templates/ingress.yaml`
- [x] T041 Document Ingress setup with `minikube addons enable ingress` in `README-K8S.md`

### Network Policies (Optional)

- [x] T042 [P] Create NetworkPolicy template in `helm/todolist/templates/networkpolicy.yaml`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T043 [P] Create deployment README in `README-K8S.md`
- [x] T044 [P] Add architecture diagram to documentation
- [x] T045 [P] Create troubleshooting guide section in `README-K8S.md`
- [x] T046 Run end-to-end deployment validation per `specs/008-k8s-minikube-helm/quickstart.md`
- [x] T047 Verify all Makefile targets work correctly
- [x] T048 Update main project README with Kubernetes deployment section

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
     ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
     ↓
┌────┴────┬────────────┬────────────┬────────────┐
↓         ↓            ↓            ↓            ↓
Phase 3   Phase 4      Phase 5      Phase 6      Phase 7
(US1-P1)  (US2-P2)     (US3-P2)     (US4-P3)     (US5-P3)
MVP 🎯    AI Docs      Docker Docs  Config Mgmt  Scaling
     ↓         ↓            ↓            ↓            ↓
     └─────────┴────────────┴────────────┴────────────┘
                            ↓
                    Phase 8 (Optional)
                            ↓
                    Phase 9 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (P1) | Foundational | Phase 2 complete |
| US2 (P2) | US1 (needs working deployment) | Phase 3 complete |
| US3 (P2) | Foundational | Phase 2 complete |
| US4 (P3) | US1 (needs working deployment) | Phase 3 complete |
| US5 (P3) | US1 (needs working deployment) | Phase 3 complete |

### Within Each Phase

- Tasks marked [P] can run in parallel
- Templates before scripts
- Implementation before validation
- Documentation can proceed in parallel with implementation

---

## Parallel Execution Examples

### Phase 2: Foundational (Parallelizable)

```bash
# Parallel Group 1: Dockerfiles
- T004 [P] Create frontend Dockerfile
- T007 [P] Update backend Dockerfile

# Parallel Group 2: Frontend configs
- T005 [P] Next.js standalone config
- T006 [P] Frontend health endpoint

# Parallel Group 3: Helm base
- T012 [P] ConfigMap template
- T013 [P] Secret template
```

### Phase 3: User Story 1 (Parallelizable)

```bash
# Parallel Group 1: Deployment templates
- T014 [P] [US1] Frontend Deployment
- T015 [P] [US1] Backend Deployment
- T016 [P] [US1] Frontend Service
- T017 [P] [US1] Backend Service

# Parallel Group 2: Scripts
- T018 [P] [US1] Prerequisites check
- T019 [P] [US1] Image build script
- T020 [P] [US1] Pod wait script
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (10 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (10 tasks)
4. **STOP and VALIDATE**: Test deployment cycle
5. Deploy/demo if ready - MVP complete!

### Suggested Order for Single Developer

```
Day 1: Phase 1 + Phase 2 (T001-T013)
       - Set up structure
       - Create Dockerfiles
       - Create Helm chart base

Day 2: Phase 3 (T014-T023)
       - Deploy templates
       - Automation scripts
       - Makefile
       - Validation

Day 3: Phase 4-5 (T024-T031)
       - AI tools documentation
       - Docker Gordon docs

Day 4: Phase 6-7 (T032-T039)
       - Configuration management
       - Scaling implementation

Day 5: Phase 8-9 (T040-T048)
       - Optional enhancements
       - Polish and README
```

---

## Task Summary

| Phase | Name | Tasks | Parallelizable |
|-------|------|-------|----------------|
| 1 | Setup | 3 | 2 |
| 2 | Foundational | 10 | 7 |
| 3 | US1: Deploy (MVP) | 10 | 7 |
| 4 | US2: AI Troubleshooting | 5 | 3 |
| 5 | US3: Docker Gordon | 3 | 1 |
| 6 | US4: Configuration | 4 | 1 |
| 7 | US5: Scaling | 4 | 2 |
| 8 | Optional | 3 | 2 |
| 9 | Polish | 6 | 3 |
| **Total** | | **48** | **28** |

### Tasks Per User Story

| User Story | Priority | Tasks | Description |
|------------|----------|-------|-------------|
| US1 | P1 | 10 | Core deployment capability (MVP) |
| US2 | P2 | 5 | AI troubleshooting documentation |
| US3 | P2 | 3 | Docker Gordon documentation |
| US4 | P3 | 4 | Configuration management |
| US5 | P3 | 4 | Service scaling |

### MVP Scope

**Minimum Viable Product = Phase 1 + Phase 2 + Phase 3**
- **Total MVP Tasks**: 23
- **Delivers**: Full deployment capability with single command
- **Independent Test**: `make deploy` → access frontend → create task → cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- MVP (Phase 1-3) can be deployed before adding documentation phases
