#!/usr/bin/env bash
set -euo pipefail

# Comprehensive Deployment Validation Script
# Validates all aspects of the Dapr microservices deployment

NAMESPACE="${NAMESPACE:-dapr-demo}"
DAPR_NAMESPACE="${DAPR_NAMESPACE:-dapr-system}"
PASSED=0
FAILED=0
WARNINGS=0

pass()    { echo "  [PASS]    $1"; ((PASSED++)); }
fail()    { echo "  [FAIL]    $1"; ((FAILED++)); }
warn()    { echo "  [WARN]    $1"; ((WARNINGS++)); }
section() { echo ""; echo "=== $1 ==="; }

echo "============================================"
echo " Dapr Microservices Deployment Validation"
echo " Namespace: $NAMESPACE"
echo " Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================"

# ---- Section 1: Cluster Connectivity ----
section "1. Cluster Connectivity"

if kubectl cluster-info &>/dev/null; then
  pass "Connected to Kubernetes cluster"
else
  fail "Cannot connect to Kubernetes cluster"
  echo "FATAL: Cannot proceed without cluster access"
  exit 1
fi

# ---- Section 2: Dapr System Components ----
section "2. Dapr System Components"

DAPR_PODS=$(kubectl get pods -n "$DAPR_NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$DAPR_PODS" -gt 0 ]; then
  pass "Dapr system pods found ($DAPR_PODS pods)"
else
  fail "No Dapr system pods found in $DAPR_NAMESPACE"
fi

for component in dapr-operator dapr-sidecar-injector dapr-sentry dapr-placement-server; do
  STATUS=$(kubectl get pods -n "$DAPR_NAMESPACE" -l app="$component" -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
  if [ "$STATUS" = "Running" ]; then
    pass "$component is running"
  else
    fail "$component status: $STATUS"
  fi
done

# ---- Section 3: Application Namespace ----
section "3. Application Namespace"

if kubectl get namespace "$NAMESPACE" &>/dev/null; then
  pass "Namespace '$NAMESPACE' exists"
else
  fail "Namespace '$NAMESPACE' not found"
fi

# ---- Section 4: Application Pods ----
section "4. Application Pods"

for svc in publisher subscriber; do
  POD=$(kubectl get pods -n "$NAMESPACE" -l app="$svc" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
  if [ -z "$POD" ]; then
    fail "$svc pod not found"
    continue
  fi

  PHASE=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
  if [ "$PHASE" = "Running" ]; then
    pass "$svc pod is running"
  else
    fail "$svc pod status: $PHASE"
  fi

  # Check container count (should be 2: app + dapr sidecar)
  READY=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[*].ready}')
  CONTAINERS=$(echo "$READY" | wc -w)
  READY_COUNT=$(echo "$READY" | tr ' ' '\n' | grep -c "true" || echo "0")

  if [ "$CONTAINERS" -ge 2 ] && [ "$READY_COUNT" -ge 2 ]; then
    pass "$svc has $READY_COUNT/$CONTAINERS containers ready (Dapr sidecar injected)"
  else
    fail "$svc has $READY_COUNT/$CONTAINERS containers ready"
  fi
done

# ---- Section 5: Dapr Components ----
section "5. Dapr Components"

COMPONENTS=$(kubectl get components -n "$NAMESPACE" --no-headers 2>/dev/null || echo "")
if [ -n "$COMPONENTS" ]; then
  COMP_COUNT=$(echo "$COMPONENTS" | wc -l)
  pass "Found $COMP_COUNT Dapr components"
  echo "$COMPONENTS" | while read -r line; do
    NAME=$(echo "$line" | awk '{print $1}')
    echo "    - $NAME"
  done
else
  warn "No Dapr components found"
fi

# ---- Section 6: Services ----
section "6. Kubernetes Services"

for svc in publisher subscriber; do
  if kubectl get svc "$svc" -n "$NAMESPACE" &>/dev/null; then
    pass "Service '$svc' exists"
  else
    fail "Service '$svc' not found"
  fi
done

# ---- Section 7: Health Checks ----
section "7. Service Health Checks"

for svc in publisher subscriber; do
  POD=$(kubectl get pods -n "$NAMESPACE" -l app="$svc" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
  if [ -z "$POD" ]; then
    fail "Cannot check $svc health - pod not found"
    continue
  fi

  HEALTH=$(kubectl exec -n "$NAMESPACE" "$POD" -c "$svc" -- curl -s http://localhost:5000/health 2>/dev/null || echo "")
  if echo "$HEALTH" | grep -q '"status"'; then
    pass "$svc /health endpoint responds"
  else
    fail "$svc /health endpoint not responding"
  fi
done

# ---- Section 8: RBAC ----
section "8. RBAC Configuration"

if kubectl get clusterrole dapr-demo-role &>/dev/null || kubectl get role -n "$NAMESPACE" --no-headers 2>/dev/null | grep -q .; then
  pass "RBAC roles configured"
else
  warn "No custom RBAC roles found (may use defaults)"
fi

# ---- Section 9: Network Policies ----
section "9. Network Policies"

NP_COUNT=$(kubectl get networkpolicies -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
if [ "$NP_COUNT" -gt 0 ]; then
  pass "Found $NP_COUNT network policies"
else
  warn "No network policies found"
fi

# ---- Section 10: Security Check ----
section "10. Security Validation"

# Check for secrets in environment variables
for svc in publisher subscriber; do
  POD=$(kubectl get pods -n "$NAMESPACE" -l app="$svc" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
  if [ -z "$POD" ]; then continue; fi

  ENV_VARS=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[0].env[*].name}' 2>/dev/null || echo "")
  if echo "$ENV_VARS" | grep -qi "password\|secret\|key\|token" 2>/dev/null; then
    warn "$svc has env vars that may contain secrets - verify they use secretKeyRef"
  else
    pass "$svc has no plaintext secret env vars"
  fi
done

# ---- Summary ----
echo ""
echo "============================================"
echo " Validation Summary"
echo "============================================"
echo " Passed:   $PASSED"
echo " Failed:   $FAILED"
echo " Warnings: $WARNINGS"
echo "============================================"

if [ "$FAILED" -gt 0 ]; then
  echo " RESULT: FAIL"
  exit 1
else
  echo " RESULT: PASS"
  exit 0
fi
