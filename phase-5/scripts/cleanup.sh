#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="dapr-demo"
REMOVE_DAPR="${REMOVE_DAPR:-false}"

echo "=== Cleanup Dapr Demo ==="
echo "Namespace: $NAMESPACE"

# Delete application resources
echo "Deleting application deployments..."
kubectl delete -k "$PROJECT_ROOT/deploy/kubernetes/base" --ignore-not-found=true 2>/dev/null || true

# Delete Dapr components
echo "Deleting Dapr components..."
for component in "$PROJECT_ROOT"/deploy/dapr/components/*.yaml; do
  if [ -f "$component" ]; then
    kubectl delete -f "$component" --ignore-not-found=true 2>/dev/null || true
  fi
done

# Delete Dapr configuration
kubectl delete -f "$PROJECT_ROOT/deploy/dapr/config/config.yaml" --ignore-not-found=true 2>/dev/null || true

# Delete namespace
echo "Deleting namespace..."
kubectl delete namespace "$NAMESPACE" --ignore-not-found=true 2>/dev/null || true

# Optionally remove Dapr
if [ "$REMOVE_DAPR" = "true" ]; then
  echo "Removing Dapr installation..."
  helm uninstall dapr -n dapr-system 2>/dev/null || true
  kubectl delete namespace dapr-system --ignore-not-found=true 2>/dev/null || true
fi

echo ""
echo "=== Cleanup complete ==="
