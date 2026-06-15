#!/bin/bash
# Cursor local executor turnkey — verify CivForge after implementation.
# Usage: bash tools/turnkey-cursor-local.sh [--advances N] [--restart]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ADVANCES=2
RESTART=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --advances) ADVANCES="${2:-2}"; shift 2 ;;
    --restart) RESTART=true; shift ;;
    *) shift ;;
  esac
done

echo "=== CivForge Cursor Local Turnkey ==="
echo "Lane: docs/EXECUTION_LANE_V2.md (Cursor executes; Grok plans on grok.com)"

if $RESTART; then
  bash tools/start-kernel-8080.sh
fi

echo "1. Unit tests..."
python3 -m pytest tests/test_multi_agent_state.py tests/test_civstudy_metadata.py tests/test_civstudy_mechanics_bridge.py -q

echo "2. validate-game..."
bash tools/validate-game.sh

echo "3. MCP tools..."
python3 -c '
import json, subprocess
proc = subprocess.run(
    ["python3", "tools/mcp_server.py"],
    input="{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}\n",
    capture_output=True, text=True,
)
tools = json.loads(proc.stdout.strip().splitlines()[0])["result"]["tools"]
print("  tools:", len(tools))
'

echo "4. Advance $ADVANCES turns..."
for i in $(seq 1 "$ADVANCES"); do
  python3 tools/civforge_cli.py advance >/dev/null
  echo "  advance $i OK"
done

HEAD=$(git rev-parse --short HEAD)
echo "5. HEAD: $HEAD"
curl -sf http://127.0.0.1:8080/state | python3 -c '
import json, sys
d = json.load(sys.stdin)
print("  turn:", d.get("current_turn"), "fun:", d.get("fun_score"))
sim = d.get("civstudy_sim") or {}
print("  civstudy_sim:", sim.get("active_district"))
'

echo "=== Cursor local turnkey PASSED ==="
echo "Write execution receipt: receipts/cursor-execution-$(date +%Y%m%d-%H%M%S).md"
