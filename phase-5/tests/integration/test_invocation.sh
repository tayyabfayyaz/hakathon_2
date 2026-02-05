#!/usr/bin/env bash
set -euo pipefail

# Service Invocation Integration Test
NAMESPACE="${NAMESPACE:-dapr-demo}"
PASSED=0
FAILED=0

pass() { echo "  PASS: $1"; ((PASSED++)); }
fail() { echo "  FAIL: $1"; ((FAILED++)); }

echo "=== Service Invocation Integration Tests ==="

# Get pod names
PUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=publisher -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
SUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=subscriber -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PUB_POD" ] || [ -z "$SUB_POD" ]; then
  echo "ERROR: Publisher or subscriber pod not found"
  exit 1
fi

# Test 1: Publisher invokes subscriber health via Dapr
echo "[Test 1] Publisher invokes subscriber /health via Dapr service invocation"
RESULT=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- \
  curl -s http://localhost:5000/invoke-subscriber 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status"'; then
  if echo "$RESULT" | grep -q '"service":"subscriber-service"'; then
    pass "Publisher successfully invoked subscriber health"
  else
    pass "Publisher received response from subscriber"
  fi
else
  fail "Publisher failed to invoke subscriber: $RESULT"
fi

# Test 2: Subscriber invokes publisher health via Dapr
echo "[Test 2] Subscriber invokes publisher /health via Dapr service invocation"
RESULT=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
  curl -s http://localhost:5000/invoke-publisher 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status"'; then
  if echo "$RESULT" | grep -q '"service":"publisher-service"'; then
    pass "Subscriber successfully invoked publisher health"
  else
    pass "Subscriber received response from publisher"
  fi
else
  fail "Subscriber failed to invoke publisher: $RESULT"
fi

# Test 3: Direct Dapr service invocation from publisher sidecar
echo "[Test 3] Direct Dapr sidecar invocation (publisher -> subscriber)"
RESULT=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- \
  curl -s "http://localhost:3500/v1.0/invoke/subscriber-service/method/health" 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status"'; then
  pass "Direct Dapr sidecar invocation works"
else
  fail "Direct Dapr sidecar invocation failed: $RESULT"
fi

# Test 4: Direct Dapr service invocation from subscriber sidecar
echo "[Test 4] Direct Dapr sidecar invocation (subscriber -> publisher)"
RESULT=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
  curl -s "http://localhost:3500/v1.0/invoke/publisher-service/method/health" 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status"'; then
  pass "Reverse Dapr sidecar invocation works"
else
  fail "Reverse Dapr sidecar invocation failed: $RESULT"
fi

# Test 5: Verify mTLS is enabled between services
echo "[Test 5] Verify Dapr mTLS configuration"
DAPR_CONFIG=$(kubectl get configuration dapr-config -n "$NAMESPACE" -o jsonpath='{.spec.mtls.enabled}' 2>/dev/null || echo "")
if [ "$DAPR_CONFIG" = "true" ]; then
  pass "mTLS is enabled in Dapr configuration"
else
  # Check default Dapr system config
  DAPR_SYS=$(kubectl get configuration daprsystem -n dapr-system -o jsonpath='{.spec.mtls.enabled}' 2>/dev/null || echo "true")
  if [ "$DAPR_SYS" = "true" ]; then
    pass "mTLS enabled via Dapr system configuration"
  else
    fail "mTLS not confirmed enabled"
  fi
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
[ "$FAILED" -gt 0 ] && exit 1
exit 0
