#!/bin/bash
# Deployment Validation Script
# Usage: ./validate-deployment.sh <namespace>

NAMESPACE=${1:-todolist}
TIMEOUT=${2:-300}

echo "=== Deployment Validation ==="
echo "Namespace: $NAMESPACE"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Check namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "ERROR: Namespace '$NAMESPACE' does not exist"
    exit 1
fi

# Wait for deployments
echo "Waiting for deployments to be ready..."
DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

for deploy in $DEPLOYMENTS; do
    echo "  Checking: $deploy"
    if ! kubectl rollout status deployment/"$deploy" -n "$NAMESPACE" --timeout="${TIMEOUT}s"; then
        echo "  ERROR: Deployment '$deploy' failed"
        kubectl describe deployment "$deploy" -n "$NAMESPACE"
        exit 1
    fi
    echo "  OK: $deploy is ready"
done

# Check pods
echo ""
echo "Pod Status:"
kubectl get pods -n "$NAMESPACE" -o wide

# Check for any pods not in Running state
NOT_RUNNING=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded -o name 2>/dev/null)
if [ -n "$NOT_RUNNING" ]; then
    echo ""
    echo "WARNING: Some pods are not running:"
    echo "$NOT_RUNNING"
fi

# Check services
echo ""
echo "Services:"
kubectl get svc -n "$NAMESPACE"

# Check endpoints
echo ""
echo "Endpoints:"
kubectl get endpoints -n "$NAMESPACE"

# Health checks
echo ""
echo "=== Health Checks ==="

# Get service endpoints
SERVICES=$(kubectl get svc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

for svc in $SERVICES; do
    PORT=$(kubectl get svc "$svc" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')
    echo "Testing $svc:$PORT..."

    # Run curl from a temporary pod
    RESULT=$(kubectl run curl-test-$RANDOM --image=curlimages/curl --rm -i --restart=Never --timeout=30s -- \
        curl -s -o /dev/null -w "%{http_code}" "http://${svc}.${NAMESPACE}.svc.cluster.local:${PORT}/health" 2>/dev/null || echo "000")

    if [ "$RESULT" = "200" ] || [ "$RESULT" = "204" ]; then
        echo "  OK: $svc health check passed (HTTP $RESULT)"
    else
        echo "  WARN: $svc health check returned HTTP $RESULT"
    fi
done

echo ""
echo "=== Validation Complete ==="
