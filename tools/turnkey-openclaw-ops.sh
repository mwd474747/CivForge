#!/bin/bash
# OpenClaw turnkey ops packet — Nexus :8082, poller, wt probes, receipt scaffold.
# Usage: bash tools/turnkey-openclaw-ops.sh [--once|--daemon]
# Label: prototype-only until OpenClaw refreshes wt receipts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:---once}"
KEY_FILE="${HOME}/.openclaw/runtime/nexus-satellite-api-keys.json"
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

echo "2. Nexus :8082 health..."
if curl -sf http://127.0.0.1:8082/api/health >/tmp/nexus-health.json; then
  python3 -c 'import json; d=json.load(open("/tmp/nexus-health.json")); print("  nexus:", d.get("status", d))'
  NEXUS_OK=true
else
  echo "  WARN: 8082 not live — OpenClaw must start dawsos-nexus on this Mac"
  NEXUS_OK=false
fi

echo "3. Satellite API key..."
if [[ -f "$KEY_FILE" ]]; then
  python3 -c "
import json
k = json.load(open('$KEY_FILE'))
print('  civforge-kernel key:', 'present' if 'civforge-kernel' in k else 'MISSING')
"
  KEY_OK=true
else
  echo "  WARN: missing $KEY_FILE"
  KEY_OK=false
fi

echo "4. Poller..."
if $KEY_OK && $NEXUS_OK; then
  export NEXUS_URL="${NEXUS_URL:-http://127.0.0.1:8082}"
  export NEXUS_API_KEY
  NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$KEY_FILE'))['civforge-kernel']['apiKey'])")"
  if [[ "$MODE" == "--daemon" ]]; then
    bash tools/start-poller-daemon.sh
  else
    python3 tools/nexus_command_poller.py --once || true
  fi
  POLLER_OK=true
else
  echo "  SKIP poller (prereqs missing)"
  POLLER_OK=false
fi

echo "5. wt probe pointers (read-only)..."
for f in \
  "reports/ops/dawsos-projection-pipeline-receipt-latest.json" \
  "reports/ops/workflow-dispatch-health-probe-latest.json" \
  "engine-src/active/config/governed-connectors-registry.v1.json"
do
  if [[ -f "$WT_ROOT/$f" ]]; then
    echo "  OK $f"
  else
    echo "  MISSING $f (OpenClaw refresh)"
  fi
done

echo "6. Boundary contract mirror check..."
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
- nexus_8082: $($NEXUS_OK && echo ok || echo blocked)
- api_key: $($KEY_OK && echo ok || echo blocked)
- poller: $($POLLER_OK && echo exercised || echo skipped)

## OpenClaw next (authority lane)
1. Sustained dawsos-nexus on :8082 + register civforge-kernel if missing
2. Poller daemon: \`bash tools/start-poller-daemon.sh\`
3. wt: mirror \`docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md\` + governed-connectors-registry row
4. Refresh wt receipts per partner-lane packet
5. Vercel redeploy after frontend changes: \`vercel --prod\` from CivForge root

## Canonical docs
- docs/OPENCLAW_OPS_PACKET_V1.md
- docs/OPENCLAW_WT_APPLY_PACKET_V1.md
- receipts/work-pack-openclaw-civforge-ops-001.md
EOF

echo "7. Receipt scaffold: $RECEIPT_OUT"
echo "=== OpenClaw ops turnkey complete ==="
