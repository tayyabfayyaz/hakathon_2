#!/usr/bin/env bash
set -euo pipefail

# Pub/Sub Integration Test
NAMESPACE="${NAMESPACE:-dapr-demo}"
PASSED=0
FAILED=0

pass() { echo "  PASS: $1"; ((PASSED++)); }
fail() { echo "  FAIL: $1"; ((FAILED++)); }

echo "=== Pub/Sub Integration Tests ==="

# Get pod names
PUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=publisher -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
SUB_POD=$(kubectl get pods -n "$NAMESPACE" -l app=subscriber -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$PUB_POD" ] || [ -z "$SUB_POD" ]; then
  echo "ERROR: Publisher or subscriber pod not found"
  exit 1
fi

# Test 1: Publisher can publish a message
echo "[Test 1] Publish message via /publish endpoint"
RESULT=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- \
  curl -s -X POST http://localhost:5000/publish \
  -H "Content-Type: application/json" \
  -d '{"order_id":"TEST-001","amount":42.00,"customer":"test-user"}' 2>/dev/null || echo "")

if echo "$RESULT" | grep -q '"status":"published"'; then
  pass "Message published successfully"
  MSG_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message_id',''))" 2>/dev/null || echo "")
else
  fail "Failed to publish message: $RESULT"
fi

# Wait for message delivery
sleep 3

# Test 2: Subscriber received the message (check logs)
echo "[Test 2] Subscriber received message"
SUB_LOGS=$(kubectl logs -n "$NAMESPACE" "$SUB_POD" -c subscriber --tail=20 2>/dev/null || echo "")
if echo "$SUB_LOGS" | grep -q "Received event"; then
  pass "Subscriber received event"
else
  fail "No received event in subscriber logs"
fi

# Test 3: Dapr subscription endpoint works
echo "[Test 3] Dapr subscription declaration"
SUBS=$(kubectl exec -n "$NAMESPACE" "$SUB_POD" -c subscriber -- \
  curl -s http://localhost:5000/dapr/subscribe 2>/dev/null || echo "")

if echo "$SUBS" | grep -q '"topic":"orders"'; then
  pass "Subscription declaration correct"
else
  fail "Subscription declaration invalid: $SUBS"
fi

# Test 4: Publish multiple messages
echo "[Test 4] Publish multiple messages"
SUCCESS_COUNT=0
for i in $(seq 1 5); do
  R=$(kubectl exec -n "$NAMESPACE" "$PUB_POD" -c publisher -- \
    curl -s -X POST http://localhost:5000/publish \
    -H "Content-Type: application/json" \
    -d "{\"order_id\":\"BATCH-$i\",\"amount\":$((i * 10))}" 2>/dev/null || echo "")
  if echo "$R" | grep -q '"status":"published"'; then
    ((SUCCESS_COUNT++))
  fi
done

if [ "$SUCCESS_COUNT" -eq 5 ]; then
  pass "All 5 batch messages published"
else
  fail "Only $SUCCESS_COUNT/5 batch messages published"
fi

# Summary
echo ""
echo "=== Results ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
[ "$FAILED" -gt 0 ] && exit 1
exit 0
