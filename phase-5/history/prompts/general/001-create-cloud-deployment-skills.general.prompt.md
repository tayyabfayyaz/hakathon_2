---
id: 001
title: Create Cloud Deployment Skills
stage: general
date: 2026-02-05
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 009-dapr-k8s-deployment
user: user
command: general
labels: ["deployment", "skills", "kubernetes", "docker", "helm", "azure", "gcp", "dapr", "cicd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/commands/sp.deploy.md
  - .claude/commands/sp.deploy.local.md
  - .claude/commands/sp.deploy.azure.md
  - .claude/commands/sp.deploy.gcp.md
  - .claude/commands/sp.deploy.monitor.md
  - .claude/commands/sp.deploy.cicd.md
  - .claude/skills/deploy/SKILL.md
  - .claude/skills/deploy/scripts/validate-deployment.sh
  - .claude/skills/deploy/scripts/detect-context.sh
  - .claude/skills/deploy/scripts/quick-deploy.sh
  - .claude/skills/deploy-local/SKILL.md
  - .claude/skills/deploy-azure/SKILL.md
  - .claude/skills/deploy-gcp/SKILL.md
  - .claude/skills/deploy-monitor/SKILL.md
  - .claude/skills/deploy-cicd/SKILL.md
tests:
  - none
---

## Prompt

You analyze the deployment stretegy and then read the code base of deployment then you create a skill of cloud deployment. That use docker, kubernetes, helm, Azure, more tools use in this project deployment.

## Response snapshot

Analyzed the entire deployment codebase and created a comprehensive suite of cloud deployment artifacts:

### Commands (`.claude/commands/`) - Slash commands invoked with `/sp.deploy.*`

1. **sp.deploy** - Main autonomous cloud deployment agent
2. **sp.deploy.local** - Local Minikube deployment
3. **sp.deploy.azure** - Azure AKS deployment
4. **sp.deploy.gcp** - Google GKE deployment
5. **sp.deploy.monitor** - Monitoring stack deployment
6. **sp.deploy.cicd** - CI/CD pipeline management

### Skills (`.claude/skills/`) - Auto-invoked by Claude based on context

1. **deploy/** - Main deployment skill with supporting scripts
   - `SKILL.md` - Core deployment instructions
   - `scripts/validate-deployment.sh` - Deployment validation
   - `scripts/detect-context.sh` - Platform auto-detection
   - `scripts/quick-deploy.sh` - Quick deployment helper
2. **deploy-local/** - Local Minikube deployment
3. **deploy-azure/** - Azure AKS deployment
4. **deploy-gcp/** - Google GKE deployment
5. **deploy-monitor/** - Prometheus/Grafana/Fluentd stack
6. **deploy-cicd/** - GitHub Actions management

Key technologies covered:
- Docker (containerization with multi-stage builds)
- Kubernetes (AKS, GKE, Minikube)
- Helm (package management)
- Kustomize (overlay management)
- Dapr (distributed application runtime)
- Azure (ACR, Key Vault, Cosmos DB)
- GCP (Artifact Registry, Secret Manager, Firestore)
- GitHub Actions (CI/CD)
- Prometheus/Grafana (monitoring)
- Fluentd (log aggregation)

## Outcome

- ✅ Impact: Created 6 comprehensive deployment skills covering local, Azure, GCP, monitoring, and CI/CD workflows
- 🧪 Tests: N/A (skill documentation)
- 📁 Files: 6 skill files created in .claude/commands/
- 🔁 Next prompts: Test skills with actual deployments, add more cloud providers if needed
- 🧠 Reflection: Comprehensive analysis of existing deployment infrastructure enabled creation of well-structured, autonomous deployment agents

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add support for AWS EKS deployment
