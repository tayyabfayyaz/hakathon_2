# Data Model: Kubernetes Resources for TodoList Pro

**Feature**: 006-k8s-minikube-deploy
**Date**: 2026-01-19

## Overview

This document defines the Kubernetes resource entities required to deploy TodoList Pro on Minikube. These are not database entities but Kubernetes API objects that will be managed via Helm Charts.

---

## 1. Helm Chart Entity

### Chart.yaml (Umbrella)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| apiVersion | string | Helm chart API version | v2 |
| name | string | Chart name | todolist-pro |
| version | semver | Chart version | 1.0.0 |
| appVersion | string | Application version | 1.0.0 |
| description | string | Chart description | TodoList Pro Kubernetes deployment |
| type | string | Chart type | application |
| dependencies | array | Subchart references | [{name: frontend}, {name: backend}] |

### Relationships
- Contains 2 subcharts: frontend, backend
- Manages shared resources: Secrets
- References values.yaml for configuration

---

## 2. Deployment Entity

### Frontend Deployment

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| metadata.name | string | Deployment name | todolist-pro-frontend |
| metadata.labels | map | K8s labels | app: todolist-pro, component: frontend |
| spec.replicas | int | Pod count | Default: 1 |
| spec.selector | map | Pod selector | matchLabels: app.kubernetes.io/name: frontend |
| spec.template.spec.containers[0].name | string | Container name | frontend |
| spec.template.spec.containers[0].image | string | Docker image | todolist-frontend:local |
| spec.template.spec.containers[0].ports[0].containerPort | int | Container port | 3000 |
| spec.template.spec.containers[0].envFrom | array | Config/Secret refs | ConfigMap, Secret refs |
| spec.template.spec.containers[0].resources | object | Resource limits | limits: {memory: 512Mi, cpu: 500m} |
| spec.template.spec.containers[0].livenessProbe | object | Health check | httpGet: {path: /, port: 3000} |
| spec.template.spec.containers[0].readinessProbe | object | Ready check | httpGet: {path: /, port: 3000} |

### Backend Deployment

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| metadata.name | string | Deployment name | todolist-pro-backend |
| metadata.labels | map | K8s labels | app: todolist-pro, component: backend |
| spec.replicas | int | Pod count | Default: 1 |
| spec.selector | map | Pod selector | matchLabels: app.kubernetes.io/name: backend |
| spec.template.spec.containers[0].name | string | Container name | backend |
| spec.template.spec.containers[0].image | string | Docker image | todolist-backend:local |
| spec.template.spec.containers[0].ports[0].containerPort | int | Container port | 8000 |
| spec.template.spec.containers[0].envFrom | array | Config/Secret refs | ConfigMap, Secret refs |
| spec.template.spec.containers[0].resources | object | Resource limits | limits: {memory: 512Mi, cpu: 500m} |
| spec.template.spec.containers[0].livenessProbe | object | Health check | httpGet: {path: /health, port: 8000} |
| spec.template.spec.containers[0].readinessProbe | object | Ready check | httpGet: {path: /health, port: 8000} |

### State Transitions

```
Deployment Created → Pods Pending → Pods Running → Ready
                  ↓
             Pods Failed → Restarting (if liveness fails)
```

---

## 3. Service Entity

### Frontend Service (NodePort)

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| metadata.name | string | Service name | todolist-pro-frontend |
| spec.type | string | Service type | NodePort |
| spec.selector | map | Pod selector | app.kubernetes.io/name: frontend |
| spec.ports[0].port | int | Service port | 3000 |
| spec.ports[0].targetPort | int | Container port | 3000 |
| spec.ports[0].nodePort | int | External port | Auto-assigned (30000-32767) |

### Backend Service (ClusterIP)

| Field | Type | Description | Constraint |
|-------|------|-------------|------------|
| metadata.name | string | Service name | todolist-pro-backend |
| spec.type | string | Service type | ClusterIP |
| spec.selector | map | Pod selector | app.kubernetes.io/name: backend |
| spec.ports[0].port | int | Service port | 8000 |
| spec.ports[0].targetPort | int | Container port | 8000 |

### Relationships
- Frontend Service → selects Frontend Deployment pods
- Backend Service → selects Backend Deployment pods
- Frontend pods → access Backend via Service DNS

---

## 4. Secret Entity

### Application Secrets

