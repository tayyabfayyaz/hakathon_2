# Quickstart: Dapr Microservices on AKS/GKE

**Feature**: 009-dapr-k8s-deployment
**Date**: 2026-02-03

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| kubectl | 1.27+ | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) |
| helm | 3.x | [Install Helm](https://helm.sh/docs/intro/install/) |
| docker | 20+ | [Install Docker](https://docs.docker.com/get-docker/) |
| dapr CLI | 1.12+ | [Install Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/) |
| az CLI | 2.x | [Install Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (AKS) |
| gcloud CLI | latest | [Install gcloud](https://cloud.google.com/sdk/docs/install) (GKE) |

### Cloud Accounts

- **Azure**: Active subscription with permissions to create AKS, Cosmos DB, Key Vault
- **GCP**: Active project with permissions to create GKE, Firestore, Secret Manager
- **GitHub**: Repository for CI/CD workflows
- **Kafka** (optional): Confluent Cloud or Redpanda Cloud account

### Verify Prerequisites

```bash
# Check all tools are installed
kubectl version --client
helm version
docker --version
dapr --version
az version      # For AKS
gcloud version  # For GKE
```

## Quick Deploy (5 minutes)

### Option A: Deploy to AKS

```bash
# 1. Login to Azure
az login
az account set --subscription "<subscription-id>"

# 2. Create AKS cluster (or use existing)
./scripts/setup-aks.sh

# 3. Install Dapr
./scripts/install-dapr.sh

# 4. Deploy application (uses Redis fallback by default)
./scripts/deploy.sh --platform aks --env dev

# 5. Validate deployment
./scripts/validate.sh
```

### Option B: Deploy to GKE

```bash
# 1. Login to GCP
gcloud auth login
gcloud config set project <project-id>

# 2. Create GKE cluster (or use existing)
./scripts/setup-gke.sh

# 3. Install Dapr
./scripts/install-dapr.sh

# 4. Deploy application (uses Redis fallback by default)
./scripts/deploy.sh --platform gke --env dev

# 5. Validate deployment
./scripts/validate.sh
```

## Step-by-Step Guide

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd dapr-k8s-demo

# Review configuration
cat deploy/kubernetes/base/kustomization.yaml
```

### 2. Create Kubernetes Cluster

#### AKS

```bash
# Set variables
export RESOURCE_GROUP="dapr-demo-rg"
export CLUSTER_NAME="dapr-demo-aks"
export LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 3 \
  --node-vm-size Standard_DS2_v2 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

#### GKE

```bash
# Set variables
export PROJECT_ID="your-project-id"
export CLUSTER_NAME="dapr-demo-gke"
export ZONE="us-central1-a"

# Create GKE cluster
gcloud container clusters create $CLUSTER_NAME \
  --project $PROJECT_ID \
  --zone $ZONE \
  --num-nodes 3 \
  --machine-type e2-standard-2 \
  --workload-pool=$PROJECT_ID.svc.id.goog

# Get credentials
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE
```

### 3. Install Dapr

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr (production mode with HA)
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.mtls.enabled=true \
  --wait

# Verify installation
kubectl get pods -n dapr-system
dapr status -k
```

Expected output:
```
NAME                   HEALTHY  STATUS   REPLICAS  VERSION  AGE
dapr-dashboard         True     Running  1         0.14.0   1m
dapr-operator          True     Running  3         1.12.0   1m
dapr-placement-server  True     Running  3         1.12.0   1m
dapr-sentry            True     Running  3         1.12.0   1m
dapr-sidecar-injector  True     Running  3         1.12.0   1m
```

### 4. Deploy Application

```bash
# Create namespace
kubectl create namespace dapr-demo

# Deploy Dapr components (Redis fallback)
kubectl apply -f deploy/dapr/components/pubsub-redis.yaml -n dapr-demo
kubectl apply -f deploy/dapr/components/statestore-redis.yaml -n dapr-demo
kubectl apply -f deploy/dapr/components/binding-cron.yaml -n dapr-demo

# Deploy Redis (if not using cloud services)
helm install redis bitnami/redis --namespace dapr-demo --set auth.enabled=false

# Deploy application using Kustomize
kubectl apply -k deploy/kubernetes/overlays/aks  # or gke

# Wait for pods
kubectl wait --for=condition=ready pod -l app=publisher -n dapr-demo --timeout=120s
kubectl wait --for=condition=ready pod -l app=subscriber -n dapr-demo --timeout=120s
```

### 5. Validate Deployment

```bash
# Check pods (should show 2/2 containers)
kubectl get pods -n dapr-demo

# Expected output:
# NAME                          READY   STATUS    RESTARTS   AGE
# publisher-7d8f9c6b5-xxxxx     2/2     Running   0          1m
# subscriber-6c9d8b7a4-xxxxx    2/2     Running   0          1m

# Check Dapr sidecar injection
kubectl describe pod -l app=publisher -n dapr-demo | grep -A5 "Containers:"

# Test health endpoint
kubectl port-forward svc/publisher -n dapr-demo 8080:80 &
curl http://localhost:8080/health

# Check logs for Pub/Sub activity
kubectl logs -l app=publisher -n dapr-demo -c publisher --tail=20
kubectl logs -l app=subscriber -n dapr-demo -c subscriber --tail=20

# View Dapr sidecar logs
kubectl logs -l app=subscriber -n dapr-demo -c daprd --tail=20
```

### 6. Test Pub/Sub Flow

```bash
# Manually trigger publisher
kubectl port-forward svc/publisher -n dapr-demo 8080:80 &
curl -X POST http://localhost:8080/publish \
  -H "Content-Type: application/json" \
  -d '{"order_id": "TEST-001", "amount": 50.00, "customer": "test-user"}'

# Check subscriber received message
kubectl logs -l app=subscriber -n dapr-demo -c subscriber --tail=5

# Verify state was stored
curl http://localhost:8081/state/message%7C%7CTEST-001
```

### 7. Access Monitoring (Optional)

```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Deploy Prometheus
kubectl apply -f deploy/kubernetes/monitoring/prometheus/configmap.yaml
kubectl apply -f deploy/kubernetes/monitoring/prometheus/deployment.yaml
kubectl apply -f deploy/kubernetes/monitoring/prometheus/service.yaml

# Deploy Grafana (set admin password)
kubectl create secret generic grafana-secrets \
  --from-literal=admin-password="admin" \
  -n monitoring
kubectl apply -f deploy/kubernetes/monitoring/grafana/deployment.yaml
kubectl apply -f deploy/kubernetes/monitoring/grafana/service.yaml

# Deploy Fluentd log aggregation
kubectl apply -f deploy/kubernetes/monitoring/fluentd/configmap.yaml
kubectl apply -f deploy/kubernetes/monitoring/fluentd/daemonset.yaml

# Access Grafana
kubectl port-forward svc/grafana -n monitoring 3000:3000 &
# Open http://localhost:3000 (admin/<your-password>)

# Access Prometheus
kubectl port-forward svc/prometheus -n monitoring 9090:9090 &
# Open http://localhost:9090
```

### 8. Enable Secret Store (Optional)

```bash
# AKS: Azure Key Vault
kubectl apply -f deploy/dapr/components/secretstore-keyvault.yaml -n dapr-demo
kubectl apply -f deploy/kubernetes/overlays/aks/patches/secrets-patch.yaml

# GKE: GCP Secret Manager
kubectl apply -f deploy/dapr/components/secretstore-gcp.yaml -n dapr-demo
kubectl apply -f deploy/kubernetes/overlays/gke/patches/secrets-patch.yaml
```

### 9. Test Service Invocation

```bash
# Publisher invokes subscriber health via Dapr
kubectl port-forward svc/publisher -n dapr-demo 8080:80 &
curl http://localhost:8080/invoke-subscriber

# Subscriber invokes publisher health via Dapr
kubectl port-forward svc/subscriber -n dapr-demo 8081:80 &
curl http://localhost:8081/invoke-publisher
```

### 10. Run Comprehensive Validation

```bash
chmod +x scripts/validate.sh
./scripts/validate.sh
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DAPR_APP_ID` | Service identifier | publisher-service / subscriber-service |
| `DAPR_HTTP_PORT` | Dapr sidecar HTTP port | 3500 |
| `APP_PORT` | Application listen port | 5000 |
| `LOG_LEVEL` | Logging verbosity | INFO |
| `PUBSUB_NAME` | Pub/Sub component name | pubsub |
| `STATESTORE_NAME` | State store component name | statestore |
| `TOPIC_NAME` | Pub/Sub topic | orders |

### Switching Pub/Sub Backend

```bash
# Use Kafka instead of Redis
kubectl delete -f deploy/dapr/components/pubsub-redis.yaml -n dapr-demo
kubectl apply -f deploy/dapr/components/pubsub-kafka.yaml -n dapr-demo

# Requires Kafka secrets to be configured first
kubectl create secret generic kafka-secrets \
  --from-literal=brokers="<bootstrap-servers>" \
  --from-literal=username="<api-key>" \
  --from-literal=password="<api-secret>" \
  -n dapr-demo
```

### Switching State Store

```bash
# AKS: Use Cosmos DB
kubectl apply -f deploy/dapr/components/statestore-cosmosdb.yaml -n dapr-demo

# GKE: Use Firestore
kubectl apply -f deploy/dapr/components/statestore-firestore.yaml -n dapr-demo
```

## Troubleshooting

### Pods not starting (0/2 or 1/2)

```bash
# Check events
kubectl describe pod -l app=publisher -n dapr-demo

# Common issues:
# - Dapr not installed: Install Dapr first
# - Missing components: Apply Dapr component YAMLs
# - Image pull error: Check registry access
```

### Pub/Sub not working

```bash
# Check component status
kubectl get components -n dapr-demo

# Check Dapr logs
kubectl logs -l app=publisher -n dapr-demo -c daprd | grep -i error

# Verify subscription
curl http://localhost:3500/v1.0/metadata
```

### State store errors

```bash
# Test state store directly
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test", "value": "hello"}]'

curl http://localhost:3500/v1.0/state/statestore/test
```

## Cleanup

```bash
# Delete application
kubectl delete namespace dapr-demo

# Uninstall Dapr
helm uninstall dapr -n dapr-system
kubectl delete namespace dapr-system

# Delete cluster
# AKS:
az aks delete --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --yes
az group delete --name $RESOURCE_GROUP --yes

# GKE:
gcloud container clusters delete $CLUSTER_NAME --zone $ZONE --quiet
```

## Next Steps

1. **Enable Kafka**: Configure Confluent Cloud credentials for production Pub/Sub
2. **Enable Cloud State Store**: Set up Cosmos DB (AKS) or Firestore (GKE)
3. **Enable Secret Store**: Configure Key Vault or Secret Manager
4. **Set up CI/CD**: Configure GitHub Actions with cloud credentials
5. **Add Monitoring**: Deploy Prometheus/Grafana stack
6. **Enable Network Policies**: Apply security configurations
