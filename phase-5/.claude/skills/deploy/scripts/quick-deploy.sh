#!/bin/bash
# Quick Deploy Script
# Usage: ./quick-deploy.sh [environment] [platform]

set -e

ENVIRONMENT=${1:-dev}
PLATFORM=${2:-auto}

echo "=== Quick Deploy ==="
echo "Environment: $ENVIRONMENT"
echo "Platform: $PLATFORM"
echo ""

# Auto-detect platform if not specified
if [ "$PLATFORM" = "auto" ]; then
    CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
    if echo "$CONTEXT" | grep -qi "minikube"; then
        PLATFORM="local"
    elif echo "$CONTEXT" | grep -qi "aks"; then
        PLATFORM="aks"
    elif echo "$CONTEXT" | grep -qi "gke"; then
        PLATFORM="gke"
    else
        echo "ERROR: Could not auto-detect platform. Please specify: local, aks, or gke"
        exit 1
    fi
    echo "Auto-detected platform: $PLATFORM"
fi

# Set namespace based on environment
NAMESPACE="todolist"
if [ "$ENVIRONMENT" = "staging" ]; then
    NAMESPACE="todolist-staging"
elif [ "$ENVIRONMENT" = "production" ]; then
    NAMESPACE="todolist-prod"
fi

echo "Namespace: $NAMESPACE"
echo ""

# Platform-specific deployment
case $PLATFORM in
    local)
        echo "=== Local (Minikube) Deployment ==="

        # Use Minikube Docker
        eval $(minikube docker-env)

        # Build images
        echo "Building images..."
        docker build -t todolist-frontend:local -f frontend/Dockerfile frontend/
        docker build -t todolist-backend:local -f backend/Dockerfile backend/

        # Deploy with Helm
        echo "Deploying with Helm..."
        helm upgrade --install todolist helm/todolist/ \
            --namespace $NAMESPACE \
            --create-namespace \
            --set frontend.image.repository=todolist-frontend \
            --set frontend.image.tag=local \
            --set frontend.image.pullPolicy=Never \
            --set backend.image.repository=todolist-backend \
            --set backend.image.tag=local \
            --set backend.image.pullPolicy=Never \
            --wait

        # Get access URL
        echo ""
        echo "=== Access ==="
        minikube service todolist-frontend -n $NAMESPACE --url
        ;;

    aks)
        echo "=== Azure AKS Deployment ==="

        # Deploy with Kustomize
        echo "Deploying with Kustomize..."
        kubectl apply -k deploy/kubernetes/overlays/aks

        # Wait for rollout
        kubectl rollout status deployment/todolist-frontend -n $NAMESPACE --timeout=300s
        kubectl rollout status deployment/todolist-backend -n $NAMESPACE --timeout=300s
        ;;

    gke)
        echo "=== Google GKE Deployment ==="

        # Deploy with Kustomize
        echo "Deploying with Kustomize..."
        kubectl apply -k deploy/kubernetes/overlays/gke

        # Wait for rollout
        kubectl rollout status deployment/todolist-frontend -n $NAMESPACE --timeout=300s
        kubectl rollout status deployment/todolist-backend -n $NAMESPACE --timeout=300s
        ;;

    *)
        echo "ERROR: Unknown platform '$PLATFORM'"
        exit 1
        ;;
esac

echo ""
echo "=== Deployment Complete ==="
kubectl get all -n $NAMESPACE
