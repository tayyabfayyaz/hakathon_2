---
id: 1
title: Create Dapr K8s Deployment Specification
stage: spec
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 009-dapr-k8s-deployment
branch: 009-dapr-k8s-deployment
user: user
command: /sp.specify
labels: ["dapr", "kubernetes", "aks", "gke", "microservices", "pubsub", "cicd"]
links:
  spec: specs/009-dapr-k8s-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-dapr-k8s-deployment/spec.md
  - specs/009-dapr-k8s-deployment/checklists/requirements.md
tests:
  - Specification quality checklist validation (all items passed)
---

## Prompt

- You are an expert in cloud-native development, Kubernetes, Dapr (Distributed Application Runtime), CI/CD pipelines, and monitoring/logging setups. Your task is to generate a complete, step-by-step guide including all necessary code, YAML configuration files, scripts, and instructions for deploying a sample microservices application using Dapr on both Azure Kubernetes Service (AKS) and Google Kubernetes Engine (GKE). Follow a spec-driven development approach, where the deployment is declarative and driven by specifications (e.g., Kubernetes YAML manifests, Dapr component YAMLs, Helm charts if applicable, and GitHub Actions workflows). This means prioritizing declarative configurations over imperative scripts, and ensuring all resources are defined in version-controlled files that can be applied reproducibly.The application should demonstrate full Dapr capabilities:Pub/Sub: Use Kafka as the broker, hosted on Confluent Cloud or Redpanda Cloud. If Kafka setup poses access issues (e.g., due to API keys or connectivity), fallback to another Dapr-compatible Pub/Sub component like Redis Streams or RabbitMQ.
State Management: Use a state store like Redis or Azure Cosmos DB (for AKS) / Google Cloud Firestore (for GKE).
Bindings: Include a cron binding for scheduled tasks (e.g., a periodic publisher).
Secrets: Use secret stores like Azure Key Vault (for AKS) or Google Secret Manager (for GKE) to manage sensitive data like Kafka credentials.
Service Invocation: Demonstrate inter-service calls between at least two microservices (e.g., a publisher service and a subscriber service).

Additional requirements:Deployment Targets: Provide separate but parallel instructions for AKS and GKE. Assume the user has Azure CLI (az) and Google Cloud CLI (gcloud) installed, along with kubectl and Helm.
CI/CD Pipeline: Set up a GitHub Actions workflow to build Docker images, run tests, and deploy to AKS/GKE. Include secrets management in the workflow (e.g., using GitHub Secrets for cloud credentials).
Monitoring and Logging: Configure Prometheus and Grafana for monitoring, and ELK Stack (Elasticsearch, Logstash, Kibana) or Fluentd with cloud-native logging (e.g., Azure Monitor or Google Cloud Operations) for logging. Integrate Dapr's built-in observability (e.g., metrics endpoint).
Sample Application: Use a simple Node.js or Python-based microservices app (e.g., one service publishes messages on a schedule via cron binding, another subscribes and stores state). Provide the source code for the services.
Best Practices: Ensure high availability, security (e.g., RBAC, network policies), and scalability. Use Helm for Dapr installation if possible. Handle environment-specific differences (e.g., cloud provider managed identities for secrets).
Prerequisites: List all required tools, accounts (e.g., Confluent/Redpanda account, GitHub repo), and setup steps.
Testing and Validation: Include commands to verify the deployment, e.g., checking pods, testing pub/sub flows, viewing logs/metrics.

Output Structure:Overview: High-level architecture diagram in ASCII or Markdown.
Prerequisites: Detailed list.
Application Code: Source code for microservices.
Dapr Configuration YAMLs: For components (pubsub, state, bindings, secrets).
Kubernetes Manifests: Deployments, Services, etc., for AKS and GKE (note differences).
CI/CD Workflow: Full GitHub Actions YAML file.
Monitoring/Logging Setup: YAMLs and instructions.
Deployment Steps: Step-by-step commands for manual deployment, then how to trigger CI/CD.
Cleanup: Instructions to tear down resources.

Ensure the output is comprehensive, error-free, and ready to copy-paste for execution. If any assumptions are made (e.g., region, cluster size), state them clearly and make them configurable.

## Response snapshot

Created comprehensive feature specification for deploying Dapr microservices on AKS and GKE:

- **Branch**: `009-dapr-k8s-deployment`
- **Spec file**: `specs/009-dapr-k8s-deployment/spec.md`
- **8 User Stories** covering: deployment, pub/sub, state management, cron bindings, secrets, service invocation, CI/CD, and monitoring
- **31 Functional Requirements** organized by capability area
- **10 Measurable Success Criteria** with specific metrics
- Documented assumptions, dependencies, and out-of-scope items
- Created quality checklist - all validation items passed

## Outcome

- ✅ Impact: Created spec defining complete Dapr deployment feature for dual-cloud (AKS/GKE)
- 🧪 Tests: Specification quality checklist - all items passed
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: `/sp.clarify` (optional) or `/sp.plan` to design implementation
- 🧠 Reflection: Made informed decisions on language (Python), versions (Dapr 1.12+), and defaults (regions, cluster sizes) to avoid excessive clarification requests

## Evaluation notes (flywheel)

- Failure modes observed: None - spec completed without needing user clarification
- Graders run and results (PASS/FAIL): Quality checklist PASS (all items checked)
- Prompt variant (if applicable): Standard /sp.specify flow
- Next experiment (smallest change to try): N/A - ready for planning phase
