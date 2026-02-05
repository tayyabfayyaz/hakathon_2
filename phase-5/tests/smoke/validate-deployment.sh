#!/usr/bin/env bash
set -euo pipefail

# Deployment Validation Smoke Tests
NAMESPACE="${NAMESPACE:-dapr-demo}"
TIMEOUT="${TIMEOUT:-120}"
PASSED=0
FAILED=0

pass() { echo "  PASS: $1"; ((PASSED++)); }
fail() { echo "  FAIL: $1"; ((FAILED++)); }

echo "=== Deployment Validation ==="
echo "Namespace: $NAMESPACE"
echo ""

# Test 1: Namespace exists
echo "[Test 1] Namespace exists"
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
  pass "Namespace $NAMESPACE exists"
else
  fail "Namespace $NAMESPACE not found"
fi

# Test 2: Dapr system pods running
echo "[Test 2] Dapr system pods running"
DAPR_PODS=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | grep -c "Running" || echo "0")
if [ "$DAPR_PODS" -ge 4 ]; then
  pass "Dapr system has $DAPR_PODS running pods"
else
  fail "Expected at least 4 Dapr system pods, found $DAPR_PODS"
fi

# Test 3: Publisher pod running with sidecar (2/2)
echo "[Test 3] Publisher pod with Dapr sidecar"
PUB_STATUS=$(kubectl get pods -n "$NAMESPACE" -l app=publisher --no-headers 2>/dev/null | head -1)
if echo "$PUB_STATUS" | grep -q "2/2.*Running"; then
  pass "Publisher pod running with Dapr sidecar (2/2)"
else
  fail "Publisher pod not in expected state: $PUB_STATUS"
fi

# Test 4: Subscriber pod running with sidecar (2/2)
echo "[Test 4] Subscriber pod with Dapr sidecar"
SUB_STATUS=$(kubectl get pods -n "$NAMESPACE" -l app=subscriber --no-headers 2>/dev/null | head -1)
if echo "$SUB_STATUS" | grep -q "2/2.*Running"; then
  pass "Subscriber pod running with Dapr sidecar (2/2)"
else
  fail "Subscriber pod not in expected state: $SUB_STATUS"
fi

# Test 5: Publisher health endpoint
echo "[Test 5] Publisher health endpoint"
PUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=publisher -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$PUB_POD" ]; then
  HEALTH=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- curl -s http://localhost:5000/health 2>/dev/null || echo "")
  if echo "$HEALTH" | grep -q "healthy"; then
    pass "Publisher health endpoint responding"
  else
    fail "Publisher health endpoint not healthy: $HEALTH"
  fi
else
  fail "No publisher pod found"
fi

# Test 6: Subscriber health endpoint
echo "[Test 6] Subscriber health endpoint"
SUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=subscriber -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$SUB_POD" ]; then
  HEALTH=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- curl -s http://localhost:5000/health 2>/dev/null || echo "")
  if echo "$HEALTH" | grep -q "healthy"; then
    pass "Subscriber health endpoint responding"
  else
    fail "Subscriber health endpoint not healthy: $HEALTH"
  fi
else
  fail "No subscriber pod found"
fi

# Test 7: Services exist
echo "[Test 7] Kubernetes services exist"
SVC_COUNT=$(kubectl get svc -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$SVC_COUNT" -ge 2 ]; then
  pass "Found $SVC_COUNT services"
else
  fail "Expected at least 2 services, found $SVC_COUNT"
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"

if [ "$FAILED" -gt 0 ]; then
  echo "STATUS: FAIL"
  exit 1
fi

echo "STATUS: PASS"
exit 0
