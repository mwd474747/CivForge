#!/bin/bash
# OpenClaw turnkey ops packet — retired-Nexus guard, wt probes, receipt scaffold.
# Usage: bash tools/turnkey-openclaw-ops.sh
# Label: prototype-only until OpenClaw refreshes wt receipts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RECEIPT_OUT="receipts/openclaw-ops-run-$(date +%Y%m%d-%H%M%S).md"
WT_ROOT="${DAWSCO_WORKSPACE_ROOT:-$HOME/.openclaw/dawsos-workspace-wt}"

echo "=== CivForge OpenClaw Ops Turnkey ==="

echo "1. Kernel :8080..."
curl -sf http://127.0.0.1:8080/state >/tmp/civforge-openclaw-state.json \
  || { echo "Start kernel: bash tools/start-kernel-8080.sh"; exit 1; }
python3 -c '
import json
d = json.load(open("/tmp/civforge-openclaw-state.json"))
print("  turn:", d.get("current_turn"), "fun:", d.get("fun_score"))
sim = d.get("civstudy_sim") or {}
print("  civstudy_sim:", sim.get("active_district"), "forks:", len(sim.get("unlocked_forks", [])))
'

echo "2. dawsos-auth :8081..."
if curl -sf http://127.0.0.1:8081/health >/tmp/dawsos-auth-health.json 2>/dev/null; then
  python3 -c 'import json; d=json.load(open("/tmp/dawsos-auth-health.json")); print("  auth:", d.get("service", d.get("status")), d.get("version", ""))'
  AUTH_OK=true
else
  echo "  WARN: 8081 not live — bash tools/start-auth-8081.sh"
  AUTH_OK=false
fi

echo "3. Retired Nexus :8082 guard..."
if curl -sf http://127.0.0.1:8082/api/health >/tmp/nexus-health.json; then
  echo "  FAIL: retired :8082 endpoint unexpectedly responded"
  NEXUS_DARK=false
else
  echo "  OK: :8082 is dark as required"
  NEXUS_DARK=true
fi

echo "4. wt probe pointers (read-only)..."
for f in \
  "reports/ops/dawsos-projection-pipeline-receipt-latest.json" \
  "reports/ops/workflow-dispatch-health-probe-latest.json" \
  "reports/ops/integration-http-probes-latest.json"
do
  if [[ -f "$WT_ROOT/$f" ]]; then
    echo "  OK $f"
  else
    echo "  MISSING $f (OpenClaw refresh)"
  fi
done
REGISTRY="$WT_ROOT/engine-src/active/config/ops/governed-connectors-registry.v1.json"
if [[ -f "$REGISTRY" ]]; then
  echo "  OK engine-src/active/config/ops/governed-connectors-registry.v1.json"
  python3 -c "
import json
r = json.load(open('$REGISTRY'))
items = r if isinstance(r, list) else r.get('connectors', r.get('entries', []))
if not isinstance(items, list):
    items = [v for v in r.values() if isinstance(v, list)]
    items = items[0] if items else []
row = next((x for x in items if isinstance(x, dict) and x.get('id') == 'civforge_kernel'), None)
print('  civforge_kernel:', row.get('status', 'found') if row else 'NOT FOUND')
" 2>/dev/null || true
else
  echo "  MISSING engine-src/active/config/ops/governed-connectors-registry.v1.json"
fi

echo "5. Boundary contract mirror check..."
if [[ -f "$WT_ROOT/engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md" ]]; then
  echo "  wt mirror present"
else
  echo "  wt mirror missing — apply docs/OPENCLAW_WT_APPLY_PACKET_V1.md"
fi

mkdir -p receipts
cat >"$RECEIPT_OUT" <<EOF
# OpenClaw CivForge Ops Run
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Label:** prototype-only (CivForge execution receipt — not dawsOS promotion truth)

## Probes
- kernel_8080: ok
- auth_8081: $($AUTH_OK && echo ok || echo blocked)
- retired_nexus_8082: $($NEXUS_DARK && echo dark || echo unexpectedly_live)

## OpenClaw status (post WP-001 closure)
1. Retired Nexus guard: :8082 must remain dark; the CivForge poller/client are retired.
2. wt registry canon: \`engine-src/active/config/ops/governed-connectors-registry.v1.json\`
3. wt boundary: pointer-only mirror (do not overwrite full contract without approval)
4. Vercel: \`vercel --prod\` when frontend changes approved

## Canonical docs
- docs/OPENCLAW_OPS_PACKET_V1.md
- docs/OPENCLAW_WT_APPLY_PACKET_V1.md
- receipts/work-pack-openclaw-civforge-ops-001.md
EOF

echo "6. Receipt scaffold: $RECEIPT_OUT"
echo "=== OpenClaw ops turnkey complete ==="

$NEXUS_DARK
