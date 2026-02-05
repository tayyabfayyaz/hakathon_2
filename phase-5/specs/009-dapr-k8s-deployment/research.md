# Research: Dapr Microservices Deployment on AKS and GKE

**Feature**: 009-dapr-k8s-deployment
**Date**: 2026-02-03
**Status**: Complete

## Research Topics

### 1. Dapr Runtime Installation Best Practices

**Decision**: Use Helm for Dapr installation with custom values for production readiness

**Rationale**:
- Helm is the official recommended installation method for production
- Provides version control and rollback capabilities
- Allows customization of resource limits, HA mode, and observability settings
- Dapr documentation recommends Helm over dapr CLI for production clusters

**Alternatives Considered**:
- `dapr init -k`: Simpler but less configurable; suitable for development only
- Manual YAML manifests: More control but harder to maintain and upgrade

**Implementation Notes**:
```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install with production values
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system --create-namespace \
  --values helm/values/dapr-values.yaml \
  --wait
```

---

### 2. Kafka vs Redis Pub/Sub for Dapr

**Decision**: Kafka (Confluent Cloud) as primary, Redis Streams as fallback

**Rationale**:
- Kafka: Production-grade, ordered delivery, persistence, replay capability
- Redis Streams: Simpler setup, no external account needed, works for development/testing
- Both are fully supported Dapr Pub/Sub components

**Alternatives Considered**:
- RabbitMQ: Good option but requires more infrastructure than Redis fallback
- NATS: Lightweight but less enterprise adoption than Kafka
- Azure Service Bus/GCP Pub/Sub: Would create cloud vendor lock-in

**Kafka Component Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: brokers
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
```

---

### 3. State Store Selection per Cloud

**Decision**:
- AKS: Azure Cosmos DB (SQL API)
- GKE: Google Cloud Firestore (Native mode)
- Fallback: Redis (both platforms)

**Rationale**:
- Native cloud services provide managed scaling, backups, and integration with IAM
- Cosmos DB: Globally distributed, multi-model database with strong consistency options
- Firestore: Serverless, scales automatically, native GCP IAM integration
- Redis fallback ensures the system works without cloud-specific setup

**Alternatives Considered**:
- PostgreSQL: Good but requires more management overhead
- MongoDB Atlas: Cross-cloud but adds another managed service dependency
- etcd: Too low-level for application state

**Cosmos DB Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.azure.cosmosdb
  version: v1
  metadata:
    - name: url
      secretKeyRef:
        name: cosmosdb-secrets
        key: url
    - name: masterKey
      secretKeyRef:
        name: cosmosdb-secrets
        key: masterKey
    - name: database
      value: "dapr-state"
    - name: collection
      value: "state"
```

---

### 4. Secret Store Integration Patterns

**Decision**:
- AKS: Azure Key Vault with Azure AD Workload Identity
- GKE: Google Secret Manager with Workload Identity

**Rationale**:
- Workload Identity eliminates the need for static credentials in pods
- Native cloud secret stores provide audit logging, rotation, and access policies
- Dapr abstracts the underlying store, keeping application code portable

**Alternatives Considered**:
- HashiCorp Vault: More features but adds operational complexity
- Kubernetes Secrets with External Secrets Operator: Good but another component to manage
- SOPS/sealed-secrets: For GitOps but doesn't integrate with Dapr natively

**Azure Key Vault Setup**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.azure.keyvault
  version: v1
  metadata:
    - name: vaultName
      value: "my-keyvault"
    - name: azureClientId
      value: "" # Uses workload identity
