# Research: Kubernetes Local Deployment with Agentic DevOps

**Feature**: 006-k8s-minikube-deploy
**Date**: 2026-01-19
**Status**: Complete

## 1. AI-DevOps Tool Selection

### Decision: Use both kubectl-ai and Kagent with Docker Gordon

**Rationale**:
- **kubectl-ai**: Best for quick manifest generation from natural language. Lightweight, single binary, fast iteration.
- **Kagent**: Full-featured Helm agent with safety protocols, dry-run recommendations, and CNCF Sandbox status (production-ready patterns).
- **Docker Gordon**: Built into Docker Desktop, provides Dockerfile optimization without additional setup.

**Alternatives Considered**:
| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| kubectl-ai only | Simple, fast | Limited Helm-specific features | Use for quick manifest prototyping |
| Kagent only | Full Helm support, safety features | Requires Helm chart installation, steeper learning curve | Use for final chart generation |
| Neither (manual) | Full control | Defeats Agentic DevOps requirement | Rejected |

## 2. kubectl-ai Installation & Configuration

### Installation (Windows)

**Option A: Krew (Recommended)**
```powershell
# Install Krew first if not available
kubectl krew install kubectl-ai
```

**Option B: Direct Download**
```powershell
# Download from GitHub releases
Invoke-WebRequest -Uri "https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai_windows_amd64.exe" -OutFile "kubectl-ai.exe"
# Move to PATH or kubectl plugins directory
```

### Configuration
```powershell
# Set environment variables (use Gemini-compatible endpoint or OpenAI)
$env:OPENAI_API_KEY = "<api-key>"
$env:OPENAI_DEPLOYMENT_NAME = "gpt-4"  # or compatible model
```

### Usage for Helm Chart Generation
```bash
# Generate deployment manifest
kubectl ai "create a deployment for fastapi backend with 2 replicas, port 8000, resource limits 512Mi memory"

# Generate service manifest
kubectl ai "create a NodePort service for fastapi-backend deployment on port 8000"

# Generate configmap
kubectl ai "create a configmap with keys API_VERSION=v1 and DEBUG=false"
```

## 3. Kagent Installation & Configuration

### Installation (Windows/Cross-platform)

**Step 1: Install Kagent CLI**
```bash
# Using Homebrew (if available on WSL2)
brew install kagent

# Or download from GitHub releases
```

**Step 2: Install CRDs**
```bash
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds
```

**Step 3: Install Kagent (Demo profile for local dev)**
```bash
kagent install --profile demo
```

### Configuration
```bash
export OPENAI_API_KEY=<your-api-key>
```

### Helm Agent Usage
```bash
# List releases
kagent invoke -t "List all Helm releases in default namespace" --agent helm-agent

# Install chart
kagent invoke -t "Install the todolist-pro chart from ./charts/todolist-pro" --agent helm-agent

# Upgrade with values
kagent invoke -t "Upgrade todolist-pro release with values from values-local.yaml" --agent helm-agent
```

## 4. Docker Gordon Configuration

### Enabling in Docker Desktop

1. Open Docker Desktop
2. Navigate to **Settings** → **Beta features** (or Features in development)
3. Enable **Docker AI** / **Ask Gordon**
4. Accept terms of service
5. Apply and restart Docker Desktop

### Usage for Dockerfile Optimization

**Via Docker Desktop UI:**
- Click "Ask Gordon" in the left sidebar
- Upload or reference existing Dockerfile
- Request optimization suggestions

**Via CLI:**
```bash
docker ai "optimize my FastAPI Dockerfile for production"
docker ai "create multi-stage build for Next.js application"
```

### Optimization Patterns Recommended

1. **Multi-stage builds** - Separate build and runtime stages
2. **Layer optimization** - Combine RUN commands, order by change frequency
3. **Security hardening** - Non-root user, minimal base images
4. **.dockerignore** - Exclude node_modules, __pycache__, .git, .env

## 5. Helm Chart Structure Design

### Decision: Umbrella Chart with Subcharts

**Structure**:
```
charts/
└── todolist-pro/
    ├── Chart.yaml              # Umbrella chart definition
    ├── values.yaml             # Default values
    ├── values-local.yaml       # Local Minikube overrides
    ├── templates/
    │   ├── _helpers.tpl        # Template helpers
    │   ├── secrets.yaml        # Shared secrets
    │   └── NOTES.txt           # Post-install instructions
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
```

