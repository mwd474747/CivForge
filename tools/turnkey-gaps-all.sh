#!/bin/bash
# Master turnkey: all gap closures + both lane packets.
# Usage: bash tools/turnkey-gaps-all.sh [--restart]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RESTART=false
if [[ "${1:-}" == "--restart" ]]; then
  RESTART=true
  bash tools/start-kernel-8080.sh
fi

echo "=== CivForge Turnkey Gaps All ==="

echo "--- Full unit test suite ---"
python3 -m pytest tests/ -q

echo "--- Full stack (auth + kernel + validate + OpenClaw probe) ---"
bash tools/turnkey-full-stack.sh --no-start

echo "--- Governance posture (OpenClaw CF-GOV-*, read-only) ---"
bash tools/turnkey-governance-posture.sh

echo "--- Cursor local executor (stateful gameplay) ---"
bash tools/turnkey-cursor-local.sh --advances 2

echo "--- OpenClaw escalation probe (read-only) ---"
bash tools/turnkey-openclaw-ops.sh --once

echo "=== Lane v2 turnkey complete ==="
echo "Grok swarm: grok.com + prompts/grok_swarm_handoff_seed.md"
echo "Cursor: docs/EXECUTION_LANE_V2.md"
echo "OpenClaw: docs/OPENCLAW_ESCALATION_PACKET_V1.md (escalation only)"
