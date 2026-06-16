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

echo "1. Truth anchor + shell hygiene..."
bash tools/verify-truth-anchor.sh
bash tools/check-agent-shell-hygiene.sh || {
  echo "  WARN: stale Cursor wrapper shells — bash tools/check-agent-shell-hygiene.sh --kill"
}

echo "2. validate-game (full pytest + API probes)..."
bash tools/validate-game.sh --read-only

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
assert len(tools) == 17, "expected 17 MCP tools"
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
print("  player_agent:", (d.get("player_agent") or {}).get("strategy"))
print("  block_b:", (d.get("work_pack_registry") or {}).get("blocks", {}).get("block_b", {}).get("status"))
sim = d.get("civstudy_sim") or {}
print("  civstudy_sim:", sim.get("active_district"))
'

echo "=== Cursor local turnkey PASSED ==="
echo "Write execution receipt: receipts/cursor-execution-$(date +%Y%m%d-%H%M%S).md"
