# Feature Specification: Dapr Microservices Deployment on AKS and GKE

**Feature Branch**: `009-dapr-k8s-deployment`
**Created**: 2026-02-03
**Status**: Draft
**Input**: User description: "Deploy a sample microservices application using Dapr on both Azure Kubernetes Service (AKS) and Google Kubernetes Engine (GKE) with full Dapr capabilities including Pub/Sub, State Management, Bindings, Secrets, and Service Invocation. Include CI/CD pipeline, monitoring, and logging."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Dapr-enabled Microservices to Kubernetes (Priority: P1)

As a DevOps engineer, I want to deploy a sample microservices application with Dapr sidecars to either AKS or GKE so that I can leverage Dapr's building blocks for distributed systems without vendor lock-in.

**Why this priority**: This is the core functionality - without successful deployment, no other features can be demonstrated or tested.

**Independent Test**: Can be fully tested by running `kubectl get pods` and verifying all application pods are running with Dapr sidecars injected, delivering a functional microservices environment.

**Acceptance Scenarios**:

1. **Given** a configured Kubernetes cluster (AKS or GKE), **When** I apply the deployment manifests, **Then** all microservice pods start successfully with Dapr sidecars (2/2 containers running)
2. **Given** Dapr is installed on the cluster, **When** I run `dapr status -k`, **Then** all Dapr system components show "Running" status
3. **Given** deployed services, **When** I check service health endpoints, **Then** each service responds with HTTP 200

---

### User Story 2 - Inter-Service Communication via Pub/Sub (Priority: P1)

As a developer, I want the publisher service to send messages via Dapr Pub/Sub to Kafka, and the subscriber service to receive and process them so that services communicate asynchronously without direct coupling.

**Why this priority**: Pub/Sub is the primary communication pattern demonstrating Dapr's value proposition.

**Independent Test**: Can be tested by triggering the publisher and verifying messages appear in subscriber logs, delivering asynchronous messaging capability.

**Acceptance Scenarios**:

1. **Given** the cron binding triggers, **When** the publisher service runs, **Then** a message is published to the configured Kafka topic via Dapr
2. **Given** a message is published, **When** the subscriber receives it, **Then** it processes the message and stores state successfully
3. **Given** Kafka is unavailable, **When** the system falls back to Redis Pub/Sub, **Then** message delivery continues without application code changes

---

### User Story 3 - State Management Across Services (Priority: P2)

As a developer, I want services to persist and retrieve state using Dapr's state store abstraction so that I can swap underlying storage providers without code changes.

**Why this priority**: State management demonstrates Dapr's portability across cloud providers (Cosmos DB on Azure, Firestore on GCP).

**Independent Test**: Can be tested by calling state store APIs and verifying data persistence, delivering stateful application capability.

**Acceptance Scenarios**:

1. **Given** a running subscriber service, **When** it receives a message, **Then** it saves the processed data to the configured state store
2. **Given** stored state, **When** a service queries for state by key, **Then** it retrieves the correct value
3. **Given** AKS deployment, **When** using Azure Cosmos DB as state store, **Then** data persists correctly
4. **Given** GKE deployment, **When** using Google Cloud Firestore as state store, **Then** data persists correctly

---

### User Story 4 - Scheduled Tasks via Cron Binding (Priority: P2)

As a developer, I want the publisher service to automatically publish messages on a schedule using Dapr input bindings so that periodic tasks run without external cron jobs.

**Why this priority**: Demonstrates Dapr bindings, a key building block for integrating external systems.

**Independent Test**: Can be tested by observing scheduled messages in logs at expected intervals.

**Acceptance Scenarios**:

1. **Given** a configured cron binding (every 30 seconds), **When** the scheduled time arrives, **Then** the publisher service receives a trigger and publishes a message
2. **Given** the cron binding is active, **When** I check application logs, **Then** I see regular invocations at the configured interval

---

### User Story 5 - Secrets Management via Cloud Providers (Priority: P2)

As a DevOps engineer, I want Dapr to retrieve secrets (like Kafka credentials) from cloud-native secret stores so that sensitive data is managed securely without hardcoding.

**Why this priority**: Security is essential for production deployments; this shows Dapr's secret store integration.

**Independent Test**: Can be tested by verifying services start correctly using secrets from Key Vault (Azure) or Secret Manager (GCP).

**Acceptance Scenarios**:

1. **Given** AKS deployment, **When** services request secrets, **Then** Dapr retrieves them from Azure Key Vault
2. **Given** GKE deployment, **When** services request secrets, **Then** Dapr retrieves them from Google Secret Manager
3. **Given** a secret is rotated in the secret store, **When** the service restarts, **Then** it uses the updated secret value

