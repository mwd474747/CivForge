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

echo "--- Grok swarm packet ---"
bash tools/turnkey-grok-play.sh --advances 2

echo "--- OpenClaw ops packet ---"
bash tools/turnkey-openclaw-ops.sh --once

echo "=== All turnkey packets exercised ==="
echo "OpenClaw: docs/OPENCLAW_OPS_PACKET_V1.md + receipts/work-pack-openclaw-civforge-ops-001.md"
echo "Grok:     docs/GROK_SWARM_PACKET_V1.md + receipts/work-pack-grok-mechanics-sim-001.md"
