# Scaling Guide

This guide explains how to scale the TodoList Pro application components in Kubernetes.

## Overview

The TodoList Pro deployment supports both manual and automatic scaling:

- **Manual scaling**: Directly set the number of replicas
- **Automatic scaling**: Use Horizontal Pod Autoscaler (HPA) based on CPU/memory metrics

## Manual Scaling

### Using Makefile

Scale the backend service using the provided Makefile target:

```bash
# Scale backend to 3 replicas
make scale-backend REPLICAS=3

# Scale backend to 5 replicas
make scale-backend REPLICAS=5

# Scale backend to 1 replica (default)
make scale-backend REPLICAS=1
```

### Using kubectl

Alternatively, use kubectl directly:

```bash
# Scale backend deployment
kubectl scale deployment todolist-backend --replicas=3

# Scale frontend deployment
kubectl scale deployment todolist-frontend --replicas=2

# Check current replica counts
kubectl get deployments
```

## Automatic Scaling (HPA)

### Enable HPA

Horizontal Pod Autoscaler is configured for the backend service but disabled by default. To enable it, update your values file:

```yaml
# In values-prod.yaml or similar
backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    # Optional: Add memory-based scaling
    targetMemoryUtilizationPercentage: 80
```

Then deploy with the updated values:

```bash
helm upgrade --install todolist ./helm/todolist -f values-prod.yaml
```

### HPA Configuration

The HPA configuration includes:

- **Min/Max Replicas**: Prevents scaling below/above specified limits
- **CPU Target**: Maintains average CPU utilization across pods
- **Memory Target**: Maintains average memory utilization (optional)
- **Scaling Behavior**: Controls how quickly to scale up/down

### Monitor HPA

Check the status of the Horizontal Pod Autoscaler:

```bash
# View HPA status
kubectl get hpa

# Get detailed HPA information
kubectl describe hpa todolist-backend

# Watch scaling events
kubectl get events --watch
```

## Resource Configuration

Proper resource requests and limits are crucial for effective scaling:

```yaml
# Example resource configuration
backend:
  resources:
    requests:
      memory: "256Mi"    # Minimum guaranteed resources
      cpu: "200m"       # Minimum guaranteed CPU
    limits:
      memory: "512Mi"   # Maximum allowed resources
      cpu: "500m"       # Maximum allowed CPU
```

### Resource Recommendations

- **Development**: Lower resources, fewer replicas
- **Staging**: Moderate resources, auto-scaling enabled
- **Production**: Higher resources, auto-scaling with appropriate thresholds

## Best Practices

### 1. Start Conservative

Begin with conservative resource requests and adjust based on actual usage:

```bash
# Monitor actual usage
kubectl top pods
kubectl top nodes
```

### 2. Appropriate Scaling Thresholds

Set CPU utilization targets between 60-80% to balance performance and cost:

```yaml
# Good target range
targetCPUUtilizationPercentage: 70
```

### 3. Memory Scaling

Consider memory-based scaling for memory-intensive workloads:

```yaml
# Enable both CPU and memory scaling
autoscaling:
  enabled: true
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### 4. Scaling Delays

Configure appropriate scaling delays to prevent flapping:

```yaml
# In values file (advanced configuration)
backend:
  autoscaling:
    behavior:
      scaleDown:
        stabilizationWindowSeconds: 300  # 5 minutes cooldown
      scaleUp:
        stabilizationWindowSeconds: 60   # 1 minute to scale up
```

## Troubleshooting

### Scaling Isn't Working

1. **Check HPA is enabled:**
   ```bash
   kubectl get hpa
   ```

2. **Verify resource requests are set:**
   ```bash
   kubectl describe deployment todolist-backend
   ```

3. **Check metrics server is running:**
   ```bash
   kubectl top nodes
   ```

### Too Much Scaling

1. **Review target percentages:**
   ```bash
   # Lower target to reduce scaling
   targetCPUUtilizationPercentage: 50
   ```

2. **Adjust min/max replicas:**
   ```yaml
   minReplicas: 2
   maxReplicas: 5
   ```

### Scaling Delays

If scaling is too slow or too fast, adjust the behavior configuration:

```yaml
autoscaling:
  behavior:
    scaleUp:
      policies:
      - type: Percent
        value: 50  # Scale up 50% of current replicas
        periodSeconds: 60
    scaleDown:
      policies:
      - type: Percent
        value: 10  # Scale down 10% of current replicas
        periodSeconds: 300
```

## Verification

### Test Scaling

1. **Deploy with HPA enabled:**
   ```bash
   helm upgrade --install todolist ./helm/todolist -f values-prod.yaml
   ```

2. **Apply load to trigger scaling:**
   ```bash
   # Use a load testing tool
   kubectl run load-test --image=curlimages/curl -it --rm -- \
     sh -c "for i in \$(seq 1 100); do curl -s http://todolist-backend:8000/api/tasks; done"
   ```

3. **Monitor scaling:**
   ```bash
   kubectl get hpa --watch
   kubectl get pods
   ```

### Check Metrics

Verify that metrics are available for scaling decisions:

```bash
# Check current metrics
kubectl top pods
kubectl top nodes

# Check historical metrics (if using Prometheus)
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq
```