---

### User Story 6 - Direct Service Invocation (Priority: P2)

As a developer, I want services to call each other directly using Dapr service invocation so that I get built-in service discovery, retries, and mTLS.

**Why this priority**: Service invocation demonstrates Dapr's service mesh capabilities.

**Independent Test**: Can be tested by calling one service's endpoint that internally calls another service via Dapr.

**Acceptance Scenarios**:

1. **Given** both services are running, **When** the subscriber calls the publisher's health endpoint via Dapr, **Then** it receives a successful response
2. **Given** a target service is temporarily unavailable, **When** an invocation is made, **Then** Dapr retries the request according to configured policy

---

### User Story 7 - CI/CD Pipeline for Automated Deployment (Priority: P3)

As a DevOps engineer, I want a GitHub Actions workflow that builds, tests, and deploys the application to AKS or GKE so that deployments are automated and repeatable.

**Why this priority**: Automation is important but the system works without it during initial setup.

**Independent Test**: Can be tested by pushing code and verifying automatic deployment completes successfully.

**Acceptance Scenarios**:

1. **Given** code is pushed to the main branch, **When** GitHub Actions workflow runs, **Then** Docker images are built and pushed to the container registry
2. **Given** images are built, **When** deployment step runs, **Then** Kubernetes manifests are applied to the target cluster
3. **Given** workflow requires cloud credentials, **When** I configure GitHub Secrets, **Then** the workflow authenticates successfully to AKS/GKE

---

### User Story 8 - Monitoring and Observability (Priority: P3)

As an operations engineer, I want to view metrics in Grafana and logs in a centralized logging system so that I can monitor application health and troubleshoot issues.

**Why this priority**: Observability is critical for production but can be added after core functionality works.

**Independent Test**: Can be tested by viewing Dapr metrics dashboards and searching application logs.

**Acceptance Scenarios**:

1. **Given** Prometheus and Grafana are deployed, **When** I access Grafana dashboards, **Then** I see Dapr sidecar metrics (request latency, throughput, errors)
2. **Given** Fluentd/logging is configured, **When** services emit logs, **Then** logs are aggregated and searchable in the logging backend
3. **Given** Dapr observability is enabled, **When** I access /metrics endpoint, **Then** Prometheus-format metrics are exposed

---

### Edge Cases

- What happens when Kafka is unreachable at startup? → System falls back to Redis Pub/Sub or enters retry mode with exponential backoff
- What happens when state store is temporarily unavailable? → Dapr returns errors to the application; application implements appropriate retry logic
- What happens when a secret doesn't exist in the secret store? → Service fails to start with clear error message in logs
- What happens when the cron binding fires but the publisher service is not ready? → Message is dropped; next scheduled invocation proceeds normally
- What happens when deploying to a cluster without Dapr installed? → Pods remain in pending state; clear error in events indicating missing Dapr sidecar injector

## Requirements *(mandatory)*

### Functional Requirements

**Core Deployment**
- **FR-001**: System MUST deploy at least two microservices (publisher and subscriber) to Kubernetes with Dapr sidecar injection
- **FR-002**: System MUST support deployment to both AKS and GKE using platform-specific configurations
- **FR-003**: System MUST install Dapr runtime on the cluster using Helm charts

**Pub/Sub Messaging**
- **FR-004**: Publisher service MUST publish messages to a Dapr Pub/Sub component
- **FR-005**: Subscriber service MUST subscribe to topics and process incoming messages
- **FR-006**: System MUST configure Kafka (Confluent Cloud or Redpanda Cloud) as the primary Pub/Sub broker
- **FR-007**: System MUST provide Redis Streams as a fallback Pub/Sub option if Kafka is unavailable

**State Management**
- **FR-008**: Subscriber service MUST store processed message state using Dapr state store API
- **FR-009**: System MUST configure Azure Cosmos DB as state store for AKS deployments
- **FR-010**: System MUST configure Google Cloud Firestore as state store for GKE deployments
- **FR-011**: System MUST provide Redis as a fallback state store option

**Bindings**
- **FR-012**: System MUST configure a Dapr cron input binding to trigger the publisher service periodically
- **FR-013**: Cron binding MUST be configurable with schedule expression (default: every 30 seconds)

**Secrets**
- **FR-014**: System MUST retrieve sensitive credentials from Azure Key Vault for AKS deployments
- **FR-015**: System MUST retrieve sensitive credentials from Google Secret Manager for GKE deployments
- **FR-016**: System MUST NOT hardcode any secrets in configuration files or source code

