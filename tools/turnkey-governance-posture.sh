#!/bin/bash
# OpenClaw CF-GOV-* governance posture turnkey (read-only by default).
#
# Implements the validated OpenClaw proposal:
#   CF-GOV-POSTURE-001, CF-CONTRACT-PARITY-002, CF-GOV-RECEIPTS-003,
#   CF-POLLER-POSTURE-004, CF-EXPOSURE-GUARD-005
#
# Default: no turn advances. Use --with-gameplay to run full validate-game.
#
# Usage:
#   bash tools/turnkey-governance-posture.sh
#   bash tools/turnkey-governance-posture.sh --with-gameplay
#   bash tools/turnkey-governance-posture.sh --restart
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RESTART=false
WITH_GAMEPLAY=false
for arg in "$@"; do
  case "$arg" in
    --restart) RESTART=true ;;
    --with-gameplay) WITH_GAMEPLAY=true ;;
  esac
done

echo "=== CivForge Governance Posture Turnkey (OpenClaw CF-GOV-*) ==="
echo "Lane: read-only posture + parity (see docs/CIVFORGE_SWARM_CLASS_V1.md)"

if $RESTART; then
  bash tools/start-kernel-8080.sh
fi

echo "1. Kernel probe (no advance)..."
curl -sf http://127.0.0.1:8080/state >/tmp/civforge-gov-posture-state.json \
  || { echo "8080 not live — run: bash tools/start-kernel-8080.sh"; exit 1; }
python3 -c '
import json
d = json.load(open("/tmp/civforge-gov-posture-state.json"))
print("  turn:", d.get("current_turn", d.get("turn")))
print("  fun:", d.get("fun_score"))
print("  status:", d.get("status"))
'

echo "2. Governance tool pytest..."
python3 -m pytest tests/test_civforge_governance_tools.py -q

echo "3. Contract parity..."
python3 tools/civforge_contract_parity.py

echo "4. Poller posture..."
python3 tools/civforge_poller_posture.py

echo "5. Receipt index..."
python3 tools/civforge_receipt_index.py

echo "6. Composite governance posture..."
python3 tools/civforge_governance_posture.py

if $WITH_GAMEPLAY; then
  echo "7. Full validate-game (stateful — advances turns)..."
  bash tools/validate-game.sh
else
  echo "7. Read-only validate-game (no turn advances)..."
  bash tools/validate-game.sh --read-only
fi

HEAD=$(git rev-parse --short HEAD)
STAMP=$(date -u +%Y%m%d-%H%M%S)
RECEIPT="receipts/openclaw-governance-turnkey-${STAMP}.md"
mkdir -p receipts
cat >"$RECEIPT" <<EOF
# OpenClaw Governance Turnkey Run
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**HEAD:** \`${HEAD}\`
**Label:** prototype-only (CivForge local — not dawsOS promotion truth)
**Proposal:** CF-GOV-POSTURE-001 … CF-EXPOSURE-GUARD-005 (closed)

## Mode
- gameplay_advances: $($WITH_GAMEPLAY && echo true || echo false)

## Posture artifacts
- receipts/civforge-governance-posture-latest.json
- receipts/civforge-contract-parity-latest.json
- receipts/civforge-poller-posture-latest.json
- receipts/civforge-receipt-index-latest.json

## Turnkey
\`bash tools/turnkey-governance-posture.sh\` (default read-only)
EOF

echo "8. Receipt: $RECEIPT"
echo "=== Governance posture turnkey PASSED ==="
echo "HEAD: $HEAD"
