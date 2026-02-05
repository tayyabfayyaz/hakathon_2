#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLATFORM="${1:---platform}"
NAMESPACE="dapr-demo"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ "$PLATFORM" != "aks" && "$PLATFORM" != "gke" ]]; then
  echo "Usage: $0 --platform <aks|gke> [--namespace <namespace>]"
  exit 1
fi

echo "=== Deploying Dapr Demo ==="
echo "Platform:  $PLATFORM"
echo "Namespace: $NAMESPACE"

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is required"; exit 1; }
command -v kustomize >/dev/null 2>&1 || KUSTOMIZE="kubectl kustomize" || true

# Verify Dapr is installed
echo "Checking Dapr installation..."
kubectl get pods -n dapr-system --no-headers | grep -q "Running" || {
  echo "ERROR: Dapr is not installed. Run './scripts/install-dapr.sh' first."
  exit 1
}

# Apply Dapr configuration
echo "Applying Dapr configuration..."
kubectl apply -f "$PROJECT_ROOT/deploy/dapr/config/config.yaml"

# Apply Dapr components
echo "Applying Dapr components..."
for component in "$PROJECT_ROOT"/deploy/dapr/components/*.yaml; do
  if [ -f "$component" ]; then
    kubectl apply -f "$component"
  fi
done

# Deploy with Kustomize overlay
echo "Deploying application with $PLATFORM overlay..."
kubectl apply -k "$PROJECT_ROOT/deploy/kubernetes/overlays/$PLATFORM"

# Wait for rollout
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/publisher -n "$NAMESPACE" --timeout=300s
kubectl rollout status deployment/subscriber -n "$NAMESPACE" --timeout=300s

# Show status
echo ""
echo "=== Deployment Status ==="
kubectl get pods -n "$NAMESPACE"
kubectl get svc -n "$NAMESPACE"

echo ""
echo "=== Deployment complete ==="
echo "Run './scripts/validate.sh' to verify the deployment."
