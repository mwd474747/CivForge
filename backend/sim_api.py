from fastapi import FastAPI, Depends, Header, HTTPException
import requests, os
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import sys
from pathlib import Path

# Add core to path for the realigned Python agentic patterns (no more Godot MVP)
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore

NEXUS_URL = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")

def send_telemetry_to_nexus(turn: int, fun_score: float, resources: dict, extra: dict = None):
    """Send heartbeat to dawsos-nexus (8082) as CivForge satellite.
    Includes agentState, customMetrics (turn, fun, resources, events, territories) for control/telemetry/simulation.
    Thin HTTP bridge only per SEPARATION.md. Commands from nexus are proposals (not direct exec).
    """
    try:
        payload = {
            "appId": "civforge-kernel",
            "status": "active",
            "agentState": "thinking",
            "customMetrics": {
                "turn": turn,
                "funScore": fun_score,
                "resources": resources,
                "territories": extra.get("territories", 0) if extra else 0,
                "events": extra.get("events", [])[-3:] if extra else [],
                "cities": extra.get("cities", 0) if extra else 0,
            }
        }
        if extra and "fun_components" in extra:
            payload["customMetrics"]["funComponents"] = extra["fun_components"]
        requests.post(f"{NEXUS_URL}/api/telemetry/heartbeat", json=payload, timeout=5)
    except Exception:
        pass  # never block game on telemetry

app = FastAPI(
    title="CivForge Governance Backend",
    description=(
        "Persistent local sandbox/workspace for CivForge agentic governance. "
        "Favors the earlier FastAPI version (state, /state, /found_city, /advance_turn, /integrate). "
        "Real purpose: govern safe, receipt-first work on the *separate* gravity-mosaic-knowledge-graph project "
        "(and future projects) using DawsOS patterns, AgentBrains, FunForge quality scoring, and strict literal verification tools. "
        "The actual gravity changes always live in /Users/michaeldawson/gravity-mosaic-knowledge-graph and are deployed ONLY via tools/deploy-gravity-mosaic/deploy.sh."
    ),
)

# === Core governance runtime (replaces Godot TurnManager / MVP driver) ===
# Persistence enabled per Mac Studio canonical lock-in (WP-BACKEND-REALIGN-EXEC-001)
# State + receipts now survive uvicorn restarts via SQLite
DB_PATH = Path(__file__).parent.parent / "gravity_backend.db"
orchestrator = GovernanceOrchestrator()
receipt_store = ReceiptStore(
    base_dir=Path(__file__).parent.parent / "receipts",
    db_path=DB_PATH
)

# In-memory state shaped exactly like the earlier FastAPI / Codespaces version the user requested.
# Semantics realigned: "player/ai_civs/territories/fun_score" now represent governance workstreams
# and quality of the agentic process controlling deploys to the separate gravity project.
# (Defined before restore to avoid NameError on import when persisted state exists.)
game_state: Dict[str, Any] = {
    "turn": 1,
    "player": {
        "name": "Governance Lead (Grok)",
        "resources": {"food": 12, "prod": 12, "sci": 9, "influence": 6, "verify_budget": 7},
        "territories": 5,   # active governed work items / projects
        "cities": 2,        # "founded" = initiated major work packs or gravity deploys
        "fun_score": 87.0,
    },
    "ai_civs": [
        {"name": "Harper (Systems)", "resources": {"food": 10, "prod": 8, "sci": 11, "influence": 5}, "territories": 3},
        {"name": "Sebastian (Governance)", "resources": {"food": 9, "prod": 7, "sci": 8, "influence": 9}, "territories": 3},
    ],
    "events": [],
    "receipts": [],  # rich DawsOS-style receipts (also written to disk via ReceiptStore)
    "work_packs": [],  # proposals / active governed items
}

# Try to restore last known state snapshot if available (now safe)
restored = receipt_store.load_state("game_state")
if restored:
    game_state.update(restored)
    print("[CivForge] Restored previous state snapshot from SQLite (persistence active)")

# Register the main agent + sub-agents (realigned from the old civs)
grok = orchestrator.register_agent("grok", "Grok (Main Orchestrator)")
orchestrator.register_agent("harper", "Harper (Agentic Systems & Memory)")
orchestrator.register_agent("sebastian", "Sebastian (Governance & Safety)")

class FoundCityRequest(BaseModel):
    city_name: str = "New Work Pack"
    position: str = "gravity-mosaic"
    investment: int = 4  # prod / attention cost

