#!/bin/bash
# Grok swarm turnkey play + verify packet.
# Usage: bash tools/turnkey-grok-play.sh [--advances N]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ADVANCES=3
if [[ "${1:-}" == "--advances" && -n "${2:-}" ]]; then
  ADVANCES="$2"
fi

echo "=== CivForge Grok Swarm Turnkey ==="

echo "1. Forbidden-pattern guard..."
if python3 tools/civforge_cli.py status 2>/dev/null | grep -qi vercel; then
  echo "  NOTE: status may mention vercel — do NOT use 'grep vercel' as sole proof"
fi
echo "  OK: use validate-game.sh + dashboard curl instead"

echo "2. validate-game (no restart)..."
bash tools/validate-game.sh

echo "3. MCP tools list..."
python3 -c '
import json, subprocess
proc = subprocess.run(
    ["python3", "tools/mcp_server.py"],
    input="{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}\n",
    capture_output=True, text=True,
)
tools = json.loads(proc.stdout.strip().splitlines()[0])["result"]["tools"]
names = {t["name"] for t in tools}
required = {
    "civforge_status", "civforge_advance_turn", "civforge_negotiate_respond",
    "civforge_governance_propose", "civforge_governance_gate",
}
missing = required - names
assert not missing, f"missing MCP tools: {missing}"
print("  MCP tools:", len(names), "including governance propose/gate")
'

echo "4. Advance $ADVANCES turns..."
for i in $(seq 1 "$ADVANCES"); do
  python3 tools/civforge_cli.py advance >/dev/null
  echo "  advance $i OK"
done

echo "5. CivStudy sim post-advance..."
python3 -c '
import json, urllib.request
with urllib.request.urlopen("http://127.0.0.1:8080/state") as r:
    d = json.loads(r.read())
sim = d.get("civstudy_sim") or {}
assert "active_district" in sim, "civstudy_sim missing"
print("  district:", sim["active_district"], "recent:", len(sim.get("recent", [])))
vp = d.get("victory_progress") or {}
if vp.get("outcome") == "victory":
    print("  game outcome: VICTORY")
'

echo "6. Dashboard smoke..."
curl -sf http://127.0.0.1:8080/dashboard | grep -q "Multi-Agent Command"
echo "  dashboard HTML OK"

echo "=== Grok turnkey complete ==="
echo "Play: http://127.0.0.1:8080/dashboard"
echo "Remote: https://civforge.vercel.app?api_base=<HTTPS_TUNNEL_TO_8080>"
echo "Packet: docs/GROK_SWARM_PACKET_V1.md"
