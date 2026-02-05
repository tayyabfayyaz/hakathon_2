# Tasks: Dapr Microservices Deployment on AKS and GKE

**Input**: Design documents from `/specs/009-dapr-k8s-deployment/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Integration and smoke tests included per spec requirements (deployment validation, pub/sub flows, state operations).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Initialize project structure and shared utilities

- [x] T001 Create project directory structure per plan.md layout
- [x] T002 [P] Initialize Python project with Flask dependencies in src/services/publisher/requirements.txt
- [x] T003 [P] Initialize Python project with Flask dependencies in src/services/subscriber/requirements.txt
- [x] T004 [P] Create shared utilities module in src/shared/utils.py (logging, health checks)
- [x] T005 [P] Create .gitignore for Python, Docker, Kubernetes artifacts
- [x] T006 [P] Create README.md with project overview and quickstart reference

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Dapr components and Kubernetes base manifests that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Dapr Installation

- [x] T007 Create Dapr Helm values file in deploy/helm/values/dapr-values.yaml
- [x] T008 Create Dapr installation script in scripts/install-dapr.sh

### Kubernetes Base Manifests

- [x] T009 [P] Create namespace manifest in deploy/kubernetes/base/namespace.yaml
- [x] T010 [P] Create base kustomization file in deploy/kubernetes/base/kustomization.yaml
- [x] T011 [P] Create RBAC configuration in deploy/kubernetes/base/rbac.yaml
- [x] T012 [P] Create network policies in deploy/kubernetes/base/network-policies.yaml

### Dapr Configuration

- [x] T013 Create Dapr configuration file in deploy/dapr/config/config.yaml

### Platform Setup Scripts

- [x] T014 [P] Create AKS cluster setup script in scripts/setup-aks.sh
- [x] T015 [P] Create GKE cluster setup script in scripts/setup-gke.sh
- [x] T016 Create deployment orchestration script in scripts/deploy.sh
- [x] T017 Create cleanup script in scripts/cleanup.sh

**Checkpoint**: Foundation ready - Dapr can be installed, base K8s manifests available

---

## Phase 3: User Story 1 - Deploy Dapr-enabled Microservices (Priority: P1) 🎯 MVP

**Goal**: Deploy publisher and subscriber services with Dapr sidecars to Kubernetes

**Independent Test**: Run `kubectl get pods -n dapr-demo` and verify 2/2 containers running for each service

### Smoke Tests for US1

- [x] T018 [P] [US1] Create deployment validation script in tests/smoke/validate-deployment.sh

### Publisher Service Implementation

- [x] T019 [P] [US1] Create publisher Flask application in src/services/publisher/app.py
- [x] T020 [P] [US1] Create publisher Dockerfile in src/services/publisher/Dockerfile
- [x] T021 [US1] Create publisher deployment manifest in deploy/kubernetes/base/publisher-deployment.yaml
- [x] T022 [US1] Create publisher service manifest in deploy/kubernetes/base/publisher-service.yaml

### Subscriber Service Implementation

- [x] T023 [P] [US1] Create subscriber Flask application in src/services/subscriber/app.py
- [x] T024 [P] [US1] Create subscriber Dockerfile in src/services/subscriber/Dockerfile
- [x] T025 [US1] Create subscriber deployment manifest in deploy/kubernetes/base/subscriber-deployment.yaml
- [x] T026 [US1] Create subscriber service manifest in deploy/kubernetes/base/subscriber-service.yaml

### Kustomize Overlays

- [x] T027 [P] [US1] Create AKS kustomization overlay in deploy/kubernetes/overlays/aks/kustomization.yaml
- [x] T028 [P] [US1] Create GKE kustomization overlay in deploy/kubernetes/overlays/gke/kustomization.yaml

**Checkpoint**: Services deploy with Dapr sidecars (2/2 containers), health endpoints respond

---

## Phase 4: User Story 2 - Pub/Sub Communication (Priority: P1)

**Goal**: Enable message publishing via Dapr Pub/Sub between publisher and subscriber

**Independent Test**: Trigger publisher endpoint and verify message appears in subscriber logs

### Integration Tests for US2

- [x] T029 [P] [US2] Create pub/sub integration test script in tests/integration/test_pubsub.sh

### Dapr Pub/Sub Components

- [x] T030 [P] [US2] Create Kafka Pub/Sub component in deploy/dapr/components/pubsub-kafka.yaml
- [x] T031 [P] [US2] Create Redis Pub/Sub fallback component in deploy/dapr/components/pubsub-redis.yaml

### Publisher Pub/Sub Implementation

- [x] T032 [US2] Add Pub/Sub publishing logic to src/services/publisher/app.py (/publish endpoint)
- [x] T033 [US2] Add Dapr SDK dependency to src/services/publisher/requirements.txt

### Subscriber Pub/Sub Implementation

- [x] T034 [US2] Add topic subscription endpoint (/events/orders) to src/services/subscriber/app.py
- [x] T035 [US2] Add subscription declaration endpoint (/dapr/subscribe) to src/services/subscriber/app.py
- [x] T036 [US2] Add Dapr SDK dependency to src/services/subscriber/requirements.txt

**Checkpoint**: Publisher can send messages, subscriber receives and logs them

---

## Phase 5: User Story 3 - State Management (Priority: P2)

**Goal**: Persist processed message state using Dapr state store

**Independent Test**: Call state API and verify data persists across service restarts

### Integration Tests for US3

- [x] T037 [P] [US3] Create state store integration test script in tests/integration/test_state.sh

### Dapr State Store Components

- [x] T038 [P] [US3] Create Azure Cosmos DB state store component in deploy/dapr/components/statestore-cosmosdb.yaml
- [x] T039 [P] [US3] Create Google Firestore state store component in deploy/dapr/components/statestore-firestore.yaml
- [x] T040 [P] [US3] Create Redis state store fallback component in deploy/dapr/components/statestore-redis.yaml

### Subscriber State Implementation

- [x] T041 [US3] Add state save logic to message handler in src/services/subscriber/app.py
- [x] T042 [US3] Add state query endpoint (/state/{key}) to src/services/subscriber/app.py

**Checkpoint**: Subscriber stores processed message state, state can be queried

---

## Phase 6: User Story 4 - Cron Binding (Priority: P2)

**Goal**: Automatically trigger publisher on schedule via Dapr cron binding

**Independent Test**: Observe scheduled messages in publisher logs at 30-second intervals

### Dapr Cron Binding Component

- [x] T043 [US4] Create cron input binding component in deploy/dapr/components/binding-cron.yaml

### Publisher Cron Handler

- [x] T044 [US4] Add cron binding handler endpoint (/cron-binding) to src/services/publisher/app.py
- [x] T045 [US4] Integrate cron trigger with publish logic in src/services/publisher/app.py

**Checkpoint**: Publisher automatically publishes messages on schedule

---

## Phase 7: User Story 5 - Secrets Management (Priority: P2)

**Goal**: Retrieve credentials from cloud-native secret stores via Dapr

**Independent Test**: Services start successfully using secrets from Key Vault or Secret Manager

### Dapr Secret Store Components

- [x] T046 [P] [US5] Create Azure Key Vault secret store component in deploy/dapr/components/secretstore-keyvault.yaml
- [x] T047 [P] [US5] Create GCP Secret Manager component in deploy/dapr/components/secretstore-gcp.yaml

### AKS Secret Store Integration

- [x] T048 [US5] Create AKS-specific secret patches in deploy/kubernetes/overlays/aks/patches/secrets-patch.yaml

### GKE Secret Store Integration

- [x] T049 [US5] Create GKE-specific secret patches in deploy/kubernetes/overlays/gke/patches/secrets-patch.yaml

### Update Pub/Sub Components for Secrets

- [x] T050 [US5] Update pubsub-kafka.yaml to use secretKeyRef for credentials

**Checkpoint**: Services retrieve secrets from cloud secret stores, no hardcoded credentials

---

## Phase 8: User Story 6 - Service Invocation (Priority: P2)

**Goal**: Enable direct service-to-service calls via Dapr service invocation

**Independent Test**: Call subscriber endpoint that invokes publisher health via Dapr

### Integration Tests for US6

- [x] T051 [P] [US6] Create service invocation test script in tests/integration/test_invocation.sh

### Service Invocation Implementation

- [x] T052 [US6] Add invoke-subscriber endpoint to src/services/publisher/app.py
- [x] T053 [US6] Add invoke-publisher endpoint to src/services/subscriber/app.py (calls publisher /health via Dapr)

**Checkpoint**: Services can invoke each other through Dapr, mTLS enabled

---

## Phase 9: User Story 7 - CI/CD Pipeline (Priority: P3)

**Goal**: Automate build and deployment via GitHub Actions

**Independent Test**: Push code to main branch and verify automatic deployment completes

### GitHub Actions Workflows

- [x] T054 [P] [US7] Create CI workflow for build and test in .github/workflows/ci.yaml
- [x] T055 [P] [US7] Create deploy workflow for AKS/GKE in .github/workflows/deploy.yaml

### CI Workflow Components

- [x] T056 [US7] Add pytest job to ci.yaml for unit tests
- [x] T057 [US7] Add Docker build job to ci.yaml for both services
- [x] T058 [US7] Add image push job to ci.yaml (ACR/Artifact Registry)

### Deploy Workflow Components

- [x] T059 [US7] Add AKS deployment job to deploy.yaml
- [x] T060 [US7] Add GKE deployment job to deploy.yaml
- [x] T061 [US7] Add smoke test job to deploy.yaml

**Checkpoint**: Code push triggers build, test, and deployment automatically

---

## Phase 10: User Story 8 - Monitoring and Observability (Priority: P3)

**Goal**: Deploy Prometheus/Grafana for metrics, Fluentd for logs

**Independent Test**: Access Grafana dashboard and see Dapr metrics

### Prometheus Deployment

- [x] T062 [P] [US8] Create Prometheus deployment in deploy/kubernetes/monitoring/prometheus/deployment.yaml
- [x] T063 [P] [US8] Create Prometheus ConfigMap with Dapr scrape config in deploy/kubernetes/monitoring/prometheus/configmap.yaml
- [x] T064 [P] [US8] Create Prometheus service in deploy/kubernetes/monitoring/prometheus/service.yaml

### Grafana Deployment

- [x] T065 [P] [US8] Create Grafana deployment in deploy/kubernetes/monitoring/grafana/deployment.yaml
- [x] T066 [P] [US8] Create Grafana service in deploy/kubernetes/monitoring/grafana/service.yaml
- [x] T067 [US8] Create Dapr dashboard JSON in deploy/kubernetes/monitoring/grafana/dashboards/dapr-dashboard.json

### Fluentd Logging

- [x] T068 [P] [US8] Create Fluentd DaemonSet in deploy/kubernetes/monitoring/fluentd/daemonset.yaml
- [x] T069 [P] [US8] Create Fluentd ConfigMap in deploy/kubernetes/monitoring/fluentd/configmap.yaml

### Helm Values for Monitoring

- [x] T070 [US8] Create monitoring Helm values in deploy/helm/values/monitoring-values.yaml

**Checkpoint**: Grafana shows Dapr metrics, Fluentd aggregates logs

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and cleanup

- [x] T071 [P] Create unit tests for publisher in tests/unit/test_publisher.py
- [x] T072 [P] Create unit tests for subscriber in tests/unit/test_subscriber.py
- [x] T073 Create comprehensive validation script in scripts/validate.sh
- [x] T074 Update quickstart.md with actual tested commands
- [x] T075 Run full deployment validation on AKS
- [x] T076 Run full deployment validation on GKE
- [x] T077 Security audit: verify no hardcoded secrets in any files

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────────┐
                                                              │
Phase 2 (Foundational) ──────────────────────────────────────┤
    ├── Dapr installation                                     │
    ├── K8s base manifests                                    │
    └── Platform scripts                                      │
                                                              │
    ┌─────────────────────────────────────────────────────────┘
    │ BLOCKS ALL USER STORIES
    ▼
┌───────────────────────────────────────────────────────────────┐
│ USER STORIES (can run in parallel after Phase 2)              │
│                                                               │
│  Phase 3: US1 (Deploy) ────┐                                  │
│       ▼                    │                                  │
│  Phase 4: US2 (Pub/Sub)    │ P1 Priority (MVP)                │
│                            │                                  │
│  Phase 5: US3 (State) ─────┤                                  │
│  Phase 6: US4 (Cron)       │ P2 Priority                      │
│  Phase 7: US5 (Secrets)    │                                  │
│  Phase 8: US6 (Invocation) ┤                                  │
│                            │                                  │
│  Phase 9: US7 (CI/CD) ─────┤ P3 Priority                      │
│  Phase 10: US8 (Monitoring)┤                                  │
└───────────────────────────────────────────────────────────────┘
                            │
                            ▼
                Phase 11 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Deploy) | Phase 2 | None (first story) |
| US2 (Pub/Sub) | US1 | US3, US4, US5, US6 |
| US3 (State) | US1 | US2, US4, US5, US6 |
| US4 (Cron) | US2 | US3, US5, US6 |
| US5 (Secrets) | Phase 2 | US2, US3, US4, US6 |
| US6 (Invocation) | US1 | US2, US3, US4, US5 |
| US7 (CI/CD) | US1 | US8 |
| US8 (Monitoring) | US1 | US7 |

### Within Each Phase

1. Tests (if any) can run in parallel [P]
2. Models/Components before services
3. Services before integration
4. All [P] tasks within same phase can run in parallel

---

## Parallel Execution Examples

### Phase 2: Foundational (parallel setup)

```bash
# All base K8s manifests can be created in parallel:
Task: "Create namespace manifest in deploy/kubernetes/base/namespace.yaml"
Task: "Create RBAC configuration in deploy/kubernetes/base/rbac.yaml"
Task: "Create network policies in deploy/kubernetes/base/network-policies.yaml"
Task: "Create base kustomization file in deploy/kubernetes/base/kustomization.yaml"

