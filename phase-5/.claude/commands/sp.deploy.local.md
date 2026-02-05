---
description: Deploy applications to local Minikube cluster for development and testing with Helm and local Docker images.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# Local Kubernetes Deployment Agent (Minikube)

## Core Principle

You are an autonomous local deployment agent optimized for fast iteration cycles. Deploy applications to Minikube for development and testing without cloud dependencies.

## Quick Start

Execute the full local deployment pipeline:

```bash
make all
```

Or step-by-step:

```bash
make check           # Verify prerequisites
make minikube-start  # Start Minikube cluster
make build           # Build Docker images
make deploy          # Deploy with Helm
make status          # Show deployment status
```

---

## Phase 1: Prerequisites Check

### 1.1 Required Tools

```bash
# Verify required tools
docker --version          # Container runtime
minikube version          # Local K8s cluster
kubectl version --client  # Kubernetes CLI
helm version              # Package manager
```

### 1.2 Optional Tools

```bash
dapr version              # Dapr CLI (for distributed apps)
```

---

## Phase 2: Minikube Setup

### 2.1 Start Cluster

```bash
# Check if Minikube is running
minikube status || {
  # Start with recommended resources
  minikube start \
    --driver=docker \
    --cpus=2 \
    --memory=4096 \
    --kubernetes-version=v1.27.0
}
```

### 2.2 Configure Docker Environment

```bash
# Use Minikube's Docker daemon (avoid registry push)
eval $(minikube docker-env)

# Verify Docker is using Minikube
docker info | grep -i "Operating System"
```

### 2.3 Enable Addons (Optional)

```bash
minikube addons enable ingress       # Nginx ingress controller
minikube addons enable metrics-server # Resource metrics
minikube addons enable dashboard     # Kubernetes dashboard
```

---

## Phase 3: Build Images

### 3.1 Frontend Image

```bash
docker build -t todolist-frontend:local -f frontend/Dockerfile frontend/
```

### 3.2 Backend Image

```bash
docker build -t todolist-backend:local -f backend/Dockerfile backend/
```

### 3.3 Microservices (if applicable)

```bash
docker build -t publisher-service:local -f src/services/publisher/Dockerfile src/services/publisher/
docker build -t subscriber-service:local -f src/services/subscriber/Dockerfile src/services/subscriber/
```

### 3.4 Verify Images

```bash
docker images | grep -E "(todolist|publisher|subscriber)"
```

---

## Phase 4: Deploy Application

### 4.1 Create Namespace

```bash
kubectl create namespace todolist --dry-run=client -o yaml | kubectl apply -f -
```

### 4.2 Create Secrets (if needed)

```bash
# Check if secrets file exists
if [ -f "helm/todolist/values-local.yaml" ]; then
  echo "Using local values with secrets"
else
  # Create minimal secrets
  kubectl create secret generic todolist-secrets \
    --from-literal=DATABASE_URL="postgresql://user:pass@localhost:5432/todo" \
    --from-literal=BETTER_AUTH_SECRET="local-dev-secret-32-chars-minimum" \
    -n todolist --dry-run=client -o yaml | kubectl apply -f -
fi
```

### 4.3 Deploy with Helm

```bash
# Install or upgrade
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --values helm/todolist/values.yaml \
  --values helm/todolist/values-dev.yaml \
  --set frontend.image.repository=todolist-frontend \
  --set frontend.image.tag=local \
  --set frontend.image.pullPolicy=Never \
  --set backend.image.repository=todolist-backend \
  --set backend.image.tag=local \
  --set backend.image.pullPolicy=Never \
  --wait --timeout 5m
```

### 4.4 Wait for Pods

```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todolist -n todolist --timeout=300s
```

---

## Phase 5: Access Application

### 5.1 Get NodePort URL

```bash
# Frontend URL
FRONTEND_PORT=$(kubectl get svc todolist-frontend -n todolist -o jsonpath='{.spec.ports[0].nodePort}')
MINIKUBE_IP=$(minikube ip)
echo "Frontend: http://${MINIKUBE_IP}:${FRONTEND_PORT}"

# Backend URL
BACKEND_PORT=$(kubectl get svc todolist-backend -n todolist -o jsonpath='{.spec.ports[0].nodePort}')
echo "Backend API: http://${MINIKUBE_IP}:${BACKEND_PORT}"
```

### 5.2 Port Forwarding (Alternative)

```bash
# Forward frontend
kubectl port-forward svc/todolist-frontend 3000:3000 -n todolist &

# Forward backend
kubectl port-forward svc/todolist-backend 8000:8000 -n todolist &

echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
```

### 5.3 Minikube Service (Alternative)

```bash
# Open frontend in browser
minikube service todolist-frontend -n todolist

# Get service URL
minikube service todolist-frontend -n todolist --url
```

---

## Phase 6: Validation

### 6.1 Check Deployment Status

```bash
# All resources
kubectl get all -n todolist

# Pod details
kubectl get pods -n todolist -o wide

# Service endpoints
kubectl get endpoints -n todolist
```

### 6.2 Health Checks

```bash
# Frontend health
curl -s http://$(minikube ip):${FRONTEND_PORT}/

# Backend health
curl -s http://$(minikube ip):${BACKEND_PORT}/api/health
```

### 6.3 View Logs

```bash
# Frontend logs
kubectl logs -f deployment/todolist-frontend -n todolist

# Backend logs
kubectl logs -f deployment/todolist-backend -n todolist

# All pods
kubectl logs -f -l app.kubernetes.io/instance=todolist -n todolist --all-containers
```

---

## Utility Commands

### View Status

```bash
make status
# Or
kubectl get all -n todolist
helm list -n todolist
```

### Update Configuration

```bash
make update-config
# Or
helm upgrade todolist helm/todolist/ -n todolist --reuse-values
```

### Scale Services

```bash
# Scale backend
kubectl scale deployment/todolist-backend --replicas=3 -n todolist

# Or via Makefile
make scale-backend REPLICAS=3
```

### View Logs

```bash
make logs-frontend
make logs-backend
```

### Cleanup

```bash
make cleanup
# Or
helm uninstall todolist -n todolist
kubectl delete namespace todolist
minikube stop
```

### Full Reset

```bash
minikube delete
make all  # Start fresh
```

---

## Troubleshooting

### ImagePullBackOff

```bash
# Ensure using Minikube Docker
eval $(minikube docker-env)

# Rebuild image
docker build -t <image>:local -f <dockerfile> <context>

# Verify imagePullPolicy is Never
kubectl get deployment <name> -n todolist -o yaml | grep imagePullPolicy
```

### Pods Pending

```bash
# Check node resources
kubectl describe nodes

# Check events
kubectl get events -n todolist --sort-by='.lastTimestamp'
```

### Service Unreachable

```bash
# Check service
kubectl describe svc <service-name> -n todolist

# Check endpoints
kubectl get endpoints <service-name> -n todolist

# Check pod labels match service selector
kubectl get pods -n todolist --show-labels
```

### Minikube Issues

```bash
# Restart Minikube
minikube stop && minikube start

# Check Minikube logs
minikube logs

# Full reset
minikube delete && minikube start
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start cluster | `minikube start` |
| Stop cluster | `minikube stop` |
| Delete cluster | `minikube delete` |
| Dashboard | `minikube dashboard` |
| SSH into node | `minikube ssh` |
| Use Docker | `eval $(minikube docker-env)` |
| Get IP | `minikube ip` |
| Service URL | `minikube service <svc> -n <ns> --url` |

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).
