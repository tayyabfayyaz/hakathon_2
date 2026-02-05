---
description: Deploy applications to Azure Kubernetes Service (AKS) with ACR, Key Vault, Cosmos DB, and Dapr integration.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# Azure Kubernetes Service (AKS) Deployment Agent

## Core Principle

You are an autonomous Azure deployment agent. Deploy applications to AKS with full Azure ecosystem integration including ACR, Key Vault, Cosmos DB, and Dapr.

---

## Phase 1: Prerequisites

### 1.1 Required Tools

```bash
az version                    # Azure CLI
kubectl version --client      # Kubernetes CLI
helm version                  # Helm
docker --version              # Docker
dapr version                  # Dapr CLI (optional)
```

### 1.2 Azure Authentication

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<subscription-id>"

# Verify subscription
az account show --query "{name:name, id:id}" -o table
```

---

## Phase 2: Infrastructure Setup (First-Time Only)

### 2.1 Create Resource Group

```bash
RESOURCE_GROUP="todolist-rg"
LOCATION="eastus"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 2.2 Create Azure Container Registry

```bash
ACR_NAME="todolistacr"

az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard \
  --admin-enabled true
```

### 2.3 Create AKS Cluster

```bash
AKS_NAME="todolist-aks"

az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 3 \
  --node-vm-size Standard_DS2_v2 \
  --enable-managed-identity \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys \
  --network-plugin azure \
  --kubernetes-version 1.27.3
```

### 2.4 Create Azure Key Vault

```bash
KEY_VAULT_NAME="todolist-kv"

az keyvault create \
  --resource-group $RESOURCE_GROUP \
  --name $KEY_VAULT_NAME \
  --location $LOCATION \
  --enable-rbac-authorization true
```

### 2.5 Create Azure Cosmos DB (Optional)

```bash
COSMOS_ACCOUNT="todolist-cosmos"

az cosmosdb create \
  --resource-group $RESOURCE_GROUP \
  --name $COSMOS_ACCOUNT \
  --kind GlobalDocumentDB \
  --default-consistency-level Session
```

---

## Phase 3: Configure AKS Access

### 3.1 Get AKS Credentials

```bash
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --overwrite-existing
```

### 3.2 Verify Cluster Access

```bash
kubectl cluster-info
kubectl get nodes
```

### 3.3 Configure Workload Identity (Optional)

```bash
# Enable OIDC issuer
az aks update \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --enable-oidc-issuer \
  --enable-workload-identity
```

---

## Phase 4: Build and Push Images

### 4.1 Login to ACR

```bash
az acr login --name $ACR_NAME
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
```

### 4.2 Build and Push Frontend

```bash
# Build
docker build -t $ACR_LOGIN_SERVER/todolist-frontend:latest -f frontend/Dockerfile frontend/

# Push
docker push $ACR_LOGIN_SERVER/todolist-frontend:latest
```

### 4.3 Build and Push Backend

```bash
# Build
docker build -t $ACR_LOGIN_SERVER/todolist-backend:latest -f backend/Dockerfile backend/

# Push
docker push $ACR_LOGIN_SERVER/todolist-backend:latest
```

### 4.4 ACR Build (Alternative - Build in Cloud)

```bash
# Build directly in ACR
az acr build \
  --registry $ACR_NAME \
  --image todolist-frontend:latest \
  --file frontend/Dockerfile \
  frontend/

az acr build \
  --registry $ACR_NAME \
  --image todolist-backend:latest \
  --file backend/Dockerfile \
  backend/
```

---

## Phase 5: Deploy Dapr (If Required)

### 5.1 Install Dapr Runtime

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.mtls.enabled=true \
  --set global.prometheus.enabled=true \
  --wait
```

### 5.2 Verify Dapr Installation

```bash
kubectl get pods -n dapr-system
dapr status -k
```

### 5.3 Deploy Dapr Configuration

```bash
kubectl apply -f deploy/dapr/config/config.yaml
```

### 5.4 Deploy Azure-Specific Dapr Components

```bash
# Apply Azure components
kubectl apply -f deploy/dapr/components/pubsub-kafka.yaml
kubectl apply -f deploy/dapr/components/statestore-cosmosdb.yaml
kubectl apply -f deploy/dapr/components/secretstore-keyvault.yaml
```

---

## Phase 6: Configure Secrets

### 6.1 Add Secrets to Key Vault

```bash
# Database URL
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "DATABASE-URL" \
  --value "postgresql://user:pass@host:5432/db"

