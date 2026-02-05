---
name: deploy-gcp
description: Deploy applications to Google Kubernetes Engine (GKE) with Artifact Registry, Secret Manager, Firestore, and Dapr. Use when deploying to Google Cloud, setting up GKE cluster, or managing GCP resources.
argument-hint: "[environment]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob
---

# Google Kubernetes Engine (GKE) Deployment

Deploy applications to GKE with full Google Cloud ecosystem integration.

## Prerequisites

```bash
gcloud version
kubectl version --client
helm version
docker --version
```

## Authentication

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project <project-id>

# Enable required APIs
gcloud services enable container.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
```

## Infrastructure Setup (First-Time)

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
ZONE="${REGION}-a"
CLUSTER_NAME="todolist-gke"
REPO_NAME="todolist-repo"

# Create Artifact Registry
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
  --zone $ZONE \
  --num-nodes 3 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5
```

## Get Cluster Credentials

```bash
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE
kubectl get nodes
```

## Build and Push Images

```bash
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and push
docker build -t ${REGISTRY}/todolist-frontend:latest -f frontend/Dockerfile frontend/
docker build -t ${REGISTRY}/todolist-backend:latest -f backend/Dockerfile backend/
docker push ${REGISTRY}/todolist-frontend:latest
docker push ${REGISTRY}/todolist-backend:latest

# Or use Cloud Build
gcloud builds submit --tag ${REGISTRY}/todolist-frontend:latest frontend/
gcloud builds submit --tag ${REGISTRY}/todolist-backend:latest backend/
```

## Deploy Dapr

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Apply GCP-specific components
kubectl apply -f deploy/dapr/components/statestore-firestore.yaml
kubectl apply -f deploy/dapr/components/secretstore-gcp.yaml
```

## Deploy Application

**Using Kustomize (recommended):**
```bash
kubectl apply -k deploy/kubernetes/overlays/gke
```

**Using Helm:**
```bash
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --create-namespace \
  --set frontend.image.repository=${REGISTRY}/todolist-frontend \
  --set backend.image.repository=${REGISTRY}/todolist-backend \
  --wait
```

## Configure Secret Manager

```bash
# Create secrets
echo -n "<connection-string>" | gcloud secrets create database-url --data-file=-
openssl rand -base64 32 | gcloud secrets create better-auth-secret --data-file=-

# Grant access to GKE service account
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[todolist/todolist-sa]" \
  --role="roles/secretmanager.secretAccessor"
```

## Validation

```bash
kubectl get all -n todolist
kubectl get ingress -n todolist
kubectl logs -f deployment/todolist-frontend -n todolist
```

## Cleanup

```bash
# Remove application
helm uninstall todolist -n todolist

# Delete cluster
gcloud container clusters delete $CLUSTER_NAME --zone $ZONE --quiet

# Delete Artifact Registry
gcloud artifacts repositories delete $REPO_NAME --location=$REGION --quiet
```
