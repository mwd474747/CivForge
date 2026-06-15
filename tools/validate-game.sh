#!/bin/bash
# Full CivForge game validation: unit tests + live kernel probes + turnkey.
#
# STATEFUL: default mode runs turnkey-multi-ui-full.sh which advances turns via CLI.
# For architecture/report-only review use --read-only (skips turn advances).
#
# Usage: bash tools/validate-game.sh [--restart] [--read-only]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RESTART=false
READ_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --restart) RESTART=true ;;
    --read-only) READ_ONLY=true ;;
  esac
done

echo "=== CivForge validate-game ==="

if $RESTART; then
  echo "1. Restart kernel on :8080..."
  bash tools/start-kernel-8080.sh
else
  echo "1. Kernel health check..."
  curl -sf http://127.0.0.1:8080/state >/tmp/civforge-validate-state.json \
    || { echo "8080 not live — run: bash tools/start-kernel-8080.sh"; exit 1; }
fi

echo "2. Unit tests..."
python3 -m pytest tests/test_multi_agent_state.py tests/test_civstudy_metadata.py tests/test_civstudy_mechanics_bridge.py -q

echo "3. API contract probes..."
python3 <<'PY'
import json, subprocess, urllib.request

KERNEL = "http://127.0.0.1:8080"

def get(path):
    with urllib.request.urlopen(f"{KERNEL}{path}", timeout=15) as r:
        return json.loads(r.read())

def post(path, body=None):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        f"{KERNEL}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

s = get("/state")
assert s["status"] == "active"
assert len(s.get("map_tiles", [])) == 25
assert set((s.get("mechanics_lanes") or {}).keys()) == {"military", "economic", "cultural"}
cs = s.get("civstudy_reference", {})
for key in ("districts", "policy_tree", "discovery_forks", "cultural_event_chains"):
    assert key in cs, f"missing civstudy_reference.{key}"
sim = s.get("civstudy_sim", {})
assert "active_district" in sim, "missing civstudy_sim.active_district"
vp = s.get("victory_progress", {})
if vp.get("joint_progress", 0) >= vp.get("target", 100):
    assert vp["milestones"][3]["done"] is True, "Joint victory milestone should sync at 100%"

n1 = post("/game/negotiate", {"to": "harper", "offer": "validate A"})
n2 = post("/game/negotiate", {"to": "harper", "offer": "validate B"})
assert n1["negotiation"]["id"] != n2["negotiation"]["id"]

proc = subprocess.run(
    ["python3", "tools/mcp_server.py"],
    input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
    capture_output=True, text=True, cwd=".",
)
tools = json.loads(proc.stdout.strip().splitlines()[0])["result"]["tools"]
names = {t["name"] for t in tools}
assert "civforge_negotiate_respond" in names
assert "civforge_governance_propose" in names
assert "civforge_governance_gate" in names
print("  API + MCP probes OK")
PY

if $READ_ONLY; then
  echo "4. Skipping turnkey multi-ui (read-only — no turn advances)"
else
  echo "4. Turnkey multi-ui (advances turns — see docs/CIVFORGE_SWARM_CLASS_V1.md)..."
  bash tools/turnkey-multi-ui-full.sh
fi

echo "=== validate-game PASSED ==="
echo "Dashboard: http://127.0.0.1:8080/dashboard"