**Rationale**:
- Subcharts allow independent versioning of frontend/backend
- Umbrella chart manages shared resources (secrets, ingress)
- Values hierarchy enables environment-specific overrides

**Alternatives Considered**:
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Single flat chart | Simpler | Harder to maintain independently | Rejected |
| Separate charts + Helmfile | Maximum flexibility | Additional tooling required | Rejected for simplicity |
| Umbrella with subcharts | Balance of modularity and simplicity | Slightly more complex structure | Selected |

## 6. Docker Image Strategy

### Decision: Minikube Built-in Registry with docker-env

**Approach**:
```bash
# Point local Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly into Minikube
docker build -t todolist-frontend:local ./frontend
docker build -t todolist-backend:local ./backend
```

**Rationale**:
- No external registry required
- Fastest iteration for local development
- Images immediately available to Minikube pods

**Alternatives Considered**:
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Docker Hub | Standard, widely supported | Requires push/pull, slower iteration | For production only |
| Local registry (registry:2) | Standard Docker registry | Additional container to manage | Rejected for simplicity |
| minikube docker-env | Fastest, no network overhead | Minikube-specific | Selected |
| minikube image load | Works without docker-env | Slower than direct build | Fallback option |

## 7. Service Exposure Strategy

### Decision: NodePort for Frontend, ClusterIP for Backend

**Configuration**:
- **Frontend**: NodePort service (accessible via `minikube service` command)
- **Backend**: ClusterIP service (internal only, accessed by frontend via K8s DNS)

**Access Pattern**:
```bash
# Get frontend URL
minikube service todolist-pro-frontend --url

# Backend accessed internally via:
# http://todolist-pro-backend.default.svc.cluster.local:8000
```

**Rationale**:
- NodePort provides easy browser access without Ingress controller
- ClusterIP for backend keeps internal services secure
- `minikube service` command handles port forwarding automatically

**Alternatives Considered**:
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Ingress with nginx | Production-like | Requires ingress controller setup | Out of scope |
| LoadBalancer | Simple | Not supported natively in Minikube | Rejected |
| NodePort + ClusterIP | Simple, effective | Different from production | Selected for local dev |

## 8. Environment Configuration Strategy

### Decision: Three-tier Configuration

**Tier 1: Helm values.yaml (defaults)**
```yaml
frontend:
  replicaCount: 1
  image:
    repository: todolist-frontend
    tag: local
  resources:
    limits:
      memory: 512Mi
      cpu: 500m
```

**Tier 2: values-local.yaml (environment overrides)**
```yaml
# Minikube-specific settings
global:
  environment: local

secrets:
  databaseUrl: "postgresql://..."  # Neon connection string
  geminiApiKey: ""                 # Placeholder, set via --set
  betterAuthSecret: ""             # Placeholder, set via --set
```

**Tier 3: Command-line --set (secrets)**
```bash
helm install todolist-pro ./charts/todolist-pro \
  -f values-local.yaml \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.geminiApiKey="$GEMINI_API_KEY" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET"
```

**Rationale**:
- Secrets never stored in files committed to Git
- Clear separation of defaults, environment config, and sensitive values
- Easy to switch environments by changing values file

## 9. Health Check Configuration

### Backend Health Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

### Frontend Health Probes

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30  # Next.js build takes time
  periodSeconds: 15

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 20
  periodSeconds: 10
```

## 10. Resource Limits

### Decision: Conservative Limits for Minikube

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 256Mi | 512Mi |
| Backend | 100m | 500m | 256Mi | 512Mi |

**Rationale**:
- Minikube typically has limited resources (4 CPU, 8GB recommended)
- Conservative limits prevent resource starvation
- Can scale up in production

## References

- kubectl-ai GitHub: https://github.com/sozercan/kubectl-ai
- Kagent Documentation: https://kagent.dev/docs
- Docker Gordon: https://docs.docker.com/ai/gordon/
- Helm Best Practices: https://helm.sh/docs/chart_best_practices/
- Minikube Handbook: https://minikube.sigs.k8s.io/docs/handbook/
