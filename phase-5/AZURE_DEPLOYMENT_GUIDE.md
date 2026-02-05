# TodoList Pro - Azure Kubernetes Service (AKS) Deployment Guide

This guide provides detailed instructions for deploying the TodoList Pro Dapr-based microservices application to Azure Kubernetes Service (AKS).

## Architecture Overview

The application consists of:
- **Publisher Service**: Publishes messages to a Dapr pub/sub component on a schedule
- **Subscriber Service**: Subscribes to messages and stores state using Dapr state management
- **Dapr Runtime**: Provides building blocks for pub/sub, state management, secrets, and service invocation

## Prerequisites

1. Active Azure subscription with appropriate permissions
2. Azure CLI (`az`) installed
3. Kubernetes CLI (`kubectl`) installed
4. Helm 3.x installed
5. Docker installed
6. Dapr CLI installed
7. Git installed

## Step-by-Step Deployment Process

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd phase-5  # Navigate to the project directory
```

### Step 2: Log in to Azure

```bash
az login
# Follow the prompts to authenticate with your Azure account
# Ensure you have an active subscription selected
az account show
```

### Step 3: Create AKS Cluster and ACR

Run the setup script to create the necessary Azure resources:

```bash
# Set environment variables (optional, uses defaults if not set)
export RESOURCE_GROUP="dapr-demo-rg"
export CLUSTER_NAME="dapr-demo-aks"
export LOCATION="eastus"
export NODE_COUNT="3"
export ACR_NAME="daprdemoregistry$(date +%s)"  # Make unique with timestamp

# Run the setup script
./scripts/setup-aks.sh
```

This script will:
- Create a resource group
- Create an Azure Container Registry (ACR)
- Create an AKS cluster with 3 nodes
- Attach ACR to AKS for seamless image pulling
- Get cluster credentials for kubectl

### Step 4: Install Dapr Runtime on AKS

```bash
./scripts/install-dapr.sh
```

This installs Dapr using Helm with the configuration from `deploy/helm/values/dapr-values.yaml`.

Verify the installation:
```bash
dapr status -k
kubectl get pods -n dapr-system
```

### Step 5: Build and Push Application Images to ACR

First, log in to ACR:
```bash
az acr login --name $ACR_NAME
```

Build and tag the images:
```bash
# Get the ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)

# Build the publisher service
docker build -t $ACR_LOGIN_SERVER/publisher-service:latest -f ./publisher/Dockerfile .
docker push $ACR_LOGIN_SERVER/publisher-service:latest

# Build the subscriber service
docker build -t $ACR_LOGIN_SERVER/subscriber-service:latest -f ./subscriber/Dockerfile .
docker push $ACR_LOGIN_SERVER/subscriber-service:latest
```

### Step 6: Update Kubernetes Manifests for ACR Images

Update the deployment files to use your ACR images by modifying:
- `deploy/kubernetes/base/publisher-deployment.yaml`
- `deploy/kubernetes/base/subscriber-deployment.yaml`

Change the image names to use your ACR:
```yaml
# In publisher-deployment.yaml
image: <your-acr-login-server>/publisher-service:latest

# In subscriber-deployment.yaml
image: <your-acr-login-server>/subscriber-service:latest
```

### Step 7: Configure Azure-Specific Dapr Components

The application includes several Dapr component configurations:

- **State Store**: Use `deploy/dapr/components/statestore-cosmosdb.yaml` for Azure Cosmos DB
- **Secret Store**: Use `deploy/dapr/components/secretstore-keyvault.yaml` for Azure Key Vault
- **Pub/Sub**: Use `deploy/dapr/components/pubsub-kafka.yaml` or `pubsub-redis.yaml`

Apply the Azure-specific components:
```bash
kubectl apply -f deploy/dapr/components/statestore-cosmosdb.yaml
kubectl apply -f deploy/dapr/components/secretstore-keyvault.yaml
kubectl apply -f deploy/dapr/components/pubsub-kafka.yaml  # or pubsub-redis.yaml
```

### Step 8: Deploy Application to AKS

```bash
./scripts/deploy.sh --platform aks
```

This will:
- Apply Dapr configuration
- Apply Dapr components
- Deploy the application using AKS-specific Kustomize overlays
- Wait for deployments to be ready

### Step 9: Validate the Deployment

```bash
./scripts/validate.sh
```

Or manually verify:

```bash
# Check pods status
kubectl get pods -n dapr-demo

# Check services
kubectl get svc -n dapr-demo

# Check Dapr sidecars
kubectl describe pods -n dapr-demo

# Check logs
kubectl logs -l app=publisher -n dapr-demo
kubectl logs -l app=subscriber -n dapr-demo
```

### Step 10: Access the Application

The publisher and subscriber services should be accessible within the cluster. For debugging purposes, you can port-forward to access them locally:

```bash
kubectl port-forward -n dapr-demo deployment/subscriber 5000:5000
```

## Configuration Files Overview

### Dapr Components
- `deploy/dapr/config/config.yaml`: Dapr configuration (tracing, metrics, mTLS)
- `deploy/dapr/components/pubsub-kafka.yaml`: Kafka pub/sub component
- `deploy/dapr/components/pubsub-redis.yaml`: Redis pub/sub fallback
- `deploy/dapr/components/statestore-cosmosdb.yaml`: Azure Cosmos DB state store
- `deploy/dapr/components/statestore-redis.yaml`: Redis state store fallback
- `deploy/dapr/components/secretstore-keyvault.yaml`: Azure Key Vault secret store
- `deploy/dapr/components/binding-cron.yaml`: Cron input binding for scheduled publishing

### Kubernetes Deployments
- `deploy/kubernetes/base/`: Base Kubernetes manifests
- `deploy/kubernetes/overlays/aks/`: AKS-specific configurations
- `deploy/kubernetes/overlays/gke/`: GKE-specific configurations

## Troubleshooting

### Common Issues

1. **Image Pull Errors**: Ensure ACR is properly attached to AKS and image names are correctly updated in deployment files.

2. **Dapr Sidecar Injection Failure**: Verify Dapr is properly installed in the cluster and annotations are correctly set in deployment files.

3. **Secret Configuration**: Make sure Azure Key Vault or other secret stores are properly configured with required secrets.

4. **Network Connectivity**: Check if services can communicate with external dependencies (Kafka, Cosmos DB, etc.).

### Useful Commands

```bash
# Check Dapr status
dapr status -k

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n <namespace>

# List Dapr components
kubectl get components.dapr.io -A

# Get Dapr dashboard URL
dapr dashboard -k

# Check if pub/sub is working
kubectl logs -l app=subscriber -n dapr-demo | grep -i "received\|message"
```

## Clean Up

To remove the deployed resources:

```bash
# Delete the application
kubectl delete -k deploy/kubernetes/overlays/aks

# Optionally uninstall Dapr
dapr uninstall -k

# Delete AKS cluster and resources (using Azure CLI)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Additional Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [AKS Documentation](https://docs.microsoft.com/azure/aks/)
- [Azure Container Registry](https://docs.microsoft.com/azure/container-registry/)