# Auth secret
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "BETTER-AUTH-SECRET" \
  --value "$(openssl rand -base64 32)"

# Kafka credentials (if using Kafka)
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "KAFKA-BOOTSTRAP-SERVERS" \
  --value "kafka-broker:9092"
```

### 6.2 Create Kubernetes Secrets (Alternative)

```bash
kubectl create namespace todolist

kubectl create secret generic todolist-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --from-literal=BETTER_AUTH_SECRET="your-secret-key" \
  -n todolist
```

---

## Phase 7: Deploy Application

### 7.1 Using Kustomize (Recommended)

```bash
# Apply AKS overlay
kubectl apply -k deploy/kubernetes/overlays/aks
```

### 7.2 Using Helm

```bash
helm upgrade --install todolist helm/todolist/ \
  --namespace todolist \
  --create-namespace \
  --set frontend.image.repository=$ACR_LOGIN_SERVER/todolist-frontend \
  --set frontend.image.tag=latest \
  --set backend.image.repository=$ACR_LOGIN_SERVER/todolist-backend \
  --set backend.image.tag=latest \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --wait --timeout 10m
```

### 7.3 Wait for Deployment

```bash
kubectl rollout status deployment/todolist-frontend -n todolist --timeout=300s
kubectl rollout status deployment/todolist-backend -n todolist --timeout=300s
```

---

## Phase 8: Configure Ingress (Optional)

### 8.1 Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

### 8.2 Get External IP

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx -w
```

### 8.3 Configure DNS (Optional)

```bash
EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Create DNS record in Azure DNS
az network dns record-set a add-record \
  --resource-group $RESOURCE_GROUP \
  --zone-name example.com \
  --record-set-name todolist \
  --ipv4-address $EXTERNAL_IP
```

---

## Phase 9: Validation

### 9.1 Check Resources

```bash
kubectl get all -n todolist
kubectl get ingress -n todolist
```

### 9.2 Health Checks

```bash
# Get service endpoints
FRONTEND_IP=$(kubectl get svc todolist-frontend -n todolist -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
BACKEND_IP=$(kubectl get svc todolist-backend -n todolist -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Or via ingress
INGRESS_IP=$(kubectl get ingress todolist -n todolist -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl -s http://$INGRESS_IP/
curl -s http://$INGRESS_IP/api/health
```

### 9.3 View Logs

```bash
kubectl logs -f deployment/todolist-frontend -n todolist
kubectl logs -f deployment/todolist-backend -n todolist
```

---

## Phase 10: Monitoring Setup

### 10.1 Enable Azure Monitor for Containers

```bash
az aks enable-addons \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --addons monitoring \
  --workspace-resource-id "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>"
```

### 10.2 Deploy Prometheus/Grafana (Alternative)

```bash
kubectl apply -f deploy/kubernetes/monitoring/prometheus/
kubectl apply -f deploy/kubernetes/monitoring/grafana/
```

---

## CI/CD Integration

### GitHub Actions Trigger

```bash
# Trigger deployment workflow
gh workflow run deploy.yaml -f platform=aks -f environment=production
```

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `ACR_LOGIN_SERVER` | ACR login server URL |

---

## Cleanup

### Remove Application

```bash
helm uninstall todolist -n todolist
kubectl delete namespace todolist
```

### Remove All Azure Resources

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Get credentials | `az aks get-credentials -g $RG -n $AKS` |
| View nodes | `kubectl get nodes` |
| Scale nodes | `az aks scale -g $RG -n $AKS --node-count 5` |
| ACR login | `az acr login --name $ACR` |
| Push image | `docker push $ACR.azurecr.io/image:tag` |
| Dapr status | `dapr status -k` |
| View secrets | `az keyvault secret list --vault-name $KV` |

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).
