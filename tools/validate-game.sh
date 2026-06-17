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
python3 -m pytest tests/ -q

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

# Deterministic probes: negotiate requires influence ≥2 on a fresh session.
post("/game/reset", {})
s = get("/state")
assert s["status"] == "active"
assert "mechanics_proposals" in s, "missing mechanics_proposals on /state"
assert "trust_erosion" in s, "missing trust_erosion on /state"
assert "victory_hud" in s, "missing victory_hud on /state"
assert len(s.get("map_tiles", [])) == 25
assert set((s.get("mechanics_lanes") or {}).keys()) == {"military", "economic", "cultural"}
cs = s.get("civstudy_reference", {})
for key in ("districts", "policy_tree", "discovery_forks", "cultural_event_chains"):
    assert key in cs, f"missing civstudy_reference.{key}"
sim = s.get("civstudy_sim", {})
assert "active_district" in sim, "missing civstudy_sim.active_district"
assert "policy_tree" in sim and "checklist" in sim["policy_tree"], "missing policy_tree.checklist (Block A)"
assert "commissioned_wonders" in sim, "missing civstudy_sim.commissioned_wonders (Block A)"
assert "cultural_path" in s.get("victory_progress", {}), "missing victory_progress.cultural_path (Block A)"
assert "work_pack_registry" in s, "missing work_pack_registry on /state"
assert s["work_pack_registry"].get("closed_block_a") is True, "Block A should be closed in registry"
assert s["work_pack_registry"]["blocks"]["block_b"]["status"] == "closed", "Block B should be closed in registry"
assert "player_agent" in s, "missing player_agent on /state (Block B)"
cat = s.get("action_catalog", {})
assert len(cat.get("wonders", [])) == 3, "expected 3 commissionable wonders in action_catalog"
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
for mech in (
    "civforge_propose_mechanics",
    "civforge_gate_mechanics",
    "civforge_apply_mechanics",
    "civforge_list_mechanics_proposals",
):
    assert mech in names, f"missing MCP tool {mech}"
assert "civforge_send_envoy" in names
assert len(names) == 17, f"expected 17 MCP tools, got {len(names)}"

# Block A route smoke (deterministic on fresh reset session)
post("/game/policy/branch", {"branch_id": "tradition"})
inf = get("/state")["player"]["resources"].get("influence", 0)
while inf < 10:
    post("/advance_turn")
    inf = get("/state")["player"]["resources"].get("influence", 0)
post("/game/wonder/commission", {"wonder_id": "wonder-oracle"})
s2 = get("/state")
assert len(s2["civstudy_sim"]["commissioned_wonders"]) >= 1

# Block B route smoke
post("/game/competition/mode", {"mode": "pva_duel"})
post("/game/competition/autoplay/start")
st = get("/game/competition/status")
assert st.get("mode") == "pva_duel"
assert st.get("autoplay", {}).get("active") is True
post("/game/player/strategy", {"strategy": "science"})
s3 = get("/state")
assert s3["player_agent"]["strategy"] == "science"

# Block C probes
ms = get("/game/mechanics/status")
assert "registry_modules" in ms
assert "diplomacy_layer" in ms["registry_modules"]
assert ms["tick_order"] == "mechanics_first_then_alternate_victory_then_milestones"
s4 = get("/state")
assert "domination_path" in s4.get("victory_progress", {}), "missing victory_progress.domination_path (Block C)"
assert s4["work_pack_registry"].get("closed_block_c") is True, "Block C should be closed in registry"

# Block D auth probes
auth = get("/game/auth/status")
assert "auth_base" in auth
assert auth["auth_base"].endswith("8081")
assert "identity_auth_enabled" in auth
assert "auth_audience" in auth or "mutator_scopes" in auth

# Block E auth consumer probes (dashboard + shared headers module)
from pathlib import Path
html = Path("frontend/index.html").read_text(encoding="utf-8")
assert "civforge_auth_token" in html and "authFetch" in html
assert Path("backend/civforge_auth_headers.py").is_file()
assert Path("tools/start-auth-8081.sh").is_file()

assert s4["work_pack_registry"].get("closed_block_e") is True
assert s4["work_pack_registry"].get("closed_block_d") is True
assert s4["work_pack_registry"].get("grok_handoff_pack") == "receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md"
print("  API + MCP + Block A + B + C + D + E probes OK")
PY

if $READ_ONLY; then
  echo "4. Skipping turnkey multi-ui (read-only — no turn advances)"
else
  echo "4. Turnkey multi-ui (advances turns — see docs/CIVFORGE_SWARM_CLASS_V1.md)..."
  bash tools/turnkey-multi-ui-full.sh
fi

echo "=== validate-game PASSED ==="
echo "Dashboard: http://127.0.0.1:8080/dashboard"
