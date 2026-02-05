# TodoList Pro - Kubernetes Deployment Guide

Deploy TodoList Pro to a local Kubernetes cluster using Minikube and Helm.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                         │
│                                                              │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │    Frontend     │         │     Backend     │            │
│  │   (Next.js)     │ ──────► │   (FastAPI)     │            │
│  │   NodePort      │         │   ClusterIP     │            │
│  │   :30080        │         │   :8000         │            │
│  └────────┬────────┘         └────────┬────────┘            │
│           │                           │                      │
│           ▼                           ▼                      │
│  ┌─────────────────────────────────────────────┐            │
│  │           ConfigMap & Secrets                │            │
│  └─────────────────────────────────────────────┘            │
│                                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Neon PostgreSQL │
                  │   (External)     │
                  └─────────────────┘
```

## Prerequisites

- Docker Desktop or Docker Engine
- Minikube 1.30+
- Helm 3.x
- kubectl CLI

### Quick Check

```bash
make check
```

## Quick Start

### 1. Clone and Configure

```bash
# Copy example values file
cp helm/todolist/values-local.yaml.example values-local.yaml

# Edit with your credentials
# Required: databaseUrl, betterAuthSecret
```

### 2. Deploy

```bash
# Full deployment (check + build + deploy)
make all

# Or step by step:
make check          # Verify prerequisites
make minikube-start # Start Minikube
make build          # Build Docker images
make deploy         # Deploy to Kubernetes
```

### 3. Access

```bash
# Get the frontend URL
minikube service todolist-frontend --url

# Or use port forwarding
kubectl port-forward svc/todolist-frontend 3000:80
```

## Configuration

### values-local.yaml

```yaml
secrets:
  # Required: PostgreSQL connection string
  databaseUrl: "postgresql+asyncpg://user:pass@host/db?ssl=require"

  # Required: Better Auth secret (32+ chars)
  betterAuthSecret: "your-secret-key"

  # Optional: Gemini API key for AI features
  geminiApiKey: ""

# Optional: Resource overrides
frontend:
  replicas: 1
  resources:
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  replicas: 1
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| BETTER_AUTH_SECRET | Authentication secret key | Yes |
| GEMINI_API_KEY | Gemini API key | No |

## Commands Reference

| Command | Description |
|---------|-------------|
| `make check` | Verify all prerequisites |
| `make build` | Build Docker images |
| `make deploy` | Deploy to Kubernetes |
| `make status` | Show deployment status |
| `make logs-frontend` | View frontend logs |
| `make logs-backend` | View backend logs |
| `make scale-backend REPLICAS=3` | Scale backend pods |
| `make update-config` | Apply config changes |
| `make cleanup` | Remove all resources |

## Troubleshooting

### Pod Not Starting?

```bash
# Check pod events
kubectl describe pod -l app=todolist

# Check logs
kubectl logs -l app=todolist --all-containers
```

### Image Not Found?

```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
make build
```

### Database Connection Failed?

```bash
# Verify secret
kubectl get secret todolist-secrets -o yaml

# Check backend logs
make logs-backend
```

### Service Not Accessible?

```bash
# Check service status
kubectl get svc -l app.kubernetes.io/name=todolist

# Use port forwarding as alternative
kubectl port-forward svc/todolist-frontend 3000:80
```

## AI-Assisted Troubleshooting

Install AI tools for enhanced diagnostics:

```bash
# kubectl-ai for natural language queries
kubectl-ai "why is my backend pod crashing?"

# Kagent for diagnostics
kagent diagnose deployment/todolist-backend
```

See [AI-Assisted DevOps Guide](docs/ai-assisted-devops.md) for details.

## Scaling

### Manual Scaling

```bash
# Scale backend to 3 replicas
make scale-backend REPLICAS=3

# Or directly with kubectl
kubectl scale deployment todolist-backend --replicas=3
```

### Auto-Scaling (Optional)

Enable HPA in values.yaml:

```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
```

## Directory Structure

```
.
├── Makefile                    # Deployment automation
├── values-local.yaml           # Your local config (gitignored)
├── helm/
│   └── todolist/
│       ├── Chart.yaml          # Chart metadata
│       ├── values.yaml         # Default values
│       ├── .helmignore         # Files to ignore
│       └── templates/          # Kubernetes manifests
├── scripts/
│   ├── check-prereqs.sh        # Prerequisites check
│   ├── build-images.sh         # Image build script
│   └── wait-for-pods.sh        # Pod readiness wait
├── docs/
│   └── ai-assisted-devops.md   # AI tools guide
└── README-K8S.md               # This file
```

## Next Steps

- [ ] Configure Ingress for custom domain
- [ ] Set up monitoring with Prometheus/Grafana
- [ ] Enable TLS with cert-manager
- [ ] Implement GitOps with ArgoCD

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
