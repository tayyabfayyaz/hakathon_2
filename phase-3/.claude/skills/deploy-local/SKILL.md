---
name: deploy-local
description: Deploy applications to local Minikube cluster for development and testing. Use when setting up local Kubernetes environment, testing deployments locally, or running the app on Minikube.
argument-hint: "[action]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob
---

# Local Kubernetes Deployment (Minikube)

Deploy applications to local Minikube cluster for fast development iterations.

## Quick Start

```bash
# Full deployment pipeline
make all
```

Or step-by-step:
```bash
make check           # Verify prerequisites
make minikube-start  # Start Minikube
make build           # Build images
make deploy          # Deploy with Helm
make status          # Show status
```

## Prerequisites

```bash
docker --version
minikube version
kubectl version --client
helm version
```

## Start Minikube

```bash
minikube status || minikube start \
  --driver=docker \
  --cpus=2 \
  --memory=4096

# Use Minikube's Docker daemon
eval $(minikube docker-env)
```

## Build Images Locally

```bash
# Build in Minikube's Docker
docker build -t todolist-frontend:local -f frontend/Dockerfile frontend/
docker build -t todolist-backend:local -f backend/Dockerfile backend/

# Verify images
docker images | grep todolist
```

## Deploy with Helm

```bash
# Create namespace
kubectl create namespace todolist --dry-run=client -o yaml | kubectl apply -f -

# Deploy
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --set frontend.image.repository=todolist-frontend \
  --set frontend.image.tag=local \
  --set frontend.image.pullPolicy=Never \
  --set backend.image.repository=todolist-backend \
  --set backend.image.tag=local \
  --set backend.image.pullPolicy=Never \
  --wait
```

## Access Application

```bash
# Get NodePort URL
FRONTEND_PORT=$(kubectl get svc todolist-frontend -n todolist -o jsonpath='{.spec.ports[0].nodePort}')
echo "Frontend: http://$(minikube ip):${FRONTEND_PORT}"

# Or use port forwarding
kubectl port-forward svc/todolist-frontend 3000:3000 -n todolist &

# Or use minikube service
minikube service todolist-frontend -n todolist --url
```

## Useful Commands

| Action | Command |
|--------|---------|
| Status | `kubectl get all -n todolist` |
| Logs | `kubectl logs -f deployment/todolist-frontend -n todolist` |
| Dashboard | `minikube dashboard` |
| SSH | `minikube ssh` |
| Stop | `minikube stop` |
| Delete | `minikube delete` |
| Cleanup | `make cleanup` |

## Troubleshooting

**ImagePullBackOff**: Ensure using Minikube's Docker with `eval $(minikube docker-env)` and rebuild images.

**Pods Pending**: Check node resources with `kubectl describe nodes`.

**Service Unreachable**: Verify endpoints with `kubectl get endpoints -n todolist`.