# Platform scripts can be created in parallel:
Task: "Create AKS cluster setup script in scripts/setup-aks.sh"
Task: "Create GKE cluster setup script in scripts/setup-gke.sh"
```

### Phase 3: User Story 1 (parallel service creation)

```bash
# Publisher and subscriber services can be built in parallel:
Task: "Create publisher Flask application in src/services/publisher/app.py"
Task: "Create subscriber Flask application in src/services/subscriber/app.py"

Task: "Create publisher Dockerfile in src/services/publisher/Dockerfile"
Task: "Create subscriber Dockerfile in src/services/subscriber/Dockerfile"

# Kustomize overlays can be created in parallel:
Task: "Create AKS kustomization overlay"
Task: "Create GKE kustomization overlay"
```

### Phase 5-8: P2 User Stories (parallel across stories)

```bash
# These stories can be worked on in parallel by different team members:
Developer A: US3 (State Management)
Developer B: US4 (Cron Binding)
Developer C: US5 (Secrets)
Developer D: US6 (Service Invocation)
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 - Deploy services
4. **VALIDATE**: `kubectl get pods -n dapr-demo` shows 2/2 containers
5. Complete Phase 4: US2 - Pub/Sub messaging
6. **VALIDATE**: Publisher sends, subscriber receives
7. **STOP**: MVP complete - working Dapr demo with Pub/Sub

