---
description: Deploy applications to Google Kubernetes Engine (GKE) with Artifact Registry, Secret Manager, Firestore, and Dapr integration.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# Google Kubernetes Engine (GKE) Deployment Agent

## Core Principle

You are an autonomous GCP deployment agent. Deploy applications to GKE with full Google Cloud ecosystem integration including Artifact Registry, Secret Manager, Firestore, and Dapr.

---

## Phase 1: Prerequisites

### 1.1 Required Tools

```bash
gcloud version                # Google Cloud CLI
kubectl version --client      # Kubernetes CLI
helm version                  # Helm
docker --version              # Docker
dapr version                  # Dapr CLI (optional)
```

### 1.2 GCP Authentication

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project <project-id>

# Verify configuration
gcloud config list
```

### 1.3 Enable Required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  compute.googleapis.com
```

---

## Phase 2: Infrastructure Setup (First-Time Only)

### 2.1 Set Variables

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
ZONE="${REGION}-a"
CLUSTER_NAME="todolist-gke"
REPO_NAME="todolist-repo"
```

### 2.2 Create Artifact Registry Repository

```bash
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="TodoList application images"
```

### 2.3 Create GKE Cluster

```bash
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --enable-ip-alias \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5
```

### 2.4 Create Firestore Database (Optional)

```bash
gcloud firestore databases create \
  --location=$REGION \
  --type=firestore-native
```

---

## Phase 3: Configure GKE Access

### 3.1 Get GKE Credentials

```bash
gcloud container clusters get-credentials $CLUSTER_NAME \
  --zone $ZONE \
  --project $PROJECT_ID
```

### 3.2 Verify Cluster Access

```bash
kubectl cluster-info
kubectl get nodes
```

### 3.3 Configure Docker Authentication

```bash
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

---

## Phase 4: Build and Push Images

### 4.1 Set Registry Variables

```bash
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"
```

### 4.2 Build and Push Frontend

```bash
# Build
docker build -t ${REGISTRY}/todolist-frontend:latest -f frontend/Dockerfile frontend/

# Push
docker push ${REGISTRY}/todolist-frontend:latest
```

### 4.3 Build and Push Backend

```bash
# Build
docker build -t ${REGISTRY}/todolist-backend:latest -f backend/Dockerfile backend/

# Push
docker push ${REGISTRY}/todolist-backend:latest
```

### 4.4 Cloud Build (Alternative - Build in Cloud)

```bash
# Build using Cloud Build
gcloud builds submit \
  --tag ${REGISTRY}/todolist-frontend:latest \
  --timeout=20m \
  frontend/

gcloud builds submit \
  --tag ${REGISTRY}/todolist-backend:latest \
  --timeout=20m \
  backend/
```

---

## Phase 5: Deploy Dapr (If Required)

### 5.1 Install Dapr Runtime

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.mtls.enabled=true \
  --set global.prometheus.enabled=true \
  --wait
```

### 5.2 Verify Dapr Installation

```bash
kubectl get pods -n dapr-system
dapr status -k
```

### 5.3 Deploy Dapr Configuration

```bash
kubectl apply -f deploy/dapr/config/config.yaml
```

### 5.4 Deploy GCP-Specific Dapr Components

```bash
# Apply GCP components
kubectl apply -f deploy/dapr/components/pubsub-kafka.yaml
kubectl apply -f deploy/dapr/components/statestore-firestore.yaml
kubectl apply -f deploy/dapr/components/secretstore-gcp.yaml
```

---

## Phase 6: Configure Secrets

### 6.1 Create Secrets in Secret Manager

```bash
# Database URL
echo -n "postgresql://user:pass@host:5432/db" | \
  gcloud secrets create database-url --data-file=-

# Auth secret
openssl rand -base64 32 | \
  gcloud secrets create better-auth-secret --data-file=-

# Kafka credentials
echo -n "kafka-broker:9092" | \
  gcloud secrets create kafka-bootstrap-servers --data-file=-
```

### 6.2 Grant Access to GKE Service Account

```bash
# Get GKE service account
GKE_SA="${PROJECT_ID}.svc.id.goog[todolist/todolist-sa]"

# Grant secret access
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:${GKE_SA}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding better-auth-secret \
  --member="serviceAccount:${GKE_SA}" \
  --role="roles/secretmanager.secretAccessor"
```

### 6.3 Create Kubernetes Secrets (Alternative)

```bash
kubectl create namespace todolist

