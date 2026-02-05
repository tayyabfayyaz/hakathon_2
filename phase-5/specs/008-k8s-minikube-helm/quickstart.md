# Quickstart: TodoList Pro Kubernetes Deployment

**Time to Deploy**: ~5 minutes

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop or Docker Engine installed
- [ ] Minikube 1.30+ installed
- [ ] Helm 3.x installed
- [ ] kubectl CLI installed

### Quick Prerequisites Check

```bash
# Check all prerequisites at once
docker --version && minikube version && helm version && kubectl version --client
```

---

## Step 1: Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Verify cluster is running
minikube status
```

---

## Step 2: Build Container Images

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build frontend image
docker build -t todolist-frontend:local ./frontend

# Build backend image
docker build -t todolist-backend:local ./backend

# Verify images exist
docker images | grep todolist
```

---

## Step 3: Configure Secrets

Create a `values-local.yaml` file with your credentials:

```yaml
secrets:
  databaseUrl: "postgresql+asyncpg://user:pass@host/db?ssl=require"
  betterAuthSecret: "your-32-char-secret-key"
  geminiApiKey: "your-gemini-api-key"  # Optional
```

---

## Step 4: Deploy with Helm

```bash
# Install the Helm chart
helm install todolist ./helm/todolist -f values-local.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=todolist --timeout=120s

# Check deployment status
kubectl get pods -l app=todolist
```

---

## Step 5: Access the Application

```bash
# Get the frontend URL
minikube service todolist-frontend --url

# Or use port forwarding
kubectl port-forward svc/todolist-frontend 3000:80
```

Open your browser to the URL displayed.

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| Check status | `kubectl get all -l app=todolist` |
| View frontend logs | `kubectl logs -l app.kubernetes.io/name=frontend -f` |
| View backend logs | `kubectl logs -l app.kubernetes.io/name=backend -f` |
| Scale backend | `kubectl scale deployment todolist-backend --replicas=3` |
| Update config | `helm upgrade todolist ./helm/todolist -f values-local.yaml` |
| Uninstall | `helm uninstall todolist` |

---

## Using Make Commands (Alternative)

If you prefer using Make:

```bash
make check          # Check prerequisites
make build          # Build images
make deploy         # Deploy to Kubernetes
make status         # View status
make logs-backend   # View backend logs
make cleanup        # Remove all resources
```

---

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
# Ensure you're using Minikube's Docker
eval $(minikube docker-env)

# Verify image exists
docker images | grep todolist
```

### Database Connection Failed?

```bash
# Check secret is created
kubectl get secret todolist-secrets -o yaml

# Test database URL from pod
kubectl exec -it deploy/todolist-backend -- python -c "import asyncpg; print('OK')"
```

---

## AI-Assisted Troubleshooting (Optional)

Install AI tools for enhanced troubleshooting:

```bash
# kubectl-ai for natural language queries
kubectl-ai "why is my backend pod crashing?"

# Kagent for diagnostics
kagent diagnose deployment/todolist-backend
```

---

## Next Steps

- [ ] Enable Ingress for custom domain access
- [ ] Configure autoscaling for production-like testing
- [ ] Set up monitoring with Prometheus/Grafana
- [ ] Explore service mesh with Istio