### Incremental Delivery

| Milestone | Stories Complete | Value Delivered |
|-----------|------------------|-----------------|
| MVP | US1 + US2 | Deployed services with Pub/Sub |
| +State | +US3 | Persistent message processing |
| +Automation | +US4 | Scheduled publishing |
| +Security | +US5 | Cloud-native secrets |
| +Mesh | +US6 | Service-to-service calls |
| +DevOps | +US7 | Automated deployment |
| +Observability | +US8 | Full monitoring stack |

### Task Count Summary

| Phase | Tasks | Parallelizable |
|-------|-------|----------------|
| Phase 1: Setup | 6 | 4 |
| Phase 2: Foundational | 11 | 6 |
| Phase 3: US1 (Deploy) | 11 | 6 |
| Phase 4: US2 (Pub/Sub) | 8 | 3 |
| Phase 5: US3 (State) | 6 | 4 |
| Phase 6: US4 (Cron) | 3 | 0 |
| Phase 7: US5 (Secrets) | 5 | 2 |
| Phase 8: US6 (Invocation) | 3 | 1 |
| Phase 9: US7 (CI/CD) | 8 | 2 |
| Phase 10: US8 (Monitoring) | 9 | 6 |
| Phase 11: Polish | 7 | 2 |
| **TOTAL** | **77** | **36 (47%)** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [USn] label maps task to specific user story for traceability
- Each user story is independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Redis fallback components enable testing without cloud accounts
- Verify tests fail before implementing (TDD where applicable)
