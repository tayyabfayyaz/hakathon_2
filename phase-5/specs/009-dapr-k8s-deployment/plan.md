# Implementation Plan: Dapr Microservices Deployment on AKS and GKE

**Branch**: `009-dapr-k8s-deployment` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-dapr-k8s-deployment/spec.md`

## Summary

Deploy a production-ready sample microservices application demonstrating all major Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Service Invocation) on both Azure Kubernetes Service and Google Kubernetes Engine. The solution uses declarative Kubernetes manifests, Helm charts for Dapr installation, and GitHub Actions for CI/CD, with comprehensive monitoring via Prometheus/Grafana and centralized logging.

## Technical Context

**Language/Version**: Python 3.11 (microservices), YAML (configurations), Bash/PowerShell (scripts)
**Primary Dependencies**:
- Dapr 1.12+ (runtime and CLI)
- Helm 3.x (package manager)
- Docker (containerization)
- kubectl (Kubernetes CLI)
- Azure CLI / Google Cloud CLI

**Storage**:
- Primary: Azure Cosmos DB (AKS) / Google Cloud Firestore (GKE)
- Fallback: Redis (both platforms)

**Testing**:
- pytest (Python unit tests)
- kubectl + shell scripts (integration/smoke tests)
- Dapr CLI validation commands

**Target Platform**:
- Azure Kubernetes Service (AKS) - Kubernetes 1.27+
- Google Kubernetes Engine (GKE) - Kubernetes 1.27+

**Project Type**: Multi-service Kubernetes deployment (Infrastructure as Code)

**Performance Goals**:
- 100+ messages/minute throughput
- Pod startup < 5 minutes
- Message delivery < 5 seconds

**Constraints**:
- State operations < 2 seconds
- No hardcoded secrets
- RBAC and network policies required

**Scale/Scope**:
- 2 microservices (publisher, subscriber)
- 3-node cluster default
- Single region deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Test-First | ✅ PASS | Tests defined for each Dapr capability; smoke tests for deployment validation |
| Library-First | ✅ PASS | Services are independent, self-contained Python applications |
| Simplicity | ✅ PASS | Minimal viable setup with clear fallbacks; no over-engineering |
| Observability | ✅ PASS | Prometheus/Grafana for metrics; Fluentd for logs; Dapr metrics endpoints |
| Security | ✅ PASS | RBAC, network policies, cloud-native secret stores; no plaintext secrets |

## Project Structure

### Documentation (this feature)

```text
specs/009-dapr-k8s-deployment/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity models
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: API contracts and Dapr component schemas
│   ├── pubsub-messages.yaml
│   ├── state-schema.yaml
│   └── service-api.yaml
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
# Kubernetes/Dapr Deployment Project Structure
src/
├── services/
│   ├── publisher/
│   │   ├── app.py              # Publisher service code
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── subscriber/
│       ├── app.py              # Subscriber service code
│       ├── requirements.txt
│       └── Dockerfile
└── shared/
    └── utils.py                # Shared utilities (logging, health checks)

deploy/
├── dapr/
│   ├── components/
│   │   ├── pubsub-kafka.yaml       # Kafka Pub/Sub component
│   │   ├── pubsub-redis.yaml       # Redis Pub/Sub fallback
│   │   ├── statestore-cosmosdb.yaml
│   │   ├── statestore-firestore.yaml
│   │   ├── statestore-redis.yaml   # Redis state fallback
│   │   ├── secretstore-keyvault.yaml
│   │   ├── secretstore-gcp.yaml
│   │   └── binding-cron.yaml       # Cron input binding
│   └── config/
│       └── config.yaml             # Dapr configuration
├── kubernetes/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── publisher-deployment.yaml
│   │   ├── publisher-service.yaml
│   │   ├── subscriber-deployment.yaml
│   │   ├── subscriber-service.yaml
│   │   ├── network-policies.yaml
│   │   └── rbac.yaml
│   ├── overlays/
│   │   ├── aks/
│   │   │   ├── kustomization.yaml
│   │   │   └── patches/
│   │   └── gke/
│   │       ├── kustomization.yaml
│   │       └── patches/
│   └── monitoring/
│       ├── prometheus/
│       │   ├── deployment.yaml
│       │   ├── configmap.yaml
│       │   └── service.yaml
│       ├── grafana/
│       │   ├── deployment.yaml
│       │   ├── dashboards/
│       │   └── service.yaml
│       └── fluentd/
│           ├── daemonset.yaml
│           └── configmap.yaml
└── helm/
    └── values/
        ├── dapr-values.yaml
        └── monitoring-values.yaml