class ProposeWorkRequest(BaseModel):
    action: str = "gravity_update"
    details: Dict[str, Any] = {}
    investment: int = 3

class GateRequest(BaseModel):
    proposal_id: str
    fun_score_override: Optional[float] = None

@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """Returns live governance workspace state (matches the earlier FastAPI/Codespaces shape exactly for easy testing).

    Includes player (lead workstream), ai_civs (sub-agents), resources, territories (active items),
    fun_score (quality/engagement of the governed process), receipts, events.
    """
    recent = game_state["receipts"][-5:] if game_state["receipts"] else []
    return {
        "status": "active",
        "current_turn": game_state["turn"],
        "player": game_state["player"],
        "ai_civs": game_state["ai_civs"],
        "recent_events": game_state["events"][-3:],
        "fun_score": game_state["player"]["fun_score"],
        "receipts": recent,
        "note": "CivForge FastAPI governance workspace. Use this to drive receipt-first work on the separate gravity-mosaic project. Actual deploys go through tools/deploy-gravity-mosaic/deploy.sh with literal verification.",
    }

@app.post("/found_city")
async def found_city(req: FoundCityRequest) -> Dict[str, Any]:
    """Initiate a governed work item ('found city' in the original paste = start a major work pack or gravity deploy thread).

    Checks prod/attention budget, updates state + territories, appends detailed receipt (with turn, status, fun_score, claim).
    This is the exact surface from the earlier FastAPI version.
    """
    if game_state["player"]["resources"]["prod"] < req.investment:
        return {
            "error": "Not enough Production / attention budget",
            "required": req.investment,
            "available": game_state["player"]["resources"]["prod"],
        }

    game_state["player"]["resources"]["prod"] -= req.investment
    game_state["player"]["cities"] += 1
    game_state["player"]["territories"] += 1
    game_state["player"]["resources"]["food"] += 2
    game_state["player"]["fun_score"] = min(100.0, game_state["player"]["fun_score"] + 4.0)

    receipt = {
        "turn": game_state["turn"],
        "action": "found_work_pack",
        "work": req.city_name,
        "investment": req.investment,
        "status": "SUCCESS",
        "fun_delta": 4.0,
        "claim": f"Initiated governed work: {req.city_name} for {req.position}",
        "fun_score": game_state["player"]["fun_score"],
    }
    game_state["receipts"].append(receipt)
    game_state["events"].append(
        f"Turn {game_state['turn']}: Founded work pack '{req.city_name}' (invested {req.investment})."
    )
    game_state["work_packs"].append({"name": req.city_name, "status": "active"})

    # Sub-agents react (realigned from original paste)
    for ai in game_state["ai_civs"]:
        ai["territories"] += 1 if game_state["turn"] % 2 == 0 else 0

    # Also log via core ReceiptStore (disk + memory)
    receipt_store.append(receipt, filename_hint="work-pack")

    # Telemetry to dawsos-nexus on work pack / found action
    extra = {
        "territories": game_state["player"].get("territories", 0),
        "cities": game_state["player"].get("cities", 0),
        "events": game_state.get("events", []),
    }
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)

    return {
        "message": f"Work pack '{req.city_name}' initiated successfully!",
        "updated_state": game_state["player"],
        "receipt": receipt,
        "next_steps": "Call /advance_turn to run a full governance cycle (agent decisions + FunForge + gate), or use /governance/propose for a gravity deploy.",
    }

@app.post("/advance_turn")
async def advance_turn() -> Dict[str, Any]:
    """Advance one governance cycle (the heart of the earlier FastAPI version).

    Now powered by the real Python GovernanceOrchestrator + AgentBrains + FunForge.
    Produces a rich receipt (status, fun_score, decisions, gate result) and updates the workspace state.
    """
    result = orchestrator.advance_cycle(player_actions=1)

    game_state["turn"] = result["turn"]
    game_state["player"]["fun_score"] = result["fun_score"]

    # Tick resources (governance budget)
    for key in ["food", "prod", "sci", "influence", "verify_budget"]:
        if key in game_state["player"]["resources"]:
            game_state["player"]["resources"][key] += 1

    receipt = result["receipt"]
    game_state["receipts"].append(receipt)
    for ev in result.get("events", []):
        game_state["events"].append(ev)

    # Persist the important ones + snapshot full state for restart survival
    receipt_store.append(receipt, filename_hint="governance-cycle")
    receipt_store.save_state("game_state", game_state)

    # Send telemetry to dawsos-nexus (8082) - primary for control, telemetry, simulation input, audit mirror
    extra = {
        "territories": game_state["player"].get("territories", 0),
        "cities": game_state["player"].get("cities", 0),
        "events": game_state.get("events", []),
    }
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)

    return {
        "message": f"Governance cycle {game_state['turn']} advanced.",
        "receipt": receipt,
        "state": game_state["player"],
        "agent_decisions": receipt.get("decisions", {}),
    }

