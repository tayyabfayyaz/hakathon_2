#!/usr/bin/env bash
set -euo pipefail

# GKE Cluster Setup Script
PROJECT_ID="${GCP_PROJECT_ID:-}"
CLUSTER_NAME="${CLUSTER_NAME:-dapr-demo-gke}"
ZONE="${ZONE:-us-central1-a}"
REGION="${REGION:-us-central1}"
NODE_COUNT="${NODE_COUNT:-3}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-2}"

if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: GCP_PROJECT_ID environment variable is required"
  exit 1
fi

echo "=== GKE Cluster Setup ==="
echo "Project:     $PROJECT_ID"
echo "Cluster:     $CLUSTER_NAME"
echo "Zone:        $ZONE"
echo "Node Count:  $NODE_COUNT"

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "ERROR: Google Cloud CLI (gcloud) is required"; exit 1; }

# Set project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable container.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --quiet

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create dapr-demo \
  --repository-format=docker \
  --location="$REGION" \
  --description="Dapr demo container images" \
  --quiet 2>/dev/null || echo "Repository already exists."

# Create GKE cluster
echo "Creating GKE cluster (this may take several minutes)..."
gcloud container clusters create "$CLUSTER_NAME" \
  --zone "$ZONE" \
  --num-nodes "$NODE_COUNT" \
  --machine-type "$MACHINE_TYPE" \
  --enable-network-policy \
  --workload-pool="${PROJECT_ID}.svc.id.goog" \
  --quiet

# Get credentials
echo "Fetching cluster credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$ZONE"

# Verify connection
echo "Verifying cluster connection..."
kubectl get nodes

echo ""
echo "=== GKE cluster setup complete ==="
echo "Next: Run './scripts/install-dapr.sh' to install Dapr."