kubectl create secret generic todolist-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --from-literal=BETTER_AUTH_SECRET="your-secret-key" \
  -n todolist
```

---

## Phase 7: Deploy Application

### 7.1 Using Kustomize (Recommended)

```bash
# Apply GKE overlay
kubectl apply -k deploy/kubernetes/overlays/gke
```

### 7.2 Using Helm

```bash
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --create-namespace \
  --set frontend.image.repository=${REGISTRY}/todolist-frontend \
  --set frontend.image.tag=latest \
  --set backend.image.repository=${REGISTRY}/todolist-backend \
  --set backend.image.tag=latest \
  --set ingress.enabled=true \
  --set ingress.className=gce \
  --wait --timeout 10m
```

### 7.3 Wait for Deployment

```bash
kubectl rollout status deployment/todolist-frontend -n todolist --timeout=300s
kubectl rollout status deployment/todolist-backend -n todolist --timeout=300s
```

---

## Phase 8: Configure Ingress

### 8.1 Using GKE Ingress (GCE)

```bash
# GKE uses the gce ingress class by default
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todolist-ingress
  namespace: todolist
  annotations:
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todolist-frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todolist-backend
            port:
              number: 8000
EOF
```

### 8.2 Get External IP

```bash
kubectl get ingress todolist-ingress -n todolist -w
```

### 8.3 Configure Cloud DNS (Optional)

```bash
EXTERNAL_IP=$(kubectl get ingress todolist-ingress -n todolist -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create DNS record
gcloud dns record-sets create todolist.example.com \
  --zone=example-zone \
  --type=A \
  --ttl=300 \
  --rrdatas=$EXTERNAL_IP
```

---

## Phase 9: Validation

### 9.1 Check Resources

```bash
kubectl get all -n todolist
kubectl get ingress -n todolist
```

### 9.2 Health Checks

```bash
# Get ingress IP
INGRESS_IP=$(kubectl get ingress todolist-ingress -n todolist -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl -s http://$INGRESS_IP/
curl -s http://$INGRESS_IP/api/health
```

### 9.3 View Logs

```bash
kubectl logs -f deployment/todolist-frontend -n todolist
kubectl logs -f deployment/todolist-backend -n todolist
```

---

## Phase 10: Monitoring Setup

### 10.1 Enable GKE Monitoring

GKE comes with Cloud Monitoring and Cloud Logging enabled by default.

```bash
# View logs in Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=todolist" --limit 50
```

### 10.2 Deploy Prometheus/Grafana (Alternative)

```bash
kubectl apply -f deploy/kubernetes/monitoring/prometheus/
kubectl apply -f deploy/kubernetes/monitoring/grafana/
```

### 10.3 Cloud Monitoring Dashboard

```bash
# Create dashboard via Console or gcloud
gcloud monitoring dashboards create --config-from-file=deploy/monitoring/gcp-dashboard.json
```

---

## CI/CD Integration

### GitHub Actions Trigger

```bash
# Trigger deployment workflow
gh workflow run deploy.yaml -f platform=gke -f environment=production
```

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Google Cloud project ID |
| `GCP_SA_KEY` | Service account key JSON |
| `GKE_CLUSTER` | GKE cluster name |
| `GKE_ZONE` | GKE cluster zone |

### Workload Identity Federation (Recommended)

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

---

## Cleanup

### Remove Application

```bash
helm uninstall todolist -n todolist
kubectl delete namespace todolist
```

### Remove GKE Cluster

```bash
gcloud container clusters delete $CLUSTER_NAME --zone $ZONE --quiet
```

### Remove All Resources

```bash
# Delete Artifact Registry
gcloud artifacts repositories delete $REPO_NAME --location=$REGION --quiet

# Delete secrets
gcloud secrets delete database-url --quiet
gcloud secrets delete better-auth-secret --quiet

# Delete cluster
gcloud container clusters delete $CLUSTER_NAME --zone $ZONE --quiet
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Get credentials | `gcloud container clusters get-credentials $CLUSTER --zone $ZONE` |
| View nodes | `kubectl get nodes` |
| Scale nodes | `gcloud container clusters resize $CLUSTER --num-nodes 5 --zone $ZONE` |
| Auth Docker | `gcloud auth configure-docker $REGION-docker.pkg.dev` |
| Push image | `docker push $REGION-docker.pkg.dev/$PROJECT/$REPO/image:tag` |
| Dapr status | `dapr status -k` |
| View secrets | `gcloud secrets list` |
| View logs | `gcloud logging read "resource.type=k8s_container"` |

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).