```

---

### 5. Kubernetes Configuration Management

**Decision**: Kustomize with base/overlays structure

**Rationale**:
- Built into kubectl (no additional tooling)
- Clean separation between base resources and environment-specific patches
- Handles AKS vs GKE differences elegantly
- Easier to understand than Helm for application manifests

**Alternatives Considered**:
- Helm charts for apps: Overkill for internal services; templating complexity
- Plain YAML with sed/envsubst: Fragile, hard to maintain
- Jsonnet/cdk8s: More powerful but steeper learning curve

**Kustomize Structure**:
```
deploy/kubernetes/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   └── deployments...
├── overlays/
│   ├── aks/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── gke/
│       ├── kustomization.yaml
│       └── patches/
```

---

### 6. CI/CD Pipeline Design

**Decision**: GitHub Actions with environment-based deployments

**Rationale**:
- Spec requirement for GitHub Actions
- Environment protection rules for production deployments
- Matrix builds for multi-platform images (if needed)
- Native integration with GitHub Secrets for credentials

**Workflow Structure**:
1. **ci.yaml**: Triggered on PRs and pushes
   - Run unit tests (pytest)
   - Lint Python code (flake8, black)
   - Build Docker images
   - Run security scans (trivy)

2. **deploy.yaml**: Triggered on main branch merge
   - Build and push images to registry
   - Deploy to target cluster (AKS or GKE)
   - Run smoke tests
   - Notify on failure

**Secrets Required**:
| Secret | Platform | Purpose |
|--------|----------|---------|
| AZURE_CREDENTIALS | AKS | Service principal JSON |
| ACR_LOGIN_SERVER | AKS | Container registry URL |
| GCP_CREDENTIALS | GKE | Service account key JSON |
| GCP_PROJECT_ID | GKE | Project identifier |
| KUBECONFIG_AKS | AKS | Cluster credentials |
| KUBECONFIG_GKE | GKE | Cluster credentials |

---

### 7. Monitoring Stack Configuration

**Decision**: Prometheus + Grafana deployed via Helm with Dapr-specific dashboards

**Rationale**:
- Industry standard, extensive ecosystem
- Dapr exposes Prometheus metrics by default on :9090/metrics
- Pre-built Dapr dashboards available for Grafana
- Works identically on AKS and GKE

**Alternatives Considered**:
- Azure Monitor + Application Insights: AKS-only, not portable to GKE
- Google Cloud Operations (Stackdriver): GKE-only, not portable to AKS
- Datadog/New Relic: Excellent but adds cost and vendor dependency

**Prometheus Configuration**:
```yaml
# Scrape Dapr sidecars
scrape_configs:
  - job_name: 'dapr'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
        action: keep
        regex: "true"
```

---

### 8. Logging Architecture

**Decision**: Fluentd DaemonSet with cloud-native backends

**Rationale**:
- Fluentd is CNCF graduated, battle-tested
- Can ship to Azure Monitor (AKS) or Cloud Logging (GKE)
- Also works with self-hosted ELK if needed
- Dapr sidecar logs are captured automatically from stdout

**Alternatives Considered**:
- Fluent Bit: Lighter but fewer plugins
- Loki + Promtail: Good with Grafana but newer, less enterprise adoption
- Cloud-native only (Container Insights, GKE logging): Not portable

**Log Format**:
```json
{
  "timestamp": "2026-02-03T10:00:00Z",
  "level": "INFO",
  "service": "publisher",
  "dapr_app_id": "publisher-service",
  "message": "Published message to topic orders",
  "trace_id": "abc123"
}
```

---

### 9. Network Security Policies

**Decision**: Kubernetes NetworkPolicies with default-deny and explicit allowlists

**Rationale**:
- Native Kubernetes feature, works on both AKS and GKE
- Dapr sidecars require specific ports (3500 for HTTP, 50001 for gRPC)
- Default-deny ensures only expected traffic flows

**Required Policies**:
1. Allow Dapr sidecar to communicate with Dapr control plane
2. Allow application container to talk to its sidecar only
3. Allow ingress traffic to subscriber for topic subscriptions
4. Deny all other pod-to-pod communication

---

### 10. Python SDK and Application Design

**Decision**: Flask-based services with Dapr Python SDK

**Rationale**:
- Flask is lightweight, widely understood
- Dapr Python SDK provides helper functions for all building blocks
- CloudEvents format for Pub/Sub messages (Dapr default)

**Alternatives Considered**:
- FastAPI: Better for async but adds complexity for demo app
- Raw HTTP calls: More portable but loses SDK convenience
- Node.js/Go: Good options but Python matches spec assumption

**Publisher Service Pattern**:
```python
from flask import Flask
from dapr.clients import DaprClient

app = Flask(__name__)

@app.route('/publish', methods=['POST'])
def publish():
    with DaprClient() as client:
        client.publish_event(
            pubsub_name='pubsub',
            topic_name='orders',
            data={'order_id': '123'}
        )
    return {'status': 'published'}
```

---

## Summary of Decisions

| Area | Decision | Primary Reason |
|------|----------|----------------|
| Dapr Install | Helm | Production-grade, configurable |
| Pub/Sub Primary | Kafka | Ordered, persistent, enterprise |
| Pub/Sub Fallback | Redis | Simple, no account needed |
| State (AKS) | Cosmos DB | Native Azure, managed |
| State (GKE) | Firestore | Native GCP, managed |
| State Fallback | Redis | Universal |
| Secrets (AKS) | Key Vault | Workload Identity |
| Secrets (GKE) | Secret Manager | Workload Identity |
| K8s Config | Kustomize | Built-in, overlays |
| CI/CD | GitHub Actions | Spec requirement |
| Monitoring | Prometheus/Grafana | Standard, portable |
| Logging | Fluentd | CNCF, flexible backends |
| App Language | Python + Flask | Simple, good SDK |
