# Feature Specification: Kubernetes Local Deployment with Agentic DevOps

**Feature Branch**: `006-k8s-minikube-deploy`
**Created**: 2026-01-19
**Status**: Draft
**Input**: User description: "Deploy phase-4 in the local kubernetes cluster using Minikube and Helm Charts following fully Agentic DevOps approach with separate frontend/backend containers, AI-assisted DevOps tools (kubectl-ai, Kagent, Docker Gordon)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Deploys Application Locally (Priority: P1)

As a developer, I want to deploy the TodoList Pro application to my local Minikube cluster using a single command, so that I can test the full production-like environment on my machine without cloud dependencies.

**Why this priority**: This is the core functionality - without successful local deployment, no other features matter. Developers need a reliable way to spin up the entire application stack locally for testing and development.

**Independent Test**: Can be fully tested by running the Helm install command and verifying both frontend and backend pods are running, accessible via browser, and can create/manage tasks.

**Acceptance Scenarios**:

1. **Given** Minikube is running and kubectl is configured, **When** developer runs `helm install todolist-pro ./charts/todolist-pro`, **Then** both frontend and backend deployments are created and reach "Running" state within 3 minutes
2. **Given** application is deployed, **When** developer accesses the frontend URL via Minikube service, **Then** the landing page loads successfully and login/register forms are functional
3. **Given** application is deployed with valid environment secrets, **When** developer creates a task through the UI, **Then** the task persists and appears in the task list after page refresh

---

### User Story 2 - AI-Assisted Helm Chart Generation (Priority: P2)

As a DevOps engineer, I want to use AI-assisted tools (kubectl-ai or Kagent) to generate and validate Helm charts, so that I can leverage AI to create production-quality Kubernetes manifests with best practices built-in.

**Why this priority**: This enables the Agentic DevOps workflow - the AI-generated charts should follow Kubernetes best practices, reducing manual configuration errors and learning curve.

**Independent Test**: Can be tested by running the AI tool to generate charts, then validating the output with `helm lint` and `kubectl --dry-run` to ensure syntactically correct and deployable manifests.

**Acceptance Scenarios**:

1. **Given** kubectl-ai or Kagent is installed and configured, **When** user requests Helm chart generation for the frontend service, **Then** a valid Helm chart is created with Deployment, Service, ConfigMap, and optionally Ingress resources
2. **Given** AI-generated Helm charts exist, **When** user runs `helm lint ./charts/frontend`, **Then** no errors are reported and only minor warnings (if any) are displayed
3. **Given** AI tool is available, **When** user requests chart modifications (e.g., "add resource limits"), **Then** the tool updates the chart appropriately with reasonable default values

---

### User Story 3 - Docker Image Build with AI Assistance (Priority: P3)

As a developer, I want to build optimized Docker images for frontend and backend using Docker AI (Gordon) assistance, so that I can create production-ready container images with security and performance best practices.

**Why this priority**: Having optimized Docker images is essential for efficient resource utilization and security, but the deployment can work with basic Dockerfiles initially.

**Independent Test**: Can be tested by building both images locally, scanning them for vulnerabilities, and verifying they run correctly as standalone containers before Kubernetes deployment.

**Acceptance Scenarios**:

1. **Given** Docker Desktop with Gordon AI is available, **When** developer requests help optimizing the frontend Dockerfile, **Then** Gordon provides suggestions for multi-stage builds, layer caching, and security hardening
2. **Given** Dockerfile exists for backend, **When** developer builds the image with `docker build`, **Then** the resulting image is under 500MB (slim Python base) and runs successfully with health checks passing
3. **Given** both images are built, **When** pushed to local registry or loaded into Minikube, **Then** Kubernetes can pull and run them without authentication errors

---

### User Story 4 - Environment Configuration Management (Priority: P2)

As a developer, I want to manage environment-specific configurations (database URL, API keys, CORS origins) through Helm values files, so that I can easily switch between local development and testing configurations without modifying code.

**Why this priority**: Proper configuration management is critical for security (no hardcoded secrets) and flexibility (easy environment switching).

**Independent Test**: Can be tested by deploying with different values files and verifying the application connects to the specified database and uses the correct API keys.

**Acceptance Scenarios**:

1. **Given** a `values-local.yaml` file exists, **When** deploying with `helm install -f values-local.yaml`, **Then** the application uses the specified external Neon database URL
2. **Given** sensitive values (API keys, database credentials) are in Kubernetes Secrets, **When** inspecting pod environment variables, **Then** secrets are not visible in plain text in ConfigMaps or deployment manifests
3. **Given** CORS_ORIGINS is configured in values, **When** frontend makes API calls to backend, **Then** CORS headers allow the configured origins

---

### User Story 5 - Health Monitoring and Service Discovery (Priority: P3)

As an operator, I want to verify that all services are healthy and properly connected through Kubernetes health checks and service discovery, so that I can ensure the application is production-ready.

**Why this priority**: Health monitoring ensures reliability but is a secondary concern after basic deployment works.

**Independent Test**: Can be tested by checking pod readiness, running health endpoints, and verifying inter-service communication via Kubernetes DNS.

**Acceptance Scenarios**:

