---
description: Deploy and configure monitoring stack (Prometheus, Grafana, Fluentd) for Kubernetes observability.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# Kubernetes Monitoring Stack Deployment Agent

## Core Principle

You are an autonomous monitoring deployment agent. Set up comprehensive observability for Kubernetes clusters using Prometheus, Grafana, and Fluentd.

---

## Phase 1: Prerequisites

### 1.1 Verify Cluster Access

```bash
kubectl cluster-info
kubectl get nodes
```

### 1.2 Check Existing Monitoring

```bash
# Check for existing monitoring namespace
kubectl get namespace monitoring 2>/dev/null && echo "Monitoring namespace exists" || echo "Will create monitoring namespace"

# Check for existing Prometheus
kubectl get pods -n monitoring -l app=prometheus 2>/dev/null

# Check for existing Grafana
kubectl get pods -n monitoring -l app=grafana 2>/dev/null
```

---

## Phase 2: Create Monitoring Namespace

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Add labels for network policies
kubectl label namespace monitoring monitoring=true --overwrite
```

---

## Phase 3: Deploy Prometheus

### 3.1 Apply Prometheus Manifests

```bash
kubectl apply -f deploy/kubernetes/monitoring/prometheus/
```

### 3.2 Or Deploy from Inline (if manifests don't exist)

```bash
# ConfigMap
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__

      - job_name: 'dapr-sidecars'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
            action: keep
            regex: "true"
          - source_labels: [__address__]
            action: replace
            regex: ([^:]+)(?::\d+)?
            replacement: $1:9090
            target_label: __address__
EOF

# Deployment
kubectl apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
        - name: prometheus
          image: prom/prometheus:v2.45.0
          args:
            - '--config.file=/etc/prometheus/prometheus.yml'
            - '--storage.tsdb.path=/prometheus/'
            - '--storage.tsdb.retention.time=7d'
            - '--web.enable-lifecycle'
          ports:
            - containerPort: 9090
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
            - name: storage
              mountPath: /prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
        - name: storage
          emptyDir: {}
EOF

# Service
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 9090
      targetPort: 9090
  selector:
    app: prometheus
EOF

