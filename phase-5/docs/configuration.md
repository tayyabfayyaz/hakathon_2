# Configuration Management Guide

This guide explains how to manage configuration for different environments in the TodoList Pro Kubernetes deployment.

## Overview

Configuration in the TodoList Pro Helm chart is managed through:

1. **Default values** (`values.yaml`) - Base configuration shared across all environments
2. **Environment-specific values** (`values-dev.yaml`, `values-prod.yaml`) - Overrides for specific environments
3. **ConfigMaps** - Non-sensitive configuration stored in Kubernetes
4. **Secrets** - Sensitive data stored securely in Kubernetes

## Environment-Specific Values

### Development Environment

Use `values-dev.yaml` for development-specific configuration:

```bash
# Deploy with development values
helm upgrade --install todolist ./helm/todolist -f values-dev.yaml
```

Features:
- Lower resource limits
- Debug mode enabled
- More permissive CORS settings
- Always pull latest images

### Production Environment

Create `values-prod.yaml` for production deployment:

```yaml
# Production values (example)
frontend:
  replicas: 3
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  replicas: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "300m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10

config:
  debug: "false"
  corsOrigins: "https://yourdomain.com"

secrets:
  # Reference external secrets (do not put actual values here)
  databaseUrl: "ref+vault://production-db-url"
```

## Configuration Override Workflow

### 1. Override Individual Values

Use `--set` to override individual values:

```bash
# Override specific values
helm upgrade --install todolist ./helm/todolist \
  --set frontend.replicas=2 \
  --set backend.resources.requests.memory=256Mi
```

### 2. Combine Multiple Value Files

Use multiple `-f` flags to layer configurations:

```bash
# Base + environment + overrides
helm upgrade --install todolist ./helm/todolist \
  -f values.yaml \
  -f values-dev.yaml \
  -f values-local.yaml
```

**Note**: Later files override earlier ones.

### 3. Use Different ConfigMaps/Secrets

Configuration changes are automatically applied to pods through ConfigMaps and Secrets. However, some changes may require pod restart:

```bash
# After updating values, restart pods to apply config changes
kubectl rollout restart deployment/todolist-frontend
kubectl rollout restart deployment/todolist-backend
```

## Managing Secrets Safely

### Best Practices

1. **Never commit secrets to version control**
2. **Use external secret stores** (HashiCorp Vault, AWS Secrets Manager)
3. **Rotate secrets regularly**
4. **Use different secrets per environment**

### Development Secrets

For local development, create `values-local.yaml`:

```bash
# Create local overrides (add to .gitignore)
cp helm/todolist/values-local.yaml.example values-local.yaml
# Edit with your local secrets
```

### Production Secrets

Use external secret management:

```yaml
# values-prod.yaml
secrets:
  # Reference external secret
  databaseUrl: "ref+vault://prod-db-url"
  betterAuthSecret: "ref+vault://better-auth-secret"
```

## Hot-Reload Configuration (Optional)

Some applications support configuration reloading without restart. Currently, the TodoList Pro deployments require restart for config changes.

To restart deployments after config changes:

```bash
# Update config and restart deployments
helm upgrade --install todolist ./helm/todolist -f values-dev.yaml
kubectl rollout restart deployment/todolist-frontend
kubectl rollout restart deployment/todolist-backend
```

## Verification

### Check Applied Configuration

```bash
# View ConfigMap
kubectl describe configmap todolist-config

# View Secret (values are masked)
kubectl describe secret todolist-secrets

# View deployment configuration
kubectl describe deployment todolist-frontend
kubectl describe deployment todolist-backend
```

### Test Configuration

```bash
# Check if pods have received new config
kubectl exec -it deploy/todolist-backend -- env | grep YOUR_VAR

# Verify application behavior with new config
kubectl logs deploy/todolist-backend --tail=20
```

## Troubleshooting

### Configuration Not Applied

1. **Check if ConfigMap/Secret was updated:**
   ```bash
   kubectl get configmap todolist-config -o yaml
   ```

2. **Restart pods if needed:**
   ```bash
   kubectl rollout restart deployment/todolist-frontend
   ```

3. **Verify deployment uses correct values:**
   ```bash
   kubectl get deployment todolist-frontend -o yaml
   ```

### Invalid Configuration

1. **Test configuration locally:**
   ```bash
   helm template test ./helm/todolist -f values-dev.yaml
   ```

2. **Validate syntax:**
   ```bash
   helm lint ./helm/todolist
   ```

3. **Dry-run before applying:**
   ```bash
   helm upgrade --install todolist ./helm/todolist -f values-dev.yaml --dry-run
   ```