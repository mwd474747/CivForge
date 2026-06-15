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

echo "--- Unit tests (mechanics + civstudy) ---"
python3 -m pytest tests/test_civstudy_metadata.py tests/test_civstudy_mechanics_bridge.py tests/test_multi_agent_state.py -q

echo "--- Cursor local executor ---"
bash tools/turnkey-cursor-local.sh --advances 2

echo "--- OpenClaw escalation probe (read-only) ---"
bash tools/turnkey-openclaw-ops.sh --once

echo "=== Lane v2 turnkey complete ==="
echo "Grok swarm: grok.com + prompts/grok_swarm_handoff_seed.md"
echo "Cursor: docs/EXECUTION_LANE_V2.md"
echo "OpenClaw: docs/OPENCLAW_ESCALATION_PACKET_V1.md (escalation only)"
