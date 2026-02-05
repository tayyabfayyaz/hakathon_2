#!/usr/bin/env bash
set -euo pipefail

# AKS Cluster Setup Script
RESOURCE_GROUP="${RESOURCE_GROUP:-dapr-demo-rg}"
CLUSTER_NAME="${CLUSTER_NAME:-dapr-demo-aks}"
LOCATION="${LOCATION:-eastus}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_VM_SIZE="${NODE_VM_SIZE:-Standard_DS2_v2}"
K8S_VERSION="${K8S_VERSION:-1.27}"
ACR_NAME="${ACR_NAME:-daprdemoregistry}"

echo "=== AKS Cluster Setup ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Cluster:        $CLUSTER_NAME"
echo "Location:       $LOCATION"
echo "Node Count:     $NODE_COUNT"

# Check prerequisites
command -v az >/dev/null 2>&1 || { echo "ERROR: Azure CLI (az) is required"; exit 1; }

# Login check
az account show >/dev/null 2>&1 || { echo "ERROR: Not logged in. Run 'az login' first."; exit 1; }

# Create resource group
echo "Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

# Create ACR
echo "Creating Azure Container Registry..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --output none 2>/dev/null || echo "ACR already exists or name taken."

# Create AKS cluster
echo "Creating AKS cluster (this may take several minutes)..."
az aks create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CLUSTER_NAME" \
  --node-count "$NODE_COUNT" \
  --node-vm-size "$NODE_VM_SIZE" \
  --kubernetes-version "$K8S_VERSION" \
  --enable-managed-identity \
  --attach-acr "$ACR_NAME" \
  --network-plugin azure \
  --generate-ssh-keys \
  --output none

# Get credentials
echo "Fetching cluster credentials..."
az aks get-credentials \
  --resource-group "$RESOURCE_GROUP" \
  --name "$CLUSTER_NAME" \
  --overwrite-existing

# Verify connection
echo "Verifying cluster connection..."
kubectl get nodes

echo ""
echo "=== AKS cluster setup complete ==="
echo "Next: Run './scripts/install-dapr.sh' to install Dapr."
