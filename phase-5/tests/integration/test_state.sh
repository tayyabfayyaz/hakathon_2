#!/usr/bin/env bash
set -euo pipefail

# State Store Integration Test
NAMESPACE="${NAMESPACE:-dapr-demo}"
PASSED=0
FAILED=0

pass() { echo "  PASS: $1"; ((PASSED++)); }
fail() { echo "  FAIL: $1"; ((FAILED++)); }

echo "=== State Store Integration Tests ==="

SUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=subscriber -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
PUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=publisher -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$SUB_POD" ] || [ -z "$PUB_POD" ]; then
  echo "ERROR: Required pods not found"
  exit 1
fi

# Test 1: Publish a message (triggers state save in subscriber)
echo "[Test 1] Publish message to trigger state save"
RESULT=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- \
  curl -s -X POST http://localhost:5000/publish \
  -H "Content-Type: application/json" \
  -d '{"order_id":"STATE-TEST-001","amount":100.00,"customer":"state-tester"}' 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status":"published"'; then
  MSG_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message_id',''))" 2>/dev/null || echo "")
  pass "Message published (id: $MSG_ID)"
else
  fail "Failed to publish: $RESULT"
fi

# Wait for processing
sleep 5

# Test 2: Query state by key
echo "[Test 2] Query state via /state endpoint"
if [ -n "$MSG_ID" ]; then
  STATE=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
    curl -s "http://localhost:5000/state/message||${MSG_ID}" 2>/dev/null || echo "")

  if echo "$STATE" | grep -q "message_id"; then
    pass "State retrieved for message $MSG_ID"
  else
    fail "State not found for message $MSG_ID: $STATE"
  fi
else
  fail "No message ID to query"
fi

# Test 3: Query non-existent state (404)
echo "[Test 3] Query non-existent state returns 404"
NOT_FOUND=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
  curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/state/nonexistent-key" 2>/dev/null || echo "")

if [ "$NOT_FOUND" = "404" ]; then
  pass "Non-existent state returns 404"
else
  fail "Expected 404, got $NOT_FOUND"
fi

# Test 4: State persists across queries
echo "[Test 4] State persistence"
if [ -n "$MSG_ID" ]; then
  STATE1=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
    curl -s "http://localhost:5000/state/message||${MSG_ID}" 2>/dev/null || echo "")
  sleep 1
  STATE2=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
    curl -s "http://localhost:5000/state/message||${MSG_ID}" 2>/dev/null || echo "")

  if [ "$STATE1" = "$STATE2" ]; then
    pass "State is persistent across queries"
  else
    fail "State changed between queries"
  fi
else
  fail "No message ID for persistence test"
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
[ "$FAILED" -gt 0 ] && exit 1
exit 0