| Field | Type | Description | Sensitivity |
|-------|------|-------------|-------------|
| metadata.name | string | Secret name | todolist-pro-secrets |
| type | string | Secret type | Opaque |
| data.DATABASE_URL | base64 | Neon PostgreSQL connection string | HIGH |
| data.GEMINI_API_KEY | base64 | Google Gemini API key | HIGH |
| data.BETTER_AUTH_SECRET | base64 | JWT signing secret | HIGH |
| data.CORS_ORIGINS | base64 | Allowed CORS origins | LOW |

### Validation Rules
- DATABASE_URL: Must be valid PostgreSQL connection string starting with `postgresql://`
- GEMINI_API_KEY: Non-empty string
- BETTER_AUTH_SECRET: Minimum 32 characters for security
- CORS_ORIGINS: Comma-separated list of valid URLs

### Security Constraints
- Never committed to Git in plain text
- Passed via `helm install --set` or external secret management
- Base64 encoded in Kubernetes (not encrypted by default)

---

## 5. ConfigMap Entity

### Frontend ConfigMap

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| metadata.name | string | ConfigMap name | todolist-pro-frontend-config |
| data.NEXT_PUBLIC_API_URL | string | Backend API URL | http://todolist-pro-backend:8000 |
| data.BETTER_AUTH_URL | string | Auth service URL | http://localhost:3000 |

### Backend ConfigMap

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| metadata.name | string | ConfigMap name | todolist-pro-backend-config |
| data.API_VERSION | string | API version string | v1 |
| data.DEBUG | string | Debug mode flag | false |
| data.PORT | string | Server port | 8000 |

### Relationships
- Deployments mount ConfigMaps as environment variables via `envFrom`
- Non-sensitive values only (secrets use Secret entity)

---

## 6. Values Configuration Entity

### values.yaml Structure

```yaml
global:
  environment: local
  imagePullPolicy: Never  # For minikube docker-env

frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: todolist-frontend
    tag: local
  service:
    type: NodePort
    port: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  config:
    nextPublicApiUrl: "http://todolist-pro-backend:8000"

backend:
  enabled: true
  replicaCount: 1
  image:
    repository: todolist-backend
    tag: local
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  config:
    apiVersion: "v1"
    debug: "false"

secrets:
  # These should be passed via --set, not stored in file
  databaseUrl: ""
  geminiApiKey: ""
  betterAuthSecret: ""
  corsOrigins: "http://localhost:3000"
```

---

## Resource Relationships Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Helm Chart: todolist-pro                  │
├─────────────────────────────────────────────────────────────┤
│  values.yaml ──────────────────────────────────────────┐    │
│       │                                                 │    │
│       ▼                                                 ▼    │
│  ┌─────────────┐     ┌─────────────┐     ┌────────────────┐ │
│  │   Secret    │     │  ConfigMap  │     │   ConfigMap    │ │
│  │  (shared)   │     │  (frontend) │     │   (backend)    │ │
│  └──────┬──────┘     └──────┬──────┘     └───────┬────────┘ │
│         │                   │                     │          │
│         ▼                   ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Deployments                          │ │
│  │  ┌──────────────────┐       ┌──────────────────┐       │ │
│  │  │     Frontend     │       │      Backend     │       │ │
│  │  │   (Next.js)      │──────▶│   (FastAPI)      │       │ │
│  │  │   Port: 3000     │ K8s   │   Port: 8000     │       │ │
│  │  └────────┬─────────┘ DNS   └────────┬─────────┘       │ │
│  └───────────┼──────────────────────────┼─────────────────┘ │
│              │                          │                    │
│              ▼                          ▼                    │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │  Service (NodePort) │    │  Service (ClusterIP)│         │
│  │  External: 3xxxx    │    │  Internal only      │         │
│  └──────────┬──────────┘    └──────────┬──────────┘         │
└─────────────┼───────────────────────────┼───────────────────┘
              │                           │
              ▼                           ▼
        Browser Access              External Neon DB
        (minikube service)          (PostgreSQL)
```

---

## Validation Checklist

- [ ] All Deployments have resource limits defined
- [ ] All Deployments have health probes configured
- [ ] Secrets contain no plain-text sensitive data in Git
- [ ] Services correctly select their target Deployments
- [ ] ConfigMaps contain only non-sensitive configuration
- [ ] values.yaml provides sensible defaults
- [ ] Chart.yaml has correct dependency references
