---
name: deploy-azure
description: Deploy applications to Azure Kubernetes Service (AKS) with Azure Container Registry, Key Vault, Cosmos DB, and Dapr. Use when deploying to Azure, setting up AKS cluster, or managing Azure cloud resources.
argument-hint: "[environment]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob
---

# Azure Kubernetes Service (AKS) Deployment

Deploy applications to AKS with full Azure ecosystem integration.

## Prerequisites

```bash
az version
kubectl version --client
helm version
docker --version
```

## Authentication

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<subscription-id>"

# Verify
az account show --query "{name:name, id:id}" -o table
```

## Infrastructure Setup (First-Time)

```bash
RESOURCE_GROUP="todolist-rg"
LOCATION="eastus"
ACR_NAME="todolistacr"
AKS_NAME="todolist-aks"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Standard

# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 3 \
  --attach-acr $ACR_NAME \
  --enable-managed-identity \
  --generate-ssh-keys
```

## Get Cluster Credentials

```bash
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME
kubectl get nodes
```

## Build and Push Images

```bash
# Login to ACR
az acr login --name $ACR_NAME
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Build and push
docker build -t $ACR_SERVER/todolist-frontend:latest -f frontend/Dockerfile frontend/
docker build -t $ACR_SERVER/todolist-backend:latest -f backend/Dockerfile backend/
docker push $ACR_SERVER/todolist-frontend:latest
docker push $ACR_SERVER/todolist-backend:latest

# Or use ACR Build
az acr build --registry $ACR_NAME --image todolist-frontend:latest frontend/
az acr build --registry $ACR_NAME --image todolist-backend:latest backend/
```

## Deploy Dapr

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Apply Azure-specific components
kubectl apply -f deploy/dapr/components/statestore-cosmosdb.yaml
kubectl apply -f deploy/dapr/components/secretstore-keyvault.yaml
```

## Deploy Application

**Using Kustomize (recommended):**
```bash
kubectl apply -k deploy/kubernetes/overlays/aks
```

**Using Helm:**
```bash
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --create-namespace \
  --set frontend.image.repository=$ACR_SERVER/todolist-frontend \
  --set backend.image.repository=$ACR_SERVER/todolist-backend \
  --wait
```

## Configure Key Vault Secrets

```bash
KEY_VAULT_NAME="todolist-kv"

az keyvault create --resource-group $RESOURCE_GROUP --name $KEY_VAULT_NAME

az keyvault secret set --vault-name $KEY_VAULT_NAME --name "DATABASE-URL" --value "<connection-string>"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "BETTER-AUTH-SECRET" --value "$(openssl rand -base64 32)"
```

## Validation

```bash
kubectl get all -n todolist
kubectl get ingress -n todolist
kubectl logs -f deployment/todolist-frontend -n todolist
```

## Cleanup

```bash
# Remove application
helm uninstall todolist -n todolist

# Remove all Azure resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
