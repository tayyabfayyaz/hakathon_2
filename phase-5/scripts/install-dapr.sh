#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DAPR_NAMESPACE="dapr-system"
DAPR_VERSION="${DAPR_VERSION:-1.12}"

echo "=== Dapr Installation ==="
echo "Namespace: $DAPR_NAMESPACE"
echo "Version:   $DAPR_VERSION"

# Check prerequisites
command -v helm >/dev/null 2>&1 || { echo "ERROR: helm is required"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is required"; exit 1; }

# Add Dapr Helm repo
echo "Adding Dapr Helm repository..."
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Create namespace
kubectl create namespace "$DAPR_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Install Dapr
echo "Installing Dapr via Helm..."
helm upgrade --install dapr dapr/dapr \
  --namespace "$DAPR_NAMESPACE" \
  --values "$PROJECT_ROOT/deploy/helm/values/dapr-values.yaml" \
  --version "$DAPR_VERSION" \
  --wait \
  --timeout 5m

# Verify installation
echo "Verifying Dapr installation..."
kubectl get pods -n "$DAPR_NAMESPACE"

echo ""
echo "=== Dapr installation complete ==="
echo "Run 'dapr status -k' to verify all components are running."