**Service Invocation**
- **FR-017**: Services MUST be able to invoke each other using Dapr service invocation
- **FR-018**: System MUST demonstrate at least one inter-service call between publisher and subscriber

**CI/CD**
- **FR-019**: System MUST include a GitHub Actions workflow for automated builds and deployments
- **FR-020**: Workflow MUST build Docker images for both microservices
- **FR-021**: Workflow MUST push images to a container registry (ACR for Azure, GCR/Artifact Registry for GCP)
- **FR-022**: Workflow MUST apply Kubernetes manifests to deploy the application
- **FR-023**: Workflow MUST use GitHub Secrets for cloud provider credentials

**Monitoring and Logging**
- **FR-024**: System MUST deploy Prometheus for metrics collection
- **FR-025**: System MUST deploy Grafana with pre-configured Dapr dashboards
- **FR-026**: System MUST configure log aggregation (Fluentd with cloud-native logging or ELK stack)
- **FR-027**: System MUST expose Dapr metrics endpoints for observability

**Security and Best Practices**
- **FR-028**: System MUST configure Kubernetes RBAC for Dapr components
- **FR-029**: System MUST apply network policies to restrict pod-to-pod communication
- **FR-030**: Deployments MUST include resource requests and limits for high availability
- **FR-031**: System MUST support horizontal pod autoscaling configuration

### Key Entities

- **Publisher Service**: Microservice that publishes messages on schedule; receives cron binding triggers; publishes to Pub/Sub topic
- **Subscriber Service**: Microservice that consumes messages; subscribes to Pub/Sub topic; stores state; exposes health endpoint
- **Dapr Sidecar**: Injected container providing Dapr building blocks to each service
- **Pub/Sub Component**: Dapr component configuration for message broker (Kafka or Redis)
- **State Store Component**: Dapr component configuration for state persistence (Cosmos DB, Firestore, or Redis)
- **Secret Store Component**: Dapr component configuration for secret retrieval (Key Vault or Secret Manager)
- **Cron Binding**: Dapr input binding that triggers publisher on schedule

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All pods reach Running state within 5 minutes of deployment on a healthy cluster
- **SC-002**: Pub/Sub messages are delivered from publisher to subscriber within 5 seconds of publication
- **SC-003**: State store operations (save and retrieve) complete within 2 seconds
- **SC-004**: Cron binding triggers publisher at the configured interval (±5 seconds tolerance)
- **SC-005**: CI/CD pipeline completes full build and deployment in under 15 minutes
- **SC-006**: Grafana dashboards display Dapr metrics within 2 minutes of deployment
- **SC-007**: Application logs are searchable in the logging backend within 1 minute of emission
- **SC-008**: Service invocation calls succeed with 99% reliability when both services are healthy
- **SC-009**: System supports at least 100 messages per minute throughput
- **SC-010**: Zero secrets exposed in plain text in any configuration files or logs

## Assumptions

- User has active Azure and/or GCP accounts with appropriate permissions
- User has Azure CLI (`az`), Google Cloud CLI (`gcloud`), `kubectl`, and `helm` installed
- User has a GitHub account and repository for CI/CD
- Confluent Cloud or Redpanda Cloud account is available for Kafka (with fallback to Redis if not)
- Default cluster configuration: 3 nodes, 2 vCPU, 8GB RAM each (configurable)
- Default region: East US (Azure) / us-central1 (GCP) (configurable)
- Dapr version: 1.12+ (latest stable)
- Kubernetes version: 1.27+ (managed service default)
- Sample application uses Python (simple, widely understood)

## Out of Scope

- Multi-cluster federation or cross-cloud deployment
- Custom domain and TLS certificate management
- Advanced Dapr features: Actors, Workflows, Configuration API
- Production-grade data backup and disaster recovery
- Cost optimization strategies
- Performance tuning beyond basic resource configuration
- Service mesh integration (Istio, Linkerd) beyond Dapr's built-in mTLS

## Dependencies

- Azure Kubernetes Service (AKS) or Google Kubernetes Engine (GKE)
- Dapr runtime and CLI
- Kafka (Confluent Cloud/Redpanda Cloud) or Redis for Pub/Sub
- Azure Cosmos DB / Google Cloud Firestore or Redis for state
- Azure Key Vault / Google Secret Manager for secrets
- Container registry (ACR/GCR/Artifact Registry)
- GitHub Actions for CI/CD
- Prometheus and Grafana for monitoring
- Fluentd or ELK stack for logging