.github/
└── workflows/
    ├── ci.yaml                 # Build and test
    └── deploy.yaml             # Deploy to AKS/GKE

scripts/
├── setup-aks.sh
├── setup-gke.sh
├── install-dapr.sh
├── deploy.sh
├── validate.sh
└── cleanup.sh

tests/
├── unit/
│   ├── test_publisher.py
│   └── test_subscriber.py
├── integration/
│   ├── test_pubsub.sh
│   ├── test_state.sh
│   └── test_invocation.sh
└── smoke/
    └── validate-deployment.sh
```

**Structure Decision**: Multi-service Kubernetes deployment with Kustomize overlays for environment-specific configurations (AKS vs GKE). Dapr components separated by capability for maintainability.

## Complexity Tracking

No constitution violations requiring justification. The project follows standard Kubernetes/Dapr patterns with appropriate fallbacks.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster (AKS/GKE)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐        ┌─────────────────────────┐            │
│  │   Publisher Service     │        │   Subscriber Service     │            │
│  │  ┌─────────┐ ┌───────┐  │        │  ┌─────────┐ ┌───────┐  │            │
│  │  │  App    │ │ Dapr  │  │        │  │  App    │ │ Dapr  │  │            │
│  │  │ (Python)│ │Sidecar│  │        │  │ (Python)│ │Sidecar│  │            │
│  │  └────┬────┘ └───┬───┘  │        │  └────┬────┘ └───┬───┘  │            │
│  └───────┼──────────┼──────┘        └───────┼──────────┼──────┘            │
│          │          │                        │          │                   │
│          │    ┌─────┴────────────────────────┴─────┐    │                   │
│          │    │         Dapr Control Plane          │    │                   │
│          │    │  (sidecar-injector, placement,      │    │                   │
│          │    │   operator, sentry)                 │    │                   │
│          │    └─────────────────────────────────────┘    │                   │
│          │                                               │                   │
│  ┌───────┴───────────────────────────────────────────────┴───────┐          │
│  │                    Dapr Building Blocks                        │          │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │          │
│  │  │ Pub/Sub │ │  State  │ │ Binding │ │ Secrets │ │ Service │ │          │
│  │  │ (Kafka/ │ │ (Cosmos/│ │  (Cron) │ │(KeyVault│ │  Invoke │ │          │
│  │  │  Redis) │ │Firestore│ │         │ │/SecMgr) │ │         │ │          │
│  │  └────┬────┘ └────┬────┘ └─────────┘ └────┬────┘ └─────────┘ │          │
│  └───────┼───────────┼────────────────────────┼──────────────────┘          │
└──────────┼───────────┼────────────────────────┼─────────────────────────────┘
           │           │                        │
           ▼           ▼                        ▼
    ┌──────────┐ ┌──────────┐            ┌──────────┐
    │  Kafka/  │ │ CosmosDB/│            │Key Vault/│
    │  Redis   │ │ Firestore│            │ SecretMgr│
    │ (Cloud)  │ │ (Cloud)  │            │ (Cloud)  │
    └──────────┘ └──────────┘            └──────────┘
```

## CI/CD Pipeline Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Push/PR to  │───▶│  Build &     │───▶│  Push to     │───▶│  Deploy to   │
│  main branch │    │  Test        │    │  Registry    │    │  K8s Cluster │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                           │                   │                    │
                           ▼                   ▼                    ▼
                    - Run pytest        - ACR (Azure)        - kubectl apply
                    - Lint Python       - Artifact Reg       - Verify pods
                    - Build images        (GCP)              - Smoke tests
```

## Technology Decisions (Summary)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Application Language | Python 3.11 | Simple, widely understood, excellent Dapr SDK |
| Primary Pub/Sub | Kafka (Confluent/Redpanda) | Production-grade, spec requirement |
| Fallback Pub/Sub | Redis Streams | Simple setup, no external account needed |
| AKS State Store | Azure Cosmos DB | Native Azure integration, managed service |
| GKE State Store | Google Firestore | Native GCP integration, managed service |
| Fallback State | Redis | Universal, works on both platforms |
| AKS Secrets | Azure Key Vault | Native integration, managed identities |
| GKE Secrets | Google Secret Manager | Native integration, workload identity |
| Monitoring | Prometheus + Grafana | Industry standard, Dapr native support |
| Logging | Fluentd | Flexible, cloud-agnostic, K8s native |
| K8s Config Mgmt | Kustomize | Built into kubectl, handles overlays well |
| CI/CD | GitHub Actions | Spec requirement, wide adoption |
