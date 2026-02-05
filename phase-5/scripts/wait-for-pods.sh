#!/bin/bash
# wait-for-pods.sh - Wait for all TodoList pods to be ready

set -e

NAMESPACE="${1:-default}"
TIMEOUT="${2:-120}"

echo "⏳ Waiting for TodoList pods to be ready (timeout: ${TIMEOUT}s)..."

# Wait for all pods with app=todolist label to be ready
kubectl wait --for=condition=ready pod \
    -l app=todolist \
    -n "$NAMESPACE" \
    --timeout="${TIMEOUT}s" 2>/dev/null || {
    echo ""
    echo "⚠️  Pods not ready within timeout. Checking status..."
    echo ""
    kubectl get pods -l app=todolist -n "$NAMESPACE"
    echo ""
    echo "📋 Pod descriptions:"
    kubectl describe pods -l app=todolist -n "$NAMESPACE" | head -100
    exit 1
}

echo ""
echo "✅ All pods are ready!"
echo ""

# Show pod status
kubectl get pods -l app=todolist -n "$NAMESPACE"

# Get frontend URL
echo ""
echo "🌐 Frontend URL:"
minikube service todolist-frontend --url -n "$NAMESPACE" 2>/dev/null || echo "Use: minikube service todolist-frontend --url"