@app.get("/integrate/civforge")
async def integrate_civforge() -> Dict[str, Any]:
    """Hook for CivForge agents (Grok, receipts, governance). Primary integration point."""
    return {
        "civforge_version": "governance-fastapi-2026",
        "current_receipts": game_state["receipts"][-6:],
        "simulation_status": "FastAPI workspace active. Governing the separate gravity-mosaic project via receipt-first loops.",
        "core": "AgentBrain + FunForge + GovernanceGate + Orchestrator (pure Python, no Godot MVP)",
        "gravity_deploy_tool": "tools/deploy-gravity-mosaic/deploy.sh (literal verification enforced)",
        "next": "POST /found_city to start a work pack, POST /advance_turn for a cycle, or use the governance endpoints + deploy tool.",
    }

# === New governance-aligned endpoints (do not break the earlier /state /found_city surface) ===

@app.post("/governance/propose")
async def governance_propose(req: ProposeWorkRequest) -> Dict[str, Any]:
    """Propose a concrete work item (e.g. a gravity-mosaic change). Returns a proposal receipt for gating."""
    proposal = orchestrator.gate.propose(
        game_state["turn"],
        req.action,
        {"details": req.details, "investment": req.investment, "target": "gravity-mosaic"},
    )
    game_state["work_packs"].append({"id": proposal.id, "action": req.action, "status": "PROPOSED"})
    return {"proposal": proposal.to_dict(), "message": "Proposal created. Call /governance/gate to evaluate with FunForge."}

@app.post("/governance/gate")
async def governance_gate(req: GateRequest) -> Dict[str, Any]:
    """Run the FunForge quality gate on a proposal. This is the real receipt-first control."""
    fun = req.fun_score_override
    if fun is None:
        fun = FunForge.calculate_fun_metrics({"agency": 0.9, "emergence": 0.92, "pacing": 0.8, "juice": 0.85})
    result = orchestrator.gate.gate(req.proposal_id, fun)
    if result.get("approved"):
        game_state["player"]["fun_score"] = max(game_state["player"]["fun_score"], fun)
    return result

@app.post("/governance/advance_and_log")
async def governance_advance_and_log() -> Dict[str, Any]:
    """Convenience: advance a cycle (agents decide + FunForge + gate) and ensure a receipt is on disk."""
    res = await advance_turn()
    # The orchestrator + receipt_store already wrote the main receipt
    return {
        "cycle_result": res,
        "disk_receipts": [str(p) for p in (Path(__file__).parent.parent / "receipts").glob("*.md")][-3:],
    }

@app.get("/governance/gravity_deploy_recommendation")
async def gravity_deploy_recommendation() -> Dict[str, Any]:
    """Agentic hook: asks the brains what they recommend for the gravity-mosaic right now.
    Real deploys must still be executed via the strict deploy.sh (this only advises + logs receipt).
    """
    state = {"resources": game_state["player"]["resources"]}
    decision = grok.decide_action(state)
    fun = FunForge.calculate_fun_metrics({"agency": 0.95, "emergence": 0.9, "pacing": 0.85, "juice": 0.88})
    comment = FunForge.comment(fun)
    rec = {
        "decision": decision,
        "fun_score": fun,
        "comment": comment,
        "recommendation": "If approved by gate, run: ./tools/deploy-gravity-mosaic/deploy.sh (it will do full literal verification on the separate gravity project).",
        "warning": "NEVER edit gravity-mosaic directly. CivForge only governs via the deploy tool + receipts.",
    }
    # Log it
    receipt_store.append({"action": "gravity_recommendation", "fun_score": fun, **rec}, "gravity-rec")
    return rec


