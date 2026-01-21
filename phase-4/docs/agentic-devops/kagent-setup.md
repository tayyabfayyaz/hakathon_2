# Kagent Setup Guide

Kagent is an AI agent framework for Kubernetes operations, featuring a helm-agent for Helm chart management. It provides safety features like dry-run recommendations and operates as a CNCF Sandbox project.

## Prerequisites

- Kubernetes cluster access (Minikube or cloud)
- kubectl configured
- Helm 3.x installed
- Valid OpenAI API key (or compatible endpoint)

## Installation

### Step 1: Install Kagent CRDs

```bash
# Install Custom Resource Definitions
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds
```

### Step 2: Install Kagent Controller

**Demo Profile (Local Development):**
```bash
# Install with demo profile (includes built-in agents)
kagent install --profile demo

# Or via Helm directly
helm install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
  --set profile=demo
```

**Production Profile:**
```bash
kagent install --profile production \
  --set openai.apiKey="$OPENAI_API_KEY"
```

### Step 3: Install Kagent CLI

**Using Homebrew (macOS/Linux):**
```bash
brew tap kagent-dev/tap
brew install kagent
```

**Direct Download:**
```bash
# Check https://github.com/kagent-dev/kagent/releases for latest version
VERSION="v0.1.0"
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
curl -LO "https://github.com/kagent-dev/kagent/releases/download/$VERSION/kagent_${OS}_${ARCH}"
chmod +x kagent_*
sudo mv kagent_* /usr/local/bin/kagent
```

**Windows (PowerShell):**
```powershell
# Download from releases
$version = "v0.1.0"
$url = "https://github.com/kagent-dev/kagent/releases/download/$version/kagent_windows_amd64.exe"
Invoke-WebRequest -Uri $url -OutFile "kagent.exe"
Move-Item kagent.exe $env:USERPROFILE\bin\
```

## Configuration

### API Key Setup

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-your-api-key"

# Or configure via Kagent
kagent config set openai.apiKey "sk-your-api-key"
```

### Verify Installation

```bash
# Check Kagent pods are running
kubectl get pods -n kagent-system

# List available agents
kagent agents list
```

## Helm Agent Usage

The helm-agent specializes in Helm chart operations with safety recommendations.

### List Helm Releases

```bash
kagent invoke -t "List all Helm releases in the default namespace" --agent helm-agent
```

### Validate Helm Chart

```bash
# Validate chart before installation
kagent invoke -t "Validate the Helm chart at ./charts/todolist-pro for best practices" --agent helm-agent
```

### Install Helm Chart

```bash
# Install TodoList Pro
kagent invoke -t "Install the todolist-pro chart from ./charts/todolist-pro with values from values-local.yaml" --agent helm-agent

# With custom values
kagent invoke -t "Install todolist-pro from ./charts/todolist-pro setting frontend.replicaCount to 2" --agent helm-agent
```

### Upgrade Helm Release

```bash
# Upgrade with new values
kagent invoke -t "Upgrade todolist-pro release with values from values-local.yaml" --agent helm-agent

# Scale deployment
kagent invoke -t "Upgrade todolist-pro to have 2 frontend replicas" --agent helm-agent
```

### Rollback Helm Release

```bash
# Rollback to previous revision
kagent invoke -t "Rollback todolist-pro to the previous revision" --agent helm-agent
```

### Check Release Status

```bash
kagent invoke -t "Show the status of the todolist-pro Helm release" --agent helm-agent
```

## Example Session for TodoList Pro

```bash
# 1. Validate the chart
kagent invoke -t "Validate the Helm chart at ./charts/todolist-pro and check for security issues" --agent helm-agent

# 2. Install with secrets
kagent invoke -t "Install todolist-pro from ./charts/todolist-pro with values-local.yaml, setting secrets.databaseUrl to my-db-url and secrets.betterAuthSecret to my-secret" --agent helm-agent

# 3. Check status
kagent invoke -t "Get the status and health of all pods in the todolist-pro release" --agent helm-agent

# 4. Scale if needed
kagent invoke -t "Scale the todolist-pro frontend to 2 replicas using helm upgrade" --agent helm-agent
```

## Safety Features

Kagent helm-agent includes built-in safety features:

1. **Dry-run Recommendations**: Suggests --dry-run for destructive operations
2. **Values Validation**: Checks values against schema if available
3. **Rollback Awareness**: Tracks revision history for safe rollbacks
4. **Secret Handling**: Warns about exposing secrets in logs

## Available Agents

| Agent | Purpose |
|-------|---------|
| helm-agent | Helm chart operations |
| kubectl-agent | General kubectl commands |
| debug-agent | Troubleshooting pods |

## Troubleshooting

### Kagent Not Responding

```bash
# Check controller status
kubectl get pods -n kagent-system
kubectl logs -n kagent-system deploy/kagent-controller

# Restart if needed
kubectl rollout restart deploy/kagent-controller -n kagent-system
```

### API Key Issues

```bash
# Verify key is configured
kagent config get openai.apiKey

# Re-set if needed
kagent config set openai.apiKey "$OPENAI_API_KEY"
```

### Agent Not Found

```bash
# List available agents
kagent agents list

# Refresh agent definitions
kagent agents refresh
```

## References

- [Kagent Documentation](https://kagent.dev/docs)
- [Kagent GitHub Repository](https://github.com/kagent-dev/kagent)
- [CNCF Sandbox Projects](https://www.cncf.io/sandbox-projects/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
