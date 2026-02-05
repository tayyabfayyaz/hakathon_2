#!/bin/bash
# build-images.sh - Build Docker images in Minikube's Docker daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🐳 Building Docker images for TodoList Pro..."
echo ""

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Starting Minikube..."
    minikube start --cpus=2 --memory=4096 --driver=docker
fi

# Point Docker to Minikube's daemon
echo "📌 Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

# Build frontend image
echo ""
echo "🏗️  Building frontend image..."
docker build -t todolist-frontend:local "$PROJECT_ROOT/frontend"

# Build backend image
echo ""
echo "🏗️  Building backend image..."
docker build -t todolist-backend:local "$PROJECT_ROOT/backend"

# Verify images
echo ""
echo "✅ Images built successfully!"
echo ""
docker images | grep todolist

echo ""
echo "🎉 Build complete! Run 'make deploy' to deploy to Kubernetes."
