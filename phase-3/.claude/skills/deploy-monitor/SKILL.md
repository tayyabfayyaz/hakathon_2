---
name: deploy-monitor
description: Deploy monitoring stack with Prometheus, Grafana, and Fluentd for Kubernetes observability. Use when setting up monitoring, dashboards, metrics collection, log aggregation, or alerting.
argument-hint: "[component]"
allowed-tools: Bash, Read, Glob
---

# Kubernetes Monitoring Stack

Deploy comprehensive observability with Prometheus, Grafana, and Fluentd.

## Components

| Component | Purpose | Port |
|-----------|---------|------|
| Prometheus | Metrics collection | 9090 |
| Grafana | Dashboards & visualization | 3000 |
| Fluentd | Log aggregation | - |

## Quick Deploy

```bash
# Deploy all monitoring components
kubectl apply -f deploy/kubernetes/monitoring/prometheus/
kubectl apply -f deploy/kubernetes/monitoring/grafana/
kubectl apply -f deploy/kubernetes/monitoring/fluentd/
```

## Create Monitoring Namespace

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
```

## Deploy Prometheus

```bash
kubectl apply -f deploy/kubernetes/monitoring/prometheus/

# Verify
kubectl get pods -n monitoring -l app=prometheus
kubectl rollout status deployment/prometheus -n monitoring
```

**What Prometheus collects:**
- Kubernetes pod/node metrics
- Dapr sidecar metrics (port 9090)
- Application metrics (with prometheus annotations)

## Deploy Grafana

```bash
kubectl apply -f deploy/kubernetes/monitoring/grafana/

# Verify
kubectl get pods -n monitoring -l app=grafana
kubectl rollout status deployment/grafana -n monitoring
```

**Default credentials:** admin / admin123

## Deploy Fluentd

```bash
kubectl apply -f deploy/kubernetes/monitoring/fluentd/

# Verify (DaemonSet - one pod per node)
kubectl get pods -n monitoring -l app=fluentd
```

## Access Dashboards

**Port Forwarding:**
```bash
# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
echo "Prometheus: http://localhost:9090"

# Grafana
kubectl port-forward svc/grafana 3001:3000 -n monitoring &
echo "Grafana: http://localhost:3001"
```

**NodePort (Minikube):**
```bash
kubectl patch svc prometheus -n monitoring -p '{"spec": {"type": "NodePort"}}'
kubectl patch svc grafana -n monitoring -p '{"spec": {"type": "NodePort"}}'

echo "Prometheus: http://$(minikube ip):$(kubectl get svc prometheus -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')"
echo "Grafana: http://$(minikube ip):$(kubectl get svc grafana -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')"
```

## Useful Dashboards

Import these Grafana dashboard IDs:
- **315**: Kubernetes Cluster Overview
- **1860**: Node Exporter Full
- **6417**: Kubernetes Pods
- **13770**: Dapr Dashboard

## Dapr Dashboard

```bash
dapr dashboard -k -n dapr-system
```

## Verify Metrics Collection

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Check Grafana datasources
curl -s http://admin:admin123@localhost:3001/api/datasources | jq '.[].name'
```

## Cleanup

```bash
kubectl delete namespace monitoring
```
