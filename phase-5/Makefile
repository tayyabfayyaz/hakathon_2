# Makefile for TodoList Pro Kubernetes Deployment
# Usage: make [target]

.PHONY: help check minikube-start build deploy status logs-frontend logs-backend scale-backend update-config cleanup all

# Default target
help:
	@echo "TodoList Pro Kubernetes Deployment"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  check          Check prerequisites (Docker, Minikube, Helm, kubectl)"
	@echo "  minikube-start Start Minikube cluster"
	@echo "  build          Build Docker images in Minikube"
	@echo "  deploy         Deploy application to Kubernetes"
	@echo "  status         Show deployment status"
	@echo "  logs-frontend  View frontend logs"
	@echo "  logs-backend   View backend logs"
	@echo "  scale-backend  Scale backend replicas (REPLICAS=3)"
	@echo "  update-config  Update configuration only"
	@echo "  cleanup        Remove all resources"
	@echo "  all            Full deployment (check + build + deploy)"
	@echo ""

# Check prerequisites
check:
	@bash scripts/check-prereqs.sh

# Start Minikube
minikube-start:
	@echo "🚀 Starting Minikube..."
	minikube start --cpus=2 --memory=4096 --driver=docker
	@echo "✅ Minikube started"

# Build images
build:
	@bash scripts/build-images.sh

# Deploy to Kubernetes
deploy:
	@echo "🚀 Deploying TodoList Pro to Kubernetes..."
	@if [ -f values-local.yaml ]; then \
		helm upgrade --install todolist ./helm/todolist -f values-local.yaml; \
	else \
		echo "⚠️  values-local.yaml not found. Using default values."; \
		echo "   Copy helm/todolist/values-local.yaml.example to values-local.yaml and configure secrets."; \
		helm upgrade --install todolist ./helm/todolist; \
	fi
	@bash scripts/wait-for-pods.sh

# Show status
status:
	@echo "📊 TodoList Pro Deployment Status"
	@echo ""
	@echo "Pods:"
	@kubectl get pods -l app=todolist
	@echo ""
	@echo "Services:"
	@kubectl get svc -l app.kubernetes.io/name=todolist
	@echo ""
	@echo "Deployments:"
	@kubectl get deployments -l app.kubernetes.io/name=todolist

# View frontend logs
logs-frontend:
	@kubectl logs -l app.kubernetes.io/component=frontend -f --tail=100

# View backend logs
logs-backend:
	@kubectl logs -l app.kubernetes.io/component=backend -f --tail=100

# Scale backend
REPLICAS ?= 2
scale-backend:
	@echo "📈 Scaling backend to $(REPLICAS) replicas..."
	@kubectl scale deployment todolist-backend --replicas=$(REPLICAS)
	@kubectl rollout status deployment/todolist-backend

# Update configuration only
update-config:
	@echo "🔄 Updating configuration..."
	@if [ -f values-local.yaml ]; then \
		helm upgrade todolist ./helm/todolist -f values-local.yaml; \
	else \
		helm upgrade todolist ./helm/todolist; \
	fi
	@echo "✅ Configuration updated"

# Cleanup
cleanup:
	@echo "🧹 Cleaning up TodoList Pro deployment..."
	@helm uninstall todolist 2>/dev/null || echo "No Helm release found"
	@echo "✅ Cleanup complete"

# Full deployment
all: check build deploy
	@echo ""
	@echo "🎉 TodoList Pro deployed successfully!"
	@echo ""
	@echo "Access the application:"
	@minikube service todolist-frontend --url
