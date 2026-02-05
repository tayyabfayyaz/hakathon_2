#!/bin/bash
# check-prereqs.sh - Verify all prerequisites for Kubernetes deployment

set -e

echo "🔍 Checking prerequisites for TodoList Pro Kubernetes deployment..."
echo ""

ERRORS=0

# Check Docker
echo -n "Docker: "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    echo "✅ Installed (v${DOCKER_VERSION})"
else
    echo "❌ Not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check if Docker is running
echo -n "Docker daemon: "
if docker info &> /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
    ERRORS=$((ERRORS + 1))
fi

# Check Minikube
echo -n "Minikube: "
if command -v minikube &> /dev/null; then
    MINIKUBE_VERSION=$(minikube version --short 2>/dev/null | head -1)
    echo "✅ Installed (${MINIKUBE_VERSION})"
else
    echo "❌ Not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check if Minikube is running
echo -n "Minikube cluster: "
if minikube status &> /dev/null; then
    echo "✅ Running"
else
    echo "⚠️  Not running (run: minikube start)"
fi

# Check Helm
echo -n "Helm: "
if command -v helm &> /dev/null; then
    HELM_VERSION=$(helm version --short 2>/dev/null | cut -d '+' -f1)
    echo "✅ Installed (${HELM_VERSION})"
else
    echo "❌ Not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check kubectl
echo -n "kubectl: "
if command -v kubectl &> /dev/null; then
    KUBECTL_VERSION=$(kubectl version --client -o json 2>/dev/null | grep -o '"gitVersion": "[^"]*"' | cut -d '"' -f4)
    echo "✅ Installed (${KUBECTL_VERSION})"
else
    echo "❌ Not installed"
    ERRORS=$((ERRORS + 1))
fi

echo ""

if [ $ERRORS -gt 0 ]; then
    echo "❌ Found ${ERRORS} missing prerequisites. Please install them before continuing."
    exit 1
else
    echo "✅ All prerequisites satisfied!"
    exit 0
fi