# ServiceAccount and RBAC
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources: ["nodes", "nodes/proxy", "services", "endpoints", "pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get"]
  - nonResourceURLs: ["/metrics"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
EOF
```

### 3.3 Verify Prometheus

```bash
kubectl get pods -n monitoring -l app=prometheus
kubectl rollout status deployment/prometheus -n monitoring
```

---

## Phase 4: Deploy Grafana

### 4.1 Apply Grafana Manifests

```bash
kubectl apply -f deploy/kubernetes/monitoring/grafana/
```

### 4.2 Or Deploy from Inline

```bash
# Secret for admin password
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: grafana-secrets
  namespace: monitoring
type: Opaque
stringData:
  admin-user: admin
  admin-password: admin123  # Change in production!
EOF

# ConfigMap for datasources
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        access: proxy
        url: http://prometheus:9090
        isDefault: true
        editable: false
EOF

# Deployment
kubectl apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:10.0.0
          ports:
            - containerPort: 3000
          env:
            - name: GF_SECURITY_ADMIN_USER
              valueFrom:
                secretKeyRef:
                  name: grafana-secrets
                  key: admin-user
            - name: GF_SECURITY_ADMIN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: grafana-secrets
                  key: admin-password
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "300m"
          volumeMounts:
            - name: datasources
              mountPath: /etc/grafana/provisioning/datasources
            - name: storage
              mountPath: /var/lib/grafana
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: datasources
          configMap:
            name: grafana-datasources
        - name: storage
          emptyDir: {}
EOF

# Service
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  type: ClusterIP
  ports:
    - port: 3000
      targetPort: 3000
  selector:
    app: grafana
EOF
```

### 4.3 Verify Grafana

```bash
kubectl get pods -n monitoring -l app=grafana
kubectl rollout status deployment/grafana -n monitoring
```

---

## Phase 5: Deploy Fluentd (Log Aggregation)

### 5.1 Apply Fluentd Manifests

```bash
kubectl apply -f deploy/kubernetes/monitoring/fluentd/
```

### 5.2 Or Deploy from Inline

```bash
# ConfigMap
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: monitoring
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>

    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>

    <match kubernetes.var.log.containers.**dapr-demo**.log>
      @type stdout
      <format>
        @type json
      </format>
    </match>

    <match kubernetes.var.log.containers.**dapr-system**.log>
      @type stdout
      <format>
        @type json
      </format>
    </match>

    <match **>
      @type null
    </match>
EOF

# DaemonSet
kubectl apply -f - <<'EOF'
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccountName: fluentd
      tolerations:
        - key: node-role.kubernetes.io/master
          effect: NoSchedule
      containers:
        - name: fluentd
          image: fluent/fluentd-kubernetes-daemonset:v1.16-debian-elasticsearch8-1
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
          volumeMounts:
            - name: config
              mountPath: /fluentd/etc
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: fluentd-config
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
EOF

# ServiceAccount and RBAC
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
rules:
  - apiGroups: [""]
    resources: ["pods", "namespaces"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluentd
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: fluentd
subjects:
  - kind: ServiceAccount
    name: fluentd
    namespace: monitoring
EOF
```

### 5.3 Verify Fluentd

```bash
kubectl get pods -n monitoring -l app=fluentd
```

---

## Phase 6: Access Monitoring Stack

### 6.1 Port Forwarding (Development)

```bash
# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
echo "Prometheus: http://localhost:9090"

# Grafana
kubectl port-forward svc/grafana 3001:3000 -n monitoring &
echo "Grafana: http://localhost:3001 (admin/admin123)"
```

### 6.2 NodePort (Minikube)

```bash
# Expose as NodePort
kubectl patch svc prometheus -n monitoring -p '{"spec": {"type": "NodePort"}}'
kubectl patch svc grafana -n monitoring -p '{"spec": {"type": "NodePort"}}'

# Get URLs
echo "Prometheus: http://$(minikube ip):$(kubectl get svc prometheus -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')"
echo "Grafana: http://$(minikube ip):$(kubectl get svc grafana -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')"
```

### 6.3 Ingress (Production)

```bash
kubectl apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: monitoring
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: prometheus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus
            port:
              number: 9090
  - host: grafana.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
EOF
```

---

## Phase 7: Import Dashboards

### 7.1 Kubernetes Cluster Dashboard

```bash
# Import via Grafana API
kubectl exec -n monitoring deployment/grafana -- \
  curl -X POST http://admin:admin123@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d '{"dashboard":{"id":null,"uid":null,"title":"Kubernetes Cluster","tags":["kubernetes"],"timezone":"browser","schemaVersion":16,"version":0},"overwrite":true}'
```

### 7.2 Dapr Dashboard

```bash
# Dapr provides its own dashboard
dapr dashboard -k -n dapr-system
```

### 7.3 Popular Dashboard IDs

| Dashboard | Grafana ID | Description |
|-----------|------------|-------------|
| Kubernetes Cluster | 315 | Cluster overview |
| Node Exporter | 1860 | Node metrics |
| Kubernetes Pods | 6417 | Pod metrics |
| Dapr | Custom | Dapr sidecar metrics |

---

## Phase 8: Validation

### 8.1 Check All Pods

```bash
kubectl get pods -n monitoring
```

### 8.2 Verify Prometheus Targets

```bash
# Port forward and check
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'
```

### 8.3 Verify Grafana Datasources

```bash
kubectl port-forward svc/grafana 3001:3000 -n monitoring &
curl -s http://admin:admin123@localhost:3001/api/datasources | jq '.[].name'
```

### 8.4 Check Fluentd Logs

```bash
kubectl logs -n monitoring -l app=fluentd --tail=20
```

---

## Phase 9: Configure Alerts (Optional)

### 9.1 Prometheus Alerting Rules

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alerts
  namespace: monitoring
data:
  alerts.yml: |
    groups:
      - name: kubernetes-alerts
        rules:
          - alert: PodCrashLooping
            expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Pod {{ $labels.pod }} is crash looping"

          - alert: PodNotReady
            expr: kube_pod_status_ready{condition="true"} == 0
            for: 10m
            labels:
              severity: critical
            annotations:
              summary: "Pod {{ $labels.pod }} is not ready"

          - alert: HighMemoryUsage
            expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Container {{ $labels.container }} memory usage > 90%"
EOF
```

---

## Cleanup

### Remove Monitoring Stack

```bash
kubectl delete namespace monitoring
```

### Remove Specific Components

```bash
kubectl delete deployment prometheus -n monitoring
kubectl delete deployment grafana -n monitoring
kubectl delete daemonset fluentd -n monitoring
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Check pods | `kubectl get pods -n monitoring` |
| Prometheus UI | `kubectl port-forward svc/prometheus 9090:9090 -n monitoring` |
| Grafana UI | `kubectl port-forward svc/grafana 3001:3000 -n monitoring` |
| View logs | `kubectl logs -f deployment/prometheus -n monitoring` |
| Fluentd logs | `kubectl logs -n monitoring -l app=fluentd` |
| Dapr dashboard | `dapr dashboard -k` |

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).