1. **Given** pods are deployed with health probes, **When** checking pod status with `kubectl get pods`, **Then** all pods show READY state (e.g., 1/1) within 2 minutes of deployment
2. **Given** backend exposes /health endpoint, **When** Kubernetes liveness probe checks the endpoint, **Then** probe succeeds and pod remains running
3. **Given** frontend needs to call backend, **When** using Kubernetes service DNS (e.g., `backend-service.default.svc.cluster.local`), **Then** requests route correctly to backend pods

---

### Edge Cases

- What happens when Minikube runs out of resources (CPU/memory)?
  - Pods should show "Pending" state with resource constraint events visible via `kubectl describe pod`
- How does the system handle database connection failures (Neon unavailable)?
  - Backend should return 503 Service Unavailable on health checks, pods should restart based on liveness probe failures
- What happens when GEMINI_API_KEY is missing or invalid?
  - Chat functionality gracefully degrades with user-friendly error message; core task management continues working
- How does the system behave during rolling updates?
  - New pods should start before old pods terminate (rolling update strategy); no downtime for users

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy frontend as a separate container running Next.js application on port 3000
- **FR-002**: System MUST deploy backend as a separate container running FastAPI application on port 8000
- **FR-003**: System MUST use Helm Charts as the package manager for Kubernetes deployments
- **FR-004**: System MUST support configuration through Helm values files without code changes
- **FR-005**: System MUST store sensitive configuration (DATABASE_URL, GEMINI_API_KEY, BETTER_AUTH_SECRET) in Kubernetes Secrets
- **FR-006**: System MUST expose frontend service via Minikube NodePort or Ingress for browser access
- **FR-007**: System MUST enable backend-to-database connectivity to external Neon PostgreSQL service
- **FR-008**: System MUST include health check probes (liveness and readiness) for both frontend and backend deployments
- **FR-009**: System MUST provide installation scripts/documentation for AI-DevOps tools (kubectl-ai, Kagent)
- **FR-010**: System MUST include Docker AI (Gordon) integration guidance for Dockerfile optimization
- **FR-011**: System MUST support `helm upgrade` for updating deployments without full reinstallation
- **FR-012**: System MUST include resource requests and limits for all containers to prevent resource starvation

### Key Entities

- **Helm Chart (todolist-pro)**: Parent chart containing frontend and backend as subcharts, manages shared configurations and secrets
- **Frontend Deployment**: Kubernetes Deployment for Next.js container, includes ConfigMap for public environment variables
- **Backend Deployment**: Kubernetes Deployment for FastAPI container, references Secrets for sensitive configuration
- **Services**: ClusterIP services for internal communication, NodePort for external frontend access
- **Secrets**: Kubernetes Secret resources storing DATABASE_URL, GEMINI_API_KEY, BETTER_AUTH_SECRET, CORS_ORIGINS
- **ConfigMaps**: Non-sensitive configuration like API_VERSION, DEBUG flags, public URLs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can deploy the complete application stack to Minikube in under 5 minutes using documented commands
- **SC-002**: All pods (frontend and backend) reach Running state within 3 minutes of Helm installation
- **SC-003**: Users can access the frontend through browser and complete full task creation workflow (login, create task, verify persistence)
- **SC-004**: AI chat functionality works with real Gemini API responses when valid API key is provided
- **SC-005**: `helm lint` passes with no errors on all generated charts
- **SC-006**: Application survives pod restarts (data persists in external database, sessions remain valid)
- **SC-007**: Resource usage stays within defined limits (e.g., frontend < 512MB RAM, backend < 512MB RAM)
- **SC-008**: Health check endpoints respond successfully within 5 seconds of pod readiness

## Assumptions

- Minikube is installed and running with sufficient resources (recommended: 4 CPU, 8GB RAM)
- Docker Desktop is installed and configured as the container runtime
- kubectl CLI is installed and configured to communicate with Minikube cluster
- Developer has internet connectivity for pulling base images and connecting to Neon database
- External Neon PostgreSQL database is accessible and has required schema migrations applied
- Valid GEMINI_API_KEY is available for AI chat functionality
- Node.js and Python development environments are available for local builds if needed

## Out of Scope

- Production deployment to cloud Kubernetes services (EKS, GKE, AKS)
- CI/CD pipeline configuration (GitHub Actions, GitLab CI)
- Horizontal Pod Autoscaling (HPA) configuration
- Persistent volume provisioning for local database (using external Neon instead)
- SSL/TLS certificate management (local development uses HTTP)
- Multi-namespace deployment strategies
- Istio or other service mesh integration
- Monitoring stack deployment (Prometheus, Grafana)

## Dependencies

- **Docker Desktop**: Required for building container images and Minikube integration
- **Minikube**: Local Kubernetes cluster runtime
- **Helm 3.x**: Package manager for Kubernetes
- **kubectl**: Kubernetes CLI for cluster interaction
- **kubectl-ai or Kagent**: AI-assisted Kubernetes tooling (will be installed as part of this feature)
- **Neon PostgreSQL**: External database service (existing, requires connectivity)
- **Gemini API**: External AI service for chat functionality (requires valid API key)

## Constraints

- **Technology**: Docker Desktop for containerization (Windows/macOS compatible)
- **Orchestration**: Minikube only (not Docker Compose or other local K8s distributions)
- **Package Management**: Helm Charts exclusively (no raw kubectl apply for application deployment)
- **AI Tooling**: Must demonstrate kubectl-ai and/or Kagent usage for chart generation
- **Database**: External Neon PostgreSQL only (no local PostgreSQL container)
- **AI Service**: Real Gemini API with provided key (no mock service)
