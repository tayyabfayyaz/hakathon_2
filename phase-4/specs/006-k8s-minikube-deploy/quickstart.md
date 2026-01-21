# Quickstart: TodoList Pro on Minikube

**Feature**: 006-k8s-minikube-deploy
**Time to Deploy**: ~10-15 minutes (first time), ~5 minutes (subsequent)

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Minikube installed (`minikube version` returns v1.30+)
- [ ] Helm 3.x installed (`helm version` returns v3.x)
- [ ] kubectl installed (`kubectl version --client`)
- [ ] Valid Neon PostgreSQL database URL
- [ ] Valid Gemini API key (for AI chat functionality)

## Step 1: Start Minikube

```powershell
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

## Step 2: Configure Docker Environment

```powershell
# Point Docker CLI to Minikube's Docker daemon
# PowerShell:
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Or Bash/WSL:
eval $(minikube docker-env)
```

## Step 3: Build Docker Images

```powershell
# Build frontend image
docker build -t todolist-frontend:local -f frontend/Dockerfile ./frontend

# Build backend image
docker build -t todolist-backend:local -f backend/Dockerfile ./backend

# Verify images are available
docker images | Select-String "todolist"
```

## Step 4: Install AI-DevOps Tools (Optional)

### kubectl-ai

```powershell
# Using Krew (if installed)
kubectl krew install kubectl-ai

# Or download binary from GitHub releases
# https://github.com/sozercan/kubectl-ai/releases
```

### Kagent

```bash
# Install Kagent CRDs
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds

# Install Kagent
kagent install --profile demo
```

### Docker Gordon

Enable in Docker Desktop:
1. Settings → Beta features
2. Enable "Docker AI"
3. Apply and restart

## Step 5: Deploy with Helm

### Set Environment Variables

```powershell
# Set your secrets (replace with actual values)
$env:DATABASE_URL = "postgresql://user:pass@host.neon.tech/dbname?sslmode=require"
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:BETTER_AUTH_SECRET = "your-32-char-minimum-secret-here"
```

### Install the Helm Chart

```powershell
# Install TodoList Pro
helm install todolist-pro ./charts/todolist-pro `
  -f ./charts/todolist-pro/values-local.yaml `
  --set secrets.databaseUrl="$env:DATABASE_URL" `
  --set secrets.geminiApiKey="$env:GEMINI_API_KEY" `
  --set secrets.betterAuthSecret="$env:BETTER_AUTH_SECRET"
```

### Verify Deployment

```powershell
# Check pods are running
kubectl get pods -l app.kubernetes.io/instance=todolist-pro

# Wait for pods to be ready (timeout 3 minutes)
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todolist-pro --timeout=180s
```

Expected output:
```
NAME                                        READY   STATUS    RESTARTS   AGE
todolist-pro-backend-xxxxx-yyyyy            1/1     Running   0          60s
todolist-pro-frontend-xxxxx-yyyyy           1/1     Running   0          60s
```

## Step 6: Access the Application

```powershell
# Get frontend URL
minikube service todolist-pro-frontend --url

# Open in browser (auto-opens on some systems)
minikube service todolist-pro-frontend
```

## Quick Reference Commands

### View Logs

```powershell
# Frontend logs
kubectl logs -l app.kubernetes.io/name=frontend -f

# Backend logs
kubectl logs -l app.kubernetes.io/name=backend -f
```

### Check Health

```powershell
# Backend health endpoint
kubectl exec -it deploy/todolist-pro-backend -- wget -qO- http://localhost:8000/health
```

### Upgrade Deployment

```powershell
helm upgrade todolist-pro ./charts/todolist-pro `
  -f ./charts/todolist-pro/values-local.yaml `
  --set secrets.databaseUrl="$env:DATABASE_URL" `
  --set secrets.geminiApiKey="$env:GEMINI_API_KEY" `
  --set secrets.betterAuthSecret="$env:BETTER_AUTH_SECRET"
```

### Uninstall

```powershell
helm uninstall todolist-pro
```

### Stop Minikube

```powershell
minikube stop
```

## Troubleshooting

### Pods stuck in Pending

```powershell
# Check events
kubectl describe pod -l app.kubernetes.io/instance=todolist-pro

# Check resources
kubectl top nodes
minikube ssh -- free -m
```

### Image pull errors

```powershell
# Ensure docker-env is set
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Rebuild images
docker build -t todolist-frontend:local ./frontend
```

### Database connection failed

```powershell
# Verify DATABASE_URL secret
kubectl get secret todolist-pro-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test connectivity from pod
kubectl exec -it deploy/todolist-pro-backend -- python -c "import asyncpg; print('OK')"
```

### Health checks failing

```powershell
# Check probe configuration
kubectl describe deploy todolist-pro-backend | grep -A10 "Liveness:"

# Test endpoint manually
kubectl port-forward svc/todolist-pro-backend 8000:8000 &
curl http://localhost:8000/health
```

## AI-Assisted Operations

For detailed setup instructions, see the AI-DevOps documentation:
- [kubectl-ai Setup Guide](../../docs/agentic-devops/kubectl-ai-setup.md)
- [Kagent Setup Guide](../../docs/agentic-devops/kagent-setup.md)
- [Docker Gordon Guide](../../docs/agentic-devops/docker-gordon-guide.md)

### Generate Manifests with kubectl-ai

```powershell
$env:OPENAI_API_KEY = "your-openai-key"

# Generate deployment
kubectl ai "create a deployment for fastapi app with 2 replicas, 512Mi memory limit"

# Generate service
kubectl ai "create a NodePort service for the frontend deployment on port 3000"
```

### Use Kagent Helm Agent

```bash
# List current releases
kagent invoke -t "List all Helm releases" --agent helm-agent

# Upgrade with AI assistance
kagent invoke -t "Upgrade todolist-pro with 2 replicas for frontend" --agent helm-agent
```

### Optimize Dockerfiles with Gordon

In Docker Desktop:
1. Open "Ask Gordon"
2. Type: "Analyze my FastAPI Dockerfile at backend/Dockerfile and suggest optimizations"
3. Review and apply suggestions

## Success Checklist

- [ ] Minikube cluster running with sufficient resources
- [ ] Both Docker images built successfully
- [ ] Helm chart installed without errors
- [ ] All pods in Running state
- [ ] Frontend accessible via browser
- [ ] Can create and manage tasks
- [ ] AI chat responds with valid Gemini responses

## Next Steps

After successful deployment:

1. **Customize Configuration**: Edit `values-local.yaml` for your needs
2. **Scale Replicas**: `helm upgrade --set frontend.replicaCount=2`
3. **Add Ingress**: Enable nginx-ingress for production-like routing
4. **Monitor Resources**: `kubectl top pods`
