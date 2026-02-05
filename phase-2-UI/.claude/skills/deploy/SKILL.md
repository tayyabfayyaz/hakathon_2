---
name: deploy
description: Deploy applications to Kubernetes clusters (Minikube, AKS, GKE) using Docker, Helm, Kustomize, and Dapr. Use when deploying, releasing, shipping code to production, staging, or development environments.
argument-hint: "[environment] [platform]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
context: fork
agent: general-purpose
---

# Cloud Deployment Agent

You are an autonomous cloud deployment agent. Deploy applications to Kubernetes clusters across multiple cloud providers.

## Arguments

- **Environment**: `$ARGUMENTS[0]` (dev, staging, production) - defaults to dev
- **Platform**: `$ARGUMENTS[1]` (local, aks, gke, both) - auto-detected if not specified

## Phase 1: Prerequisites Check

Verify required tools are available:

```bash
# Check prerequisites
docker --version
kubectl version --client
helm version
```

For cloud deployments:
- Azure: `az version`
- GCP: `gcloud version`
- Local: `minikube version`

## Phase 2: Context Detection

Detect deployment target:

```bash
# Get current Kubernetes context
kubectl config current-context

# Check cluster info
kubectl cluster-info
kubectl get nodes
```

**Auto-detection rules:**
- Context contains `minikube` → Local deployment
- Context contains `aks` → Azure AKS
- Context contains `gke` → Google GKE

## Phase 3: Build Docker Images

Build images for the target registry:

```bash
# For local (Minikube)
eval $(minikube docker-env)
docker build -t todolist-frontend:local -f frontend/Dockerfile frontend/
docker build -t todolist-backend:local -f backend/Dockerfile backend/

# For Azure ACR
az acr login --name <acr-name>
docker build -t <acr>.azurecr.io/todolist-frontend:latest -f frontend/Dockerfile frontend/
docker push <acr>.azurecr.io/todolist-frontend:latest

# For GCP Artifact Registry
gcloud auth configure-docker <region>-docker.pkg.dev
docker build -t <region>-docker.pkg.dev/<project>/<repo>/todolist-frontend:latest -f frontend/Dockerfile frontend/
docker push <region>-docker.pkg.dev/<project>/<repo>/todolist-frontend:latest
```

## Phase 4: Deploy Dapr (if needed)

```bash
# Check if Dapr is installed
dapr status -k || {
  helm repo add dapr https://dapr.github.io/helm-charts/
  helm repo update
  helm upgrade --install dapr dapr/dapr \
    --namespace dapr-system \
    --create-namespace \
    --wait
}

# Apply Dapr components
kubectl apply -f deploy/dapr/config/
kubectl apply -f deploy/dapr/components/
```

## Phase 5: Deploy Application

**Using Helm (preferred):**
```bash
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --create-namespace \
  --values helm/todolist/values.yaml \
  --wait --timeout 10m
```

**Using Kustomize:**
```bash
kubectl apply -k deploy/kubernetes/overlays/<platform>
```

## Phase 6: Validation

```bash
# Check deployment status
kubectl get all -n todolist
kubectl rollout status deployment/todolist-frontend -n todolist
kubectl rollout status deployment/todolist-backend -n todolist

# Health checks
kubectl get pods -n todolist -o wide
kubectl get endpoints -n todolist
```

## Phase 7: Report

Provide deployment summary:
- Environment deployed
- Services running
- Access URLs
- Any warnings or issues

## Production Safeguard

**IMPORTANT**: If deploying to production, STOP and ask for explicit confirmation before proceeding.

## Additional Resources

- For local deployment details, see [deploy-local skill](../deploy-local/SKILL.md)
- For Azure-specific steps, see [deploy-azure skill](../deploy-azure/SKILL.md)
- For GCP-specific steps, see [deploy-gcp skill](../deploy-gcp/SKILL.md)