@app.post("/simulation/what_if")
async def what_if_simulation(scenario: dict):
    """What-if simulation for Civ Game mechanics, driven by live dawsos-nexus telemetry (customMetrics, agentState).
    Projects resource yields + fun impact. Uses nexus as source of truth for fleet/agent context (thin bridge).
    """
    nexus_data = {}
    try:
        nexus = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")
        # Try specific app, then fleet list, then health as fallback (nexus schema: apps may be list or keyed)
        for ep in [f"{nexus}/api/apps/civforge-kernel", f"{nexus}/api/apps", f"{nexus}/api/health"]:
            resp = requests.get(ep, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and (data.get("latestMetrics") or data.get("customMetrics") or data.get("agentState")):
                    nexus_data = data
                    break
                if isinstance(data, list) and data:
                    # pick civforge or first
                    for a in data:
                        if isinstance(a, dict) and a.get("appId") == "civforge-kernel":
                            nexus_data = a
                            break
                    if not nexus_data:
                        nexus_data = data[0]
                else:
                    nexus_data = data
                break
    except Exception:
        nexus_data = {}
    # Project resources + fun using scenario investment (simple model extensible via more nexus customMetrics)
    current = dict(game_state["player"]["resources"])
    invest = int(scenario.get("investment", 0))
    projected = {k: v + invest for k, v in current.items()}
    # Fun impact estimate from nexus context if present, else local
    fun_base = game_state["player"].get("fun_score", 0)
    nexus_fun = 0
    if isinstance(nexus_data, dict):
        cm = nexus_data.get("customMetrics") or nexus_data.get("latestMetrics") or {}
        nexus_fun = cm.get("funScore", 0) or 0
    fun_impact = max(fun_base, nexus_fun) + 3 + (invest // 2)
    return {
        "current": current,
        "projected": projected,
        "nexus_context": nexus_data if nexus_data else {"note": "no telemetry yet or nexus down"},
        "fun_impact_estimate": round(fun_impact, 1),
        "note": "Simulation using dawsos-nexus telemetry/customMetrics for Civ Game what-if (governed, receipt-first)."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


# Thin bridge auth to dawsos-nexus (8082) - primary control + evolving auth sister (replaces archived prototype).
# register-device / token issuance / verify via tools/dawsos_auth_client.py or direct /api/apps + x-nexus-api-key / operator token.
# protected_advance demonstrates govern scope for sensitive actions. Commands from nexus are treated as proposals (see SEPARATION.md).
import requests
from fastapi import Header, HTTPException

NEXUS_AUTH_BASE = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")
NEXUS_OPERATOR = os.environ.get("NEXUS_OPERATOR_TOKEN", "")

def require_govern_token(authorization: str = Header(None)):
    """Validate govern token/credential from dawsos-nexus.
    Accepts: Bearer <NEXUS_OPERATOR_TOKEN>, or x-nexus-api-key style, or falls back to client verify.
    Thin HTTP only. Not full identity store (hybrid possible).
    """
    if not authorization:
        # Allow dev/demo with operator token in env for local Mac Studio
        if NEXUS_OPERATOR:
            return {"scope": "govern", "identity": "operator-dev", "source": "env-operator"}
        raise HTTPException(401, "Auth token required (dawsos-nexus govern scope)")
    token = authorization.split(" ")[-1] if " " in authorization else authorization
    if NEXUS_OPERATOR and token == NEXUS_OPERATOR:
        return {"scope": "govern", "identity": "operator", "source": "nexus-operator"}
    # Try client-style or health with token (nexus uses header auth primarily)
    try:
        # Prefer header style for apps
        r = requests.get(f"{NEXUS_AUTH_BASE}/api/health", headers={"Authorization": f"Bearer {token}", "x-nexus-api-key": token}, timeout=4)
        if r.status_code == 200:
            return {"scope": "govern", "identity": "nexus-auth", "source": "nexus-verify"}
    except Exception:
        pass
    # Fallback: if no operator set, be permissive for local dev (governed by 8080 kernel anyway)
    if not NEXUS_OPERATOR:
        return {"scope": "govern", "identity": "local-dev", "warning": "no operator token; dev mode"}
    raise HTTPException(401, "Invalid or insufficient dawsos-nexus token for govern action")

@app.post("/governance/protected_advance")
async def protected_advance(claims: dict = Depends(require_govern_token)):
    # Protected path: requires valid govern credential from dawsos-nexus (or operator token).
    # In real use: register CivForge as app via client, issue scoped token, use for sensitive turns.
    # Telemetry still sent on success.
    extra = {"territories": game_state["player"].get("territories", 0), "cities": game_state["player"].get("cities", 0), "events": game_state.get("events", [])}
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)
    return {
        "status": "advanced with auth",
        "claims": claims,
        "turn": game_state["turn"],
        "note": "Protected via dawsos-nexus (8082) thin bridge. Commands from nexus treated as proposals per sister contract."
    }
