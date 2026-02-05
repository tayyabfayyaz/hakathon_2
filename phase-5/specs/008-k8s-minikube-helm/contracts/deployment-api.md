# Deployment API Contract

**Feature**: 008-k8s-minikube-helm
**Date**: 2026-02-01

## CLI Commands Contract

### 1. Prerequisites Check

**Command**: `make check-prerequisites` or `./scripts/check-prereqs.sh`

**Output Contract**:
```
Checking prerequisites...
✓ Docker: v24.0.0
✓ Minikube: v1.32.0
✓ Helm: v3.14.0
✓ kubectl: v1.29.0
All prerequisites met!
```

**Error Output**:
```
✗ Minikube: Not found
  Install: https://minikube.sigs.k8s.io/docs/start/
```

**Exit Codes**:
- `0`: All prerequisites met
- `1`: One or more prerequisites missing

---

### 2. Build Images

**Command**: `make build` or `./scripts/build-images.sh`

**Input**: None (uses current source code)

**Output Contract**:
```
Setting up Minikube Docker environment...
Building frontend image...
Successfully built todolist-frontend:local
Building backend image...
Successfully built todolist-backend:local
Images built successfully!
```

**Exit Codes**:
- `0`: Images built successfully
- `1`: Build failed

---

### 3. Deploy Application

**Command**: `make deploy` or `helm install todolist ./helm/todolist`

**Input**: Optional `values.yaml` override

**Output Contract**:
```
Deploying TodoList Pro to Kubernetes...
NAME: todolist
NAMESPACE: default
STATUS: deployed
REVISION: 1

Waiting for pods to be ready...
✓ todolist-frontend: Running (1/1)
✓ todolist-backend: Running (1/1)

Access the application:
  Frontend URL: http://192.168.49.2:30080
  Backend API: http://192.168.49.2:30081

Run 'minikube service todolist-frontend' for browser access
```

**Exit Codes**:
- `0`: Deployment successful
- `1`: Deployment failed

---

### 4. Get Application Status

**Command**: `make status` or `kubectl get all -l app=todolist`

**Output Contract**:
```
NAME                                    READY   STATUS    RESTARTS   AGE
pod/todolist-frontend-xxx               1/1     Running   0          5m
pod/todolist-backend-xxx                1/1     Running   0          5m

NAME                        TYPE        CLUSTER-IP      PORT(S)
service/todolist-frontend   NodePort    10.96.x.x       80:30080/TCP
service/todolist-backend    ClusterIP   10.96.x.x       8000/TCP

NAME                                READY   UP-TO-DATE   AVAILABLE
deployment/todolist-frontend        1/1     1            1
deployment/todolist-backend         1/1     1            1
```

---

### 5. Scale Backend

**Command**: `make scale-backend REPLICAS=3` or `kubectl scale deployment todolist-backend --replicas=3`

**Input**: `REPLICAS` (integer, >= 1)

**Output Contract**:
```
Scaling todolist-backend to 3 replicas...
deployment.apps/todolist-backend scaled
Waiting for replicas...
✓ 3/3 replicas ready
```

**Exit Codes**:
- `0`: Scaling successful
- `1`: Scaling failed or timeout

---

### 6. View Logs

**Command**: `make logs-frontend` or `make logs-backend`

**Output Contract**:
```
Streaming logs for todolist-backend...
[2026-02-01 10:30:00] INFO: Starting TodoList Pro API...
[2026-02-01 10:30:01] INFO: Database initialized
[2026-02-01 10:30:02] INFO: Application startup complete
```

---

### 7. Cleanup

**Command**: `make cleanup` or `helm uninstall todolist`

**Output Contract**:
```
Removing TodoList Pro from Kubernetes...
release "todolist" uninstalled
Cleaning up resources...
✓ Deployments removed
✓ Services removed
✓ ConfigMaps removed
✓ Secrets removed
Cleanup complete!
```

**Exit Codes**:
- `0`: Cleanup successful
- `1`: Cleanup failed

---

### 8. Full Reset

**Command**: `make reset`

**Output Contract**:
```
Performing full reset...
Uninstalling Helm release...
Removing local images...
Stopping Minikube...
Starting fresh Minikube cluster...
Reset complete!
```

---

## Health Check Endpoints

### Backend Health

**Endpoint**: `GET /health`

**Response Contract**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2026-02-01T10:30:00Z"
}
```

**Status Codes**:
- `200`: Healthy
- `503`: Unhealthy (database disconnected)

---

### Frontend Health

**Endpoint**: `GET /api/health`

**Response Contract**:
```json
{
  "status": "ok",
  "timestamp": "2026-02-01T10:30:00Z"
}
```

**Status Codes**:
- `200`: Healthy

---

## AI Tools Integration API

### kubectl-ai

**Command Pattern**: `kubectl-ai "<natural language query>"`

**Input Contract**:
```
kubectl-ai "why is my backend pod not starting?"
```

**Output Contract**:
```
Analyzing cluster state...

Issue Detected: ImagePullBackOff
Cause: Image 'todolist-backend:local' not found in Minikube Docker daemon

Recommended Fix:
1. Run: eval $(minikube docker-env)
2. Run: docker build -t todolist-backend:local ./backend
3. Run: kubectl delete pod <pod-name>

Would you like me to execute these commands? [y/n]
```

---

### Kagent Diagnostics

**Command Pattern**: `kagent diagnose <resource>`

**Input Contract**:
```
kagent diagnose deployment/todolist-backend
```

**Output Contract**:
```
=== Deployment Diagnostics ===
Name: todolist-backend
Namespace: default
Replicas: 1/1 ready

Pod Status:
  - todolist-backend-xxx: Running

Container Logs (last 10 lines):
  INFO: Application startup complete

Resource Usage:
  CPU: 50m / 500m (10%)
  Memory: 128Mi / 512Mi (25%)

Health Checks:
  Liveness: Passing
  Readiness: Passing

No issues detected ✓
```

---

## Error Codes Reference

| Code | Description | Resolution |
|------|-------------|------------|
| `E001` | Minikube not running | Run `minikube start` |
| `E002` | Image build failed | Check Dockerfile syntax |
| `E003` | Helm install failed | Check values.yaml |
| `E004` | Pod startup timeout | Check logs with `make logs-*` |
| `E005` | Database connection failed | Verify DATABASE_URL secret |
| `E006` | Port conflict | Change NodePort in values.yaml |
| `E007` | Resource quota exceeded | Reduce resource requests |
