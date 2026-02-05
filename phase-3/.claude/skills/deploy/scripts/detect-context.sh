#!/bin/bash
# Detect Kubernetes Context and Platform
# Outputs JSON with deployment context information

set -e

# Get current context
CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")

# Detect platform
PLATFORM="unknown"
if echo "$CONTEXT" | grep -qi "minikube"; then
    PLATFORM="local"
elif echo "$CONTEXT" | grep -qi "aks"; then
    PLATFORM="aks"
elif echo "$CONTEXT" | grep -qi "gke"; then
    PLATFORM="gke"
elif echo "$CONTEXT" | grep -qi "docker-desktop"; then
    PLATFORM="docker-desktop"
elif echo "$CONTEXT" | grep -qi "kind"; then
    PLATFORM="kind"
fi

# Get cluster info
CLUSTER_INFO=$(kubectl cluster-info 2>/dev/null | head -1 || echo "Not connected")

# Get node count
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo "0")

# Check if Dapr is installed
DAPR_INSTALLED="false"
if kubectl get namespace dapr-system &>/dev/null; then
    DAPR_INSTALLED="true"
fi

# Check if Helm is available
HELM_AVAILABLE="false"
if command -v helm &>/dev/null; then
    HELM_AVAILABLE="true"
fi

# Output JSON
cat <<EOF
{
  "context": "$CONTEXT",
  "platform": "$PLATFORM",
  "cluster_info": "$CLUSTER_INFO",
  "node_count": $NODE_COUNT,
  "dapr_installed": $DAPR_INSTALLED,
  "helm_available": $HELM_AVAILABLE
}
EOF
