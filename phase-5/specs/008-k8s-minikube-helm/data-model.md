# Data Model: Kubernetes Deployment Resources

**Feature**: 008-k8s-minikube-helm
**Date**: 2026-02-01

## Kubernetes Resource Entities

### 1. Frontend Deployment

**Kind**: Deployment
**Purpose**: Manages Next.js frontend pod replicas

| Field | Type | Description |
|-------|------|-------------|
| name | string | `todolist-frontend` |
| replicas | int | Number of pod replicas (default: 1) |
| image | string | Container image (e.g., `todolist-frontend:local`) |
| port | int | Container port (3000) |
| resources.requests.memory | string | Minimum memory (128Mi) |
| resources.requests.cpu | string | Minimum CPU (100m) |
| resources.limits.memory | string | Maximum memory (256Mi) |
| resources.limits.cpu | string | Maximum CPU (200m) |

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API URL (from ConfigMap)
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Auth URL (from ConfigMap)

---

### 2. Backend Deployment

**Kind**: Deployment
**Purpose**: Manages FastAPI backend pod replicas

| Field | Type | Description |
|-------|------|-------------|
| name | string | `todolist-backend` |
| replicas | int | Number of pod replicas (default: 1) |
| image | string | Container image (e.g., `todolist-backend:local`) |
| port | int | Container port (8000) |
| resources.requests.memory | string | Minimum memory (256Mi) |
| resources.requests.cpu | string | Minimum CPU (200m) |
| resources.limits.memory | string | Maximum memory (512Mi) |
| resources.limits.cpu | string | Maximum CPU (500m) |

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection (from Secret)
- `BETTER_AUTH_SECRET`: Auth secret (from Secret)
- `CORS_ORIGINS`: Allowed origins (from ConfigMap)
- `GEMINI_API_KEY`: AI API key (from Secret)

---

### 3. Frontend Service

**Kind**: Service
**Purpose**: Exposes frontend pods for network access

| Field | Type | Description |
|-------|------|-------------|
| name | string | `todolist-frontend` |
| type | string | `NodePort` or `ClusterIP` |
| port | int | Service port (80) |
| targetPort | int | Container port (3000) |
| nodePort | int | External port (30000-32767, optional) |

---

### 4. Backend Service

**Kind**: Service
**Purpose**: Exposes backend pods for internal cluster access

| Field | Type | Description |
|-------|------|-------------|
| name | string | `todolist-backend` |
| type | string | `ClusterIP` |
| port | int | Service port (8000) |
| targetPort | int | Container port (8000) |

---

### 5. ConfigMap

**Kind**: ConfigMap
**Purpose**: Non-sensitive application configuration

| Key | Description | Example Value |
|-----|-------------|---------------|
| `API_URL` | Backend API internal URL | `http://todolist-backend:8000` |
| `FRONTEND_URL` | Frontend URL | `http://todolist-frontend` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `API_VERSION` | API version | `1.0.0` |
| `DEBUG` | Debug mode | `false` |

---

### 6. Secret

**Kind**: Secret
**Purpose**: Sensitive configuration values

| Key | Description | Source |
|-----|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | Neon database |
| `BETTER_AUTH_SECRET` | Authentication secret | Generated |
| `GEMINI_API_KEY` | Google AI API key | User provided |

**Encoding**: Base64 (Helm manages encoding)

---

### 7. Ingress (Optional)

**Kind**: Ingress
**Purpose**: URL-based routing for production-like access

| Field | Type | Description |
|-------|------|-------------|
| name | string | `todolist-ingress` |
| host | string | `todolist.local` |
| paths | array | Routing rules |

**Paths**:
- `/` → `todolist-frontend:80`
- `/api` → `todolist-backend:8000`

---

## Resource Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        Ingress                               │
│                    (todolist.local)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   Frontend    │               │   Backend     │
│   Service     │               │   Service     │
│  (NodePort)   │               │  (ClusterIP)  │
└───────┬───────┘               └───────┬───────┘
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   Frontend    │               │   Backend     │
│  Deployment   │──────────────▶│  Deployment   │
│   (Next.js)   │   API calls   │  (FastAPI)    │
└───────┬───────┘               └───────┬───────┘
        │                               │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   ConfigMap   │               │    Secret     │
│ (non-sensitive)│              │  (sensitive)  │
└───────────────┘               └───────────────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  External DB  │
                                │    (Neon)     │
                                └───────────────┘
```

---

## State Transitions

### Pod Lifecycle

```
Pending → Running → Succeeded/Failed
    │         │
    │         └── Terminating → Terminated
    │
    └── ContainerCreating → Running
```

### Deployment Rollout

```
Progressing → Available
     │
     └── ReplicaFailure (if pods fail)
```

---

## Validation Rules

1. **Replica Count**: Must be >= 1
2. **Resource Limits**: Must be >= Resource Requests
3. **Port Numbers**: Must be 1-65535
4. **NodePort Range**: 30000-32767 (Kubernetes constraint)
5. **Secret Values**: Must be base64 encoded
6. **Image Pull Policy**: `Never` for local images, `Always` for remote
