# kubectl-ai Setup Guide

kubectl-ai is a kubectl plugin that uses AI to generate Kubernetes manifests from natural language descriptions. This guide covers installation, configuration, and usage for TodoList Pro deployment.

## Prerequisites

- kubectl installed and configured
- Valid OpenAI API key (or compatible endpoint)
- Kubernetes cluster access

## Installation

### Option A: Using Krew (Recommended)

```powershell
# Install Krew first if not already installed
# See: https://krew.sigs.k8s.io/docs/user-guide/setup/install/

# Install kubectl-ai via Krew
kubectl krew install ai
```

### Option B: Direct Binary Download

**Windows (PowerShell):**
```powershell
# Download latest release
$version = "v0.0.12"  # Check https://github.com/sozercan/kubectl-ai/releases for latest
$url = "https://github.com/sozercan/kubectl-ai/releases/download/$version/kubectl-ai_windows_amd64.exe"
Invoke-WebRequest -Uri $url -OutFile "kubectl-ai.exe"

# Move to a directory in PATH or kubectl plugins directory
Move-Item kubectl-ai.exe $env:USERPROFILE\.krew\bin\
```

**Linux/macOS:**
```bash
# Download and install
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai_$(uname -s)_$(uname -m)
chmod +x kubectl-ai_*
sudo mv kubectl-ai_* /usr/local/bin/kubectl-ai
```

## Configuration

### API Key Setup

kubectl-ai supports OpenAI API and compatible endpoints (Azure OpenAI, local models with OpenAI-compatible API).

**Environment Variables:**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key"
$env:OPENAI_DEPLOYMENT_NAME = "gpt-4"  # Model name

# Or for Azure OpenAI
$env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com"
$env:OPENAI_API_KEY = "your-azure-key"
```

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-api-key"
export OPENAI_DEPLOYMENT_NAME="gpt-4"
```

### Using with Gemini (via LiteLLM proxy)

If using Google Gemini instead of OpenAI:

```bash
# Run LiteLLM proxy
pip install litellm
export GEMINI_API_KEY="your-gemini-key"
litellm --model gemini/gemini-1.5-pro --port 8000

# Point kubectl-ai to proxy
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="dummy"  # Not used but required
```

## Usage for TodoList Pro

### Generate Deployment Manifests

```bash
# Generate backend deployment
kubectl ai "create a kubernetes deployment named todolist-backend with image todolist-backend:local, 1 replica, port 8000, memory limit 512Mi, cpu limit 500m, liveness probe on /health with 10s initial delay"

# Generate frontend deployment
kubectl ai "create a kubernetes deployment named todolist-frontend with image todolist-frontend:local, 1 replica, port 3000, memory limit 512Mi, cpu limit 500m, liveness probe on / with 30s initial delay"
```

### Generate Service Manifests

```bash
# Backend ClusterIP service
kubectl ai "create a ClusterIP service named todolist-backend for deployment todolist-backend on port 8000"

# Frontend NodePort service
kubectl ai "create a NodePort service named todolist-frontend for deployment todolist-frontend on port 3000"
```

### Generate ConfigMap

```bash
# Create ConfigMap from key-value pairs
kubectl ai "create a configmap named backend-config with keys API_VERSION=v1 DEBUG=false PORT=8000"
```

### Validate Generated Manifests

Always validate AI-generated manifests before applying:

```bash
# Dry-run validation
kubectl ai "create deployment for fastapi backend" | kubectl apply --dry-run=client -f -

# Or save and review
kubectl ai "create deployment for fastapi backend" > deployment.yaml
kubectl apply --dry-run=client -f deployment.yaml
```

## Example Session

```bash
# Generate and apply backend deployment
kubectl ai "create a kubernetes deployment named todolist-pro-backend \
  with image todolist-backend:local, \
  1 replica, \
  port 8000, \
  memory limit 512Mi, \
  cpu limit 500m, \
  liveness probe on /health with 10s initial delay, \
  readiness probe on /health with 5s initial delay, \
  environment variable PORT=8000" | kubectl apply --dry-run=client -f -

# Output will show deployment manifest and validation result
```

## Best Practices

1. **Always use --dry-run first**: Validate manifests before applying
2. **Review resource limits**: AI may suggest inappropriate values
3. **Check probe configurations**: Ensure paths and delays match your application
4. **Verify image names**: Ensure image references match your registry
5. **Add labels manually if needed**: AI may not include all required labels

## Troubleshooting

### API Key Issues
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test with simple prompt
kubectl ai "create a basic nginx deployment"
```

### Connection Issues
```bash
# Check API endpoint
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### Invalid Manifests
If kubectl-ai generates invalid YAML:
- Use more specific prompts
- Include version numbers (e.g., "kubernetes deployment v1")
- Specify exact field names

## References

- [kubectl-ai GitHub Repository](https://github.com/sozercan/kubectl-ai)
- [Krew kubectl Plugin Manager](https://krew.sigs.k8s.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
