---
name: deploy-cicd
description: Manage CI/CD pipelines using GitHub Actions for automated build, test, and deployment. Use when triggering deployments, checking pipeline status, viewing workflow runs, or managing GitHub Actions.
argument-hint: "[action] [workflow]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob
---

# CI/CD Pipeline Management (GitHub Actions)

Manage GitHub Actions workflows for automated build, test, and deployment.

## Prerequisites

```bash
gh --version
gh auth status
```

## Workflows

| Workflow | File | Triggers |
|----------|------|----------|
| CI | `.github/workflows/ci.yaml` | Push, PR |
| Deploy | `.github/workflows/deploy.yaml` | Manual, CI completion |

## Trigger Workflows

**CI Pipeline:**
```bash
# Manual trigger
gh workflow run ci.yaml

# Automatic on push
git push origin main
```

**Deploy Pipeline:**
```bash
# Deploy to specific platform
gh workflow run deploy.yaml -f platform=aks -f environment=staging

# Deploy to both clouds
gh workflow run deploy.yaml -f platform=both -f environment=production
```

**Deployment Options:**
- `platform`: `aks`, `gke`, `both`
- `environment`: `dev`, `staging`, `production`

## Monitor Workflows

```bash
# List recent runs
gh run list

# Watch specific run
gh run watch <run-id>

# View run details
gh run view <run-id>

# View logs
gh run view <run-id> --log

# View failed step logs
gh run view <run-id> --log-failed
```

## Manage Secrets

```bash
# List secrets
gh secret list

# Set Azure secrets
gh secret set AZURE_CLIENT_ID --body "<value>"
gh secret set AZURE_TENANT_ID --body "<value>"
gh secret set AZURE_SUBSCRIPTION_ID --body "<value>"
gh secret set ACR_LOGIN_SERVER --body "<acr>.azurecr.io"

# Set GCP secrets
gh secret set GCP_PROJECT_ID --body "<project-id>"
gh secret set GCP_SA_KEY --body "$(cat service-account.json)"
gh secret set GKE_CLUSTER --body "<cluster-name>"
gh secret set GKE_ZONE --body "<zone>"
```

## Workflow Control

```bash
# Cancel running workflow
gh run cancel <run-id>

# Re-run failed jobs
gh run rerun <run-id> --failed

# Re-run all jobs
gh run rerun <run-id>

# Disable workflow
gh workflow disable ci.yaml

# Enable workflow
gh workflow enable ci.yaml
```

## Download Artifacts

```bash
# List artifacts
gh run view <run-id> --json artifacts

# Download
gh run download <run-id>
```

## Quick Reference

| Action | Command |
|--------|---------|
| List workflows | `gh workflow list` |
| Run workflow | `gh workflow run <name>` |
| List runs | `gh run list` |
| Watch run | `gh run watch <id>` |
| View logs | `gh run view <id> --log` |
| Cancel | `gh run cancel <id>` |
| Re-run | `gh run rerun <id>` |

## CI Pipeline Stages

1. **Test**: Unit tests, linting
2. **Build**: Docker images (matrix build)
3. **Push-ACR**: Push to Azure Container Registry
4. **Push-GAR**: Push to Google Artifact Registry

## Deploy Pipeline Stages

1. **Deploy-AKS**: Azure deployment with Dapr
2. **Deploy-GKE**: GCP deployment with Dapr
3. **Smoke-Test**: Validation tests
