---
description: Manage CI/CD pipelines using GitHub Actions for automated build, test, and deployment workflows.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# CI/CD Pipeline Management Agent (GitHub Actions)

## Core Principle

You are an autonomous CI/CD agent. Manage GitHub Actions workflows for automated build, test, and deployment pipelines across multi-cloud environments.

---

## Phase 1: Prerequisites

### 1.1 Required Tools

```bash
gh --version     # GitHub CLI
git --version    # Git
```

### 1.2 GitHub Authentication

```bash
# Check auth status
gh auth status

# Login if needed
gh auth login
```

### 1.3 Verify Repository

```bash
# Check remote
git remote -v

# Get repo info
gh repo view --json name,owner,defaultBranchRef
```

---

## Phase 2: Workflow Discovery

### 2.1 List Available Workflows

```bash
# List all workflows
gh workflow list

# View workflow details
gh workflow view <workflow-name>
```

### 2.2 Project Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| CI Pipeline | `.github/workflows/ci.yaml` | Test, build, push images |
| Deploy Pipeline | `.github/workflows/deploy.yaml` | Deploy to AKS/GKE |

---

## Phase 3: CI Pipeline Operations

### 3.1 Trigger CI Pipeline

```bash
# Trigger on push (automatic)
git push origin main

# Manual trigger
gh workflow run ci.yaml
```

### 3.2 Monitor CI Pipeline

```bash
# List recent runs
gh run list --workflow=ci.yaml

# Watch specific run
gh run watch <run-id>

# View run details
gh run view <run-id>
```

### 3.3 CI Pipeline Stages

1. **Test Stage**
   - Run unit tests with pytest
   - Generate coverage reports
   - Lint code with flake8/eslint

2. **Build Stage**
   - Build Docker images (matrix: publisher, subscriber, frontend, backend)
   - Tag with commit SHA

3. **Push ACR Stage** (on main)
   - Authenticate to Azure Container Registry
   - Push images with proper tags

4. **Push GAR Stage** (on main)
   - Authenticate to Google Artifact Registry
   - Push images with proper tags

---

## Phase 4: Deploy Pipeline Operations

### 4.1 Trigger Deployment

```bash
# Manual trigger with inputs
gh workflow run deploy.yaml \
  -f platform=aks \
  -f environment=staging

# Deploy to both clouds
gh workflow run deploy.yaml \
  -f platform=both \
  -f environment=production
```

### 4.2 Deployment Options

| Parameter | Values | Description |
|-----------|--------|-------------|
| platform | `aks`, `gke`, `both` | Target cloud platform |
| environment | `dev`, `staging`, `production` | Deployment environment |

### 4.3 Monitor Deployment

```bash
# Watch deployment
gh run watch <run-id>

# View logs
gh run view <run-id> --log

# View failed step logs
gh run view <run-id> --log-failed
```

### 4.4 Deployment Stages

1. **Deploy-AKS** (if platform=aks or both)
   - Azure OIDC login
   - Get AKS credentials
   - Install Dapr via Helm
   - Deploy Dapr components (Kafka, Cosmos DB, Key Vault)
   - Deploy application via Kustomize
   - Wait for rollout

2. **Deploy-GKE** (if platform=gke or both)
   - GCP authentication
   - Get GKE credentials
   - Install Dapr via Helm
   - Deploy Dapr components (Kafka, Firestore, Secret Manager)
   - Deploy application via Kustomize
   - Wait for rollout

3. **Smoke-Test** (after successful deploy)
   - Validate deployments
   - Test pub/sub integration
   - Test state store
   - Test service invocation

---

## Phase 5: Configure GitHub Secrets

### 5.1 Required Secrets

```bash
# Azure secrets
gh secret set AZURE_CLIENT_ID --body "<value>"
gh secret set AZURE_TENANT_ID --body "<value>"
gh secret set AZURE_SUBSCRIPTION_ID --body "<value>"
gh secret set ACR_LOGIN_SERVER --body "<acr-name>.azurecr.io"

# GCP secrets
gh secret set GCP_PROJECT_ID --body "<project-id>"
gh secret set GCP_SA_KEY --body "$(cat service-account.json)"
gh secret set GKE_CLUSTER --body "<cluster-name>"
gh secret set GKE_ZONE --body "<zone>"
```

### 5.2 List Configured Secrets

```bash
gh secret list
```

### 5.3 Environment-Specific Secrets

```bash
# Create environment
gh api -X PUT repos/:owner/:repo/environments/production

# Set environment secret
gh secret set DATABASE_URL --env production --body "<value>"
```

---

## Phase 6: Workflow Management

### 6.1 Enable/Disable Workflows

```bash
# Disable workflow
gh workflow disable ci.yaml

# Enable workflow
gh workflow enable ci.yaml
```

### 6.2 Cancel Running Workflow

```bash
# List running workflows
gh run list --status=in_progress

# Cancel specific run
gh run cancel <run-id>
```

### 6.3 Re-run Failed Workflow

```bash
# Re-run all jobs
gh run rerun <run-id>

# Re-run only failed jobs
gh run rerun <run-id> --failed
```

---

## Phase 7: View Artifacts and Logs

### 7.1 Download Artifacts

```bash
# List artifacts
gh run view <run-id> --json artifacts

# Download artifacts
gh run download <run-id>
```

### 7.2 View Logs

```bash
# Full logs
gh run view <run-id> --log

# Specific job logs
gh run view <run-id> --log --job=<job-id>

# Failed jobs only
gh run view <run-id> --log-failed
```

---

## Phase 8: Troubleshooting

### 8.1 Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Auth failure | Expired credentials | Refresh OIDC tokens |
| Image push fails | ACR/GAR permissions | Check service principal roles |
| Deployment timeout | Pod issues | Check kubectl logs |
| Smoke test fails | Service not ready | Increase wait time |

### 8.2 Debug Commands

```bash
# View workflow run details
gh run view <run-id> --json conclusion,status,jobs

# Check failed step
gh run view <run-id> --log-failed

# Check repository permissions
gh api repos/:owner/:repo/actions/permissions
```

### 8.3 Validate Workflow Syntax

```bash
# Check workflow file syntax (requires act tool)
act --list

# Dry run locally
act -n push
```

---

## Phase 9: Create Custom Workflow

### 9.1 Template: Deploy on Tag

```yaml
# .github/workflows/deploy-tag.yaml
name: Deploy on Tag

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get version from tag
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Deploy to production
        run: |
          echo "Deploying version ${{ steps.version.outputs.version }}"
          # Add deployment steps
```

### 9.2 Template: Scheduled Deployment

```yaml
# .github/workflows/scheduled-deploy.yaml
name: Scheduled Deployment

on:
  schedule:
    - cron: '0 2 * * 1-5'  # Weekdays at 2 AM UTC
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: |
          # Add deployment steps
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| List workflows | `gh workflow list` |
| Run workflow | `gh workflow run <name>` |
| List runs | `gh run list` |
| Watch run | `gh run watch <id>` |
| View logs | `gh run view <id> --log` |
| Cancel run | `gh run cancel <id>` |
| Re-run | `gh run rerun <id>` |
| Set secret | `gh secret set <name>` |
| List secrets | `gh secret list` |

---

## Deployment Triggers Summary

| Trigger | CI | Deploy |
|---------|-----|--------|
| Push to main | Auto | Manual |
| Push to develop | Auto | No |
| Pull request | Auto (test only) | No |
| Manual dispatch | Yes | Yes |
| Tag push | Yes | Auto (production) |

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).
