# Data Model: Dapr Microservices Deployment

**Feature**: 009-dapr-k8s-deployment
**Date**: 2026-02-03

## Overview

This document defines the data structures used by the microservices application and Dapr components.

## Application Entities

### 1. Message (Pub/Sub Payload)

The message format for publisher-to-subscriber communication via Dapr Pub/Sub.

```yaml
Message:
  description: Event published to the orders topic
  properties:
    id:
      type: string
      format: uuid
      description: Unique message identifier
      example: "550e8400-e29b-41d4-a716-446655440000"
    timestamp:
      type: string
      format: date-time
      description: ISO 8601 timestamp of when message was created
      example: "2026-02-03T10:30:00Z"
    source:
      type: string
      description: Service that published the message
      example: "publisher-service"
    type:
      type: string
      description: Event type for routing/filtering
      enum: [order.created, order.processed, heartbeat]
      example: "order.created"
    data:
      type: object
      description: Event payload
      properties:
        order_id:
          type: string
          example: "ORD-2026-001"
        amount:
          type: number
          format: float
          example: 99.99
        customer:
          type: string
          example: "customer-123"
  required: [id, timestamp, source, type, data]
```

### 2. State Entry

The structure for data stored in Dapr state store.

```yaml
StateEntry:
  description: State stored by subscriber service
  key_format: "{app_id}||{entity_type}||{entity_id}"
  example_key: "subscriber-service||message||550e8400-e29b-41d4-a716-446655440000"
  properties:
    message_id:
      type: string
      description: Reference to original message
    processed_at:
      type: string
      format: date-time
      description: When the message was processed
    status:
      type: string
      enum: [received, processing, completed, failed]
      description: Processing status
    result:
      type: object
      description: Processing result or error details
      properties:
        success:
          type: boolean
        details:
          type: string
    retry_count:
      type: integer
      default: 0
      description: Number of processing attempts
  required: [message_id, processed_at, status]
```

### 3. Health Status

Health check response format for services.

```yaml
HealthStatus:
  description: Service health check response
  properties:
    status:
      type: string
      enum: [healthy, degraded, unhealthy]
    service:
      type: string
      description: Service name/app ID
    version:
      type: string
      description: Application version
    timestamp:
      type: string
      format: date-time
    checks:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
            example: "dapr_sidecar"
          status:
            type: string
            enum: [pass, warn, fail]
          message:
            type: string
  required: [status, service, timestamp]
```

## Dapr Component Configurations

### 4. Pub/Sub Component Schema

```yaml
PubSubComponent:
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: pubsub
    namespace: dapr-demo
  spec:
    type: pubsub.kafka | pubsub.redis
    version: v1
    metadata:
      # Kafka-specific
      - name: brokers
        value: "<kafka-bootstrap-servers>"
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
      # Redis-specific (fallback)
      - name: redisHost
        value: "redis:6379"
      - name: redisPassword
        secretKeyRef:
          name: redis-secrets
          key: password
```

### 5. State Store Component Schema

```yaml
StateStoreComponent:
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: statestore
    namespace: dapr-demo
  spec:
    # Azure Cosmos DB (AKS)
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
    # OR Google Firestore (GKE)
    type: state.gcp.firestore
    version: v1
    metadata:
      - name: project_id
        value: "<gcp-project-id>"
      - name: type
        value: "service_account"
      - name: private_key_id
        secretKeyRef:
          name: firestore-secrets
          key: private_key_id
    # OR Redis (fallback)
    type: state.redis
    version: v1
    metadata:
      - name: redisHost
        value: "redis:6379"
      - name: redisPassword
        secretKeyRef:
          name: redis-secrets
          key: password
```

### 6. Secret Store Component Schema

```yaml
SecretStoreComponent:
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: secretstore
    namespace: dapr-demo
  spec:
    # Azure Key Vault (AKS)
    type: secretstores.azure.keyvault
    version: v1
    metadata:
      - name: vaultName
        value: "<keyvault-name>"
      - name: azureClientId
        value: "" # Uses workload identity
    # OR Google Secret Manager (GKE)
    type: secretstores.gcp.secretmanager
    version: v1
    metadata:
      - name: project_id
        value: "<gcp-project-id>"
      - name: type
        value: "service_account"
```

### 7. Cron Binding Component Schema

```yaml
CronBindingComponent:
  apiVersion: dapr.io/v1alpha1
  kind: Component
  metadata:
    name: cron-binding
    namespace: dapr-demo
  spec:
    type: bindings.cron
    version: v1
    metadata:
      - name: schedule
        value: "@every 30s"  # Configurable: cron expression or duration
      - name: direction
        value: "input"
```

## Kubernetes Resource Specifications

### 8. Deployment Annotations

```yaml
PodAnnotations:
  description: Required annotations for Dapr sidecar injection
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "<service-name>"
    dapr.io/app-port: "5000"
    dapr.io/enable-metrics: "true"
    dapr.io/metrics-port: "9090"
    dapr.io/log-level: "info"
    dapr.io/config: "dapr-config"
```

### 9. Resource Limits

```yaml
ResourceRequirements:
  description: Default resource specifications for services
  application:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"
  dapr_sidecar:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "128Mi"
      cpu: "200m"
```

## State Transitions

### Message Processing State Machine

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
            ┌───────│  received   │
            │       └──────┬──────┘
            │              │
            │              ▼
            │       ┌─────────────┐
            │       │ processing  │◄────┐
            │       └──────┬──────┘     │
            │              │            │
            │         ┌────┴────┐       │
            │         ▼         ▼       │
            │   ┌─────────┐ ┌───────┐   │
            │   │completed│ │failed │───┘
            │   └─────────┘ └───────┘ (retry if count < 3)
            │
            │ (on error before processing)
            └──────────────────────────────▶ failed
```

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| Message | id | Must be valid UUID v4 |
| Message | timestamp | Must be valid ISO 8601 |
| Message | type | Must be in allowed enum |
| StateEntry | key | Must follow `{app_id}\|\|{type}\|\|{id}` format |
| StateEntry | retry_count | Max 3 retries before permanent failure |
| HealthStatus | status | Must reflect actual dependency health |

## Topic and Subscription Configuration

```yaml
Topics:
  orders:
    description: Main topic for order events
    publishers:
      - publisher-service
    subscribers:
      - subscriber-service
    retention: 7d  # Kafka-specific
    partitions: 3  # Kafka-specific

Subscriptions:
  - pubsubname: pubsub
    topic: orders
    route: /events/orders
    scopes:
      - subscriber-service
```
