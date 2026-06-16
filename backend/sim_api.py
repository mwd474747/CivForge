from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests, os
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import sys
from pathlib import Path
from datetime import datetime
import hmac

# Add core to path for the realigned Python agentic patterns (no more Godot MVP)
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore
from core.swarm_join import FORGE_COORDINATOR_ID
from core.mechanics_registry import build_default_registry, default_mechanics_lanes
from backend.civstudy_flavor import game_state_note
from backend.agent_control import agent_controls_summary, issue_directive, select_agent, toggle_autonomy
from backend.competition_modes import competition_summary, set_competition_mode, spectator_log, COMPETITION_MODES
from backend.dashboard_components import get_dashboard_registry
from backend.simulation_boundary import boundary_summary
from backend.telemetry_enrich import enrich_telemetry_payload

from backend.civstudy_metadata import civstudy_reference_panel
from backend.civstudy_mechanics_bridge import civstudy_sim_summary, ensure_civstudy_sim_state
from backend.game_reset import apply_defeat_cascade_seed, apply_game_reset
from backend.game_session import apply_defeat, check_defeat_conditions, policy_flags, session_phase
from backend.game_actions import action_catalog, claim_map_tile, player_cycle_decision, select_district, send_envoy, unlock_policy
from backend.trust_erosion import trust_summary
from backend.victory_hud import victory_hud_summary
from backend.mechanics_proposals import (
    apply_mechanics,
    gate_mechanics,
    list_mechanics_proposals,
    propose_mechanics,
    proposals_summary,
)
from backend.turn_simulation import (
    enrich_cycle_receipt,
    maybe_emit_defeat_receipt,
    maybe_emit_victory_receipt,
    run_turn_simulation,
)
from backend.multi_agent_state import (
    AGENT_LABELS,
    FACTION_COLORS,
    add_negotiation,
    default_alliances,
    default_map_tiles,
    default_negotiations,
    default_victory_progress,
    ensure_multi_agent_state,
    negotiations_for_api,
    respond_negotiation,
)

NEXUS_URL = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")

def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _constant_time_match(candidate: str, allowed: list[str]) -> bool:
    return any(token and hmac.compare_digest(candidate, token) for token in allowed)


def require_public_mode_token(
    authorization: Optional[str] = Header(None),
    x_civforge_token: Optional[str] = Header(None, alias="X-CivForge-Token"),
    x_nexus_api_key: Optional[str] = Header(None, alias="x-nexus-api-key"),
) -> Dict[str, Any]:
    """Optional exposure guard for mutating routes.

    Local development remains permissive by default. If the kernel is intentionally
    exposed through a tunnel or public host, set `CIVFORGE_PUBLIC_MODE=1` and one
    of `CIVFORGE_OPERATOR_TOKEN`, `CIVFORGE_API_KEY`, or `NEXUS_API_KEY`.
    """
    if not _truthy_env("CIVFORGE_PUBLIC_MODE") and not _truthy_env("CIVFORGE_REQUIRE_AUTH"):
        return {"public_mode": False, "scope": "local"}

    allowed = [
        os.environ.get("CIVFORGE_OPERATOR_TOKEN", ""),
        os.environ.get("CIVFORGE_API_KEY", ""),
        os.environ.get("NEXUS_API_KEY", ""),
    ]
    candidates = [x for x in (x_civforge_token, x_nexus_api_key) if isinstance(x, str) and x]
    if isinstance(authorization, str) and authorization:
        candidates.append(authorization.split(" ", 1)[1] if authorization.lower().startswith("bearer ") else authorization)
    if any(_constant_time_match(candidate, allowed) for candidate in candidates):
        return {"public_mode": True, "scope": "mutate"}
    raise HTTPException(401, "Mutating routes require a valid CivForge or Nexus API token (CIVFORGE_PUBLIC_MODE or CIVFORGE_REQUIRE_AUTH)")


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
        if extra:
            for key in ("alliancesCount", "negotiationsPending", "victoryProgress", "victoryOutcome", "sessionPhase", "policyFlags", "mapPlayerTiles", "mechanicsSummary"):
                if key in extra:
                    payload["customMetrics"][key] = extra[key]
        api_key = os.environ.get("NEXUS_API_KEY", "")
        headers = {"x-nexus-api-key": api_key} if api_key else None
        requests.post(f"{NEXUS_URL}/api/telemetry/heartbeat", json=payload, headers=headers, timeout=5)
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

_cors_raw = os.environ.get(
    "CIVFORGE_CORS_ORIGINS",
    "https://civforge.vercel.app,http://127.0.0.1:8080,http://localhost:8080",
)
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def local_dashboard():
    """Same-origin dashboard for Mac Studio — works over http://127.0.0.1:8080 (no mixed-content)."""
    path = Path(__file__).parent.parent / "frontend" / "index.html"
    return path.read_text(encoding="utf-8")

# === Core governance runtime (replaces Godot TurnManager / MVP driver) ===
# Persistence enabled per Mac Studio canonical lock-in (WP-BACKEND-REALIGN-EXEC-001)
# State + receipts now survive uvicorn restarts via SQLite
DB_PATH = Path(__file__).parent.parent / "gravity_backend.db"
orchestrator = GovernanceOrchestrator()
mechanics_registry = build_default_registry()
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
    "map_tiles": default_map_tiles(),
    "alliances": default_alliances(),
    "negotiations": default_negotiations(),
    "victory_progress": default_victory_progress(),
    "mechanics_lanes": default_mechanics_lanes(),
    "mechanics_proposals": [],
    "mechanics_overrides": {},
}

# Try to restore last known state snapshot if available (now safe)
restored = receipt_store.load_state("game_state")
if restored:
    game_state.update(restored)
    print("[CivForge] Restored previous state snapshot from SQLite (persistence active)")
ensure_multi_agent_state(game_state)
ensure_civstudy_sim_state(game_state)
orchestrator.turn = int(game_state.get("turn", 1))
orchestrator.gate.load_proposals(game_state.get("governance_proposals", []))


def _sync_governance_proposals_to_state() -> None:
    game_state["governance_proposals"] = [p.to_dict() for p in orchestrator.gate.proposals]


def _update_work_pack_status(proposal_id: str, status: str) -> None:
    for work_pack in game_state.get("work_packs", []):
        if work_pack.get("id") == proposal_id or work_pack.get("proposal_id") == proposal_id:
            work_pack["status"] = status
            work_pack["updated_at"] = datetime.utcnow().isoformat()


def _persist_governance_event(receipt: Dict[str, Any], filename_hint: str) -> None:
    game_state["receipts"].append(receipt)
    _sync_governance_proposals_to_state()
    receipt_store.append(receipt, filename_hint=filename_hint)
    receipt_store.save_state("game_state", game_state)

def telemetry_extra_from_state() -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    if "mechanics_lanes" not in game_state:
        game_state["mechanics_lanes"] = default_mechanics_lanes()
    player_tiles = sum(1 for t in game_state.get("map_tiles", []) if t.get("owner") == "player")
    pending_neg = sum(1 for n in game_state.get("negotiations", []) if n.get("status") == "pending")
    ml = game_state.get("mechanics_lanes", {})
    base = {
        "territories": game_state["player"].get("territories", 0),
        "cities": game_state["player"].get("cities", 0),
        "events": game_state.get("events", []),
        "alliancesCount": len(game_state.get("alliances", [])),
        "negotiationsPending": pending_neg,
        "victoryProgress": game_state.get("victory_progress", {}).get("joint_progress", 0),
        "victoryOutcome": game_state.get("victory_progress", {}).get("outcome"),
        "sessionPhase": session_phase(game_state),
        "policyFlags": policy_flags(game_state),
        "mapPlayerTiles": player_tiles,
        "mechanicsSummary": {
            "military_strength": ml.get("military", {}).get("strength"),
            "economic_institutions": ml.get("economic", {}).get("institutions"),
            "cultural_chains": ml.get("cultural", {}).get("event_chains"),
        },
    }
    return enrich_telemetry_payload(game_state, base)

forge_coordinator = orchestrator.register_agent(
    FORGE_COORDINATOR_ID, "Forge Coordinator (in-kernel)"
)
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

class NegotiateRequest(BaseModel):
    to: str = "harper"
    offer: str = "Propose joint governance review"

class NegotiateRespondRequest(BaseModel):
    negotiation_id: str
    accept: bool = True

@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """Returns live governance workspace + multi-agent civ layer."""
    ensure_multi_agent_state(game_state)
    recent = game_state["receipts"][-5:] if game_state["receipts"] else []
    return {
        "status": "active",
        "current_turn": game_state["turn"],
        "player": game_state["player"],
        "ai_civs": game_state["ai_civs"],
        "recent_events": game_state["events"][-8:],
        "fun_score": game_state["player"]["fun_score"],
        "receipts": recent,
        "map_tiles": game_state["map_tiles"],
        "alliances": game_state["alliances"],
        "negotiations": negotiations_for_api(game_state),
        "victory_progress": game_state["victory_progress"],
        "agent_labels": AGENT_LABELS,
        "faction_colors": FACTION_COLORS,
        "work_packs": game_state.get("work_packs", [])[-6:],
        "mechanics_lanes": game_state.get("mechanics_lanes", default_mechanics_lanes()),
        "civstudy_reference": civstudy_reference_panel(),
        "civstudy_sim": civstudy_sim_summary(game_state),
        "session_phase": session_phase(game_state),
        "action_catalog": action_catalog(game_state),
        "trust_erosion": trust_summary(game_state),
        "victory_hud": victory_hud_summary(game_state),
        "session_history": game_state.get("session_history", [])[-5:],
        "mechanics_proposals": proposals_summary(game_state),
        "mechanics_overrides": game_state.get("mechanics_overrides", {}),
        "note": game_state_note(),
        "agent_controls": agent_controls_summary(game_state),
        "competition_mode": competition_summary(game_state),
        "simulation_boundary": boundary_summary(game_state),
        "dashboard_components": get_dashboard_registry().all_components(),
    }

@app.get("/game/founding-session")
async def founding_session() -> Dict[str, Any]:
    """Guided founding session metadata for dashboard UI."""
    ensure_multi_agent_state(game_state)
    prod = game_state["player"]["resources"].get("prod", 0)
    return {
        "steps": [
            {"id": 1, "title": "Choose work pack name", "field": "city_name"},
            {"id": 2, "title": "Set production investment", "field": "investment", "min": 3, "max": prod},
            {"id": 3, "title": "Confirm & found", "action": "POST /found_city"},
        ],
        "defaults": {"city_name": "New Work Pack", "investment": 4, "position": "gravity-mosaic"},
        "available_prod": prod,
        "cities": game_state["player"].get("cities", 0),
        "can_found": prod >= 3,
    }

@app.post("/found_city")
async def found_city(req: FoundCityRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
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
    extra = telemetry_extra_from_state()
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)

    return {
        "message": f"Work pack '{req.city_name}' initiated successfully!",
        "updated_state": game_state["player"],
        "receipt": receipt,
        "next_steps": "Call /advance_turn to run a full governance cycle (agent decisions + FunForge + gate), or use /governance/propose for a gravity deploy.",
    }

@app.post("/advance_turn")
async def advance_turn(_claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Advance one governance cycle (the heart of the earlier FastAPI version).

    Now powered by the real Python GovernanceOrchestrator + AgentBrains + FunForge.
    Produces a rich receipt (status, fun_score, decisions, gate result) and updates the workspace state.
    """
    phase = session_phase(game_state)
    if phase == "epilogue":
        raise HTTPException(
            409,
            "Game is in victory epilogue — POST /game/reset to start a new session",
        )
    if phase == "defeat":
        reason = game_state.get("victory_progress", {}).get("defeat_reason", "defeat")
        raise HTTPException(409, f"Game ended in defeat ({reason}) — POST /game/reset to retry")
    result = orchestrator.advance_cycle(player_actions=1)
    player_line = player_cycle_decision(game_state, 1)
    result["receipt"].setdefault("decisions", {})["player"] = player_line

    game_state["turn"] = result["turn"]
    game_state["player"]["fun_score"] = result["fun_score"]
    victory_before = dict(game_state.get("victory_progress", {}))
    defeat_before = victory_before.get("outcome")

    # Tick resources (governance budget)
    for key in ["food", "prod", "sci", "influence", "verify_budget"]:
        if key in game_state["player"]["resources"]:
            game_state["player"]["resources"][key] += 1

    receipt = enrich_cycle_receipt(result["receipt"], game_state)
    game_state["receipts"].append(receipt)
    for ev in result.get("events", []):
        game_state["events"].append(ev)

    for ev in run_turn_simulation(game_state, mechanics_registry, receipt.get("decisions", {})):
        game_state["events"].append(ev)

    maybe_emit_victory_receipt(victory_before, game_state, receipt_store)
    maybe_emit_defeat_receipt(defeat_before, game_state, receipt_store)

    # Persist the important ones + snapshot full state for restart survival
    receipt_store.append(receipt, filename_hint="governance-cycle")
    receipt_store.save_state("game_state", game_state)

    # Send telemetry to dawsos-nexus (8082) - primary for control, telemetry, simulation input, audit mirror
    extra = telemetry_extra_from_state()
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)

    return {
        "message": f"Governance cycle {game_state['turn']} advanced.",
        "receipt": receipt,
        "state": game_state["player"],
        "agent_decisions": receipt.get("decisions", {}),
        "victory_progress": game_state["victory_progress"],
        "mechanics_lanes": game_state.get("mechanics_lanes"),
        "session_phase": session_phase(game_state),
    }

@app.post("/game/negotiate")
async def game_negotiate(req: NegotiateRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Player proposes a negotiation offer to another agent."""
    entry = add_negotiation(game_state, req.to, req.offer, from_agent="player")
    if entry.get("error"):
        return entry
    receipt_store.save_state("game_state", game_state)
    return {"negotiation": entry, "negotiations": negotiations_for_api(game_state)}

@app.post("/game/negotiate/respond")
async def game_negotiate_respond(req: NegotiateRespondRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Accept or decline a pending negotiation."""
    result = respond_negotiation(game_state, req.negotiation_id, req.accept)
    receipt_store.save_state("game_state", game_state)
    return {"result": result, "alliances": game_state["alliances"], "victory_progress": game_state["victory_progress"]}



class DistrictSelectRequest(BaseModel):
    district_id: str = "governance-quarter"

class PolicyUnlockRequest(BaseModel):
    policy_id: str

class MapClaimRequest(BaseModel):
    x: int
    y: int

class GameResetRequest(BaseModel):
    seed_profile: Optional[str] = None

class SendEnvoyRequest(BaseModel):
    alliance_id: str

class MechanicsProposeRequest(BaseModel):
    kind: str
    title: str
    payload: Dict[str, Any] = {}
    author: str = "grok_swarm"
    work_pack_id: str = ""
    rationale: str = ""

class MechanicsGateRequest(BaseModel):
    proposal_id: str
    fun_score_override: Optional[float] = None


class AgentSelectRequest(BaseModel):
    agent_id: str

class AgentDirectiveRequest(BaseModel):
    agent_id: str
    directive: str

class AgentAutonomyRequest(BaseModel):
    agent_id: str
    autonomous: bool = True

class CompetitionModeRequest(BaseModel):
    mode: str = "none"

class MechanicsApplyRequest(BaseModel):
    proposal_id: str

@app.get("/game/actions")
async def game_actions_catalog() -> Dict[str, Any]:
    """Player action costs and unlockable policies for dashboard/MCP."""
    ensure_multi_agent_state(game_state)
    return action_catalog(game_state)

@app.post("/game/district/select")
async def game_district_select(req: DistrictSelectRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = select_district(game_state, req.district_id)
    if result.get("error"):
        return result
    receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/policy/unlock")
async def game_policy_unlock(req: PolicyUnlockRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = unlock_policy(game_state, req.policy_id)
    if result.get("error"):
        return result
    receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/map/claim")
async def game_map_claim(req: MapClaimRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = claim_map_tile(game_state, req.x, req.y)
    if result.get("error"):
        return result
    receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/diplomacy/send_envoy")
async def game_send_envoy(req: SendEnvoyRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = send_envoy(game_state, req.alliance_id)
    if result.get("error"):
        return result
    receipt_store.save_state("game_state", game_state)
    return result

@app.get("/game/mechanics/proposals")
async def game_mechanics_proposals_list(status: Optional[str] = None) -> Dict[str, Any]:
    """List mechanics proposals (Grok swarm proposal lane — not simulation-only)."""
    return list_mechanics_proposals(game_state, status=status)

@app.post("/game/mechanics/propose")
async def game_mechanics_propose(
    req: MechanicsProposeRequest,
    _claims: Dict[str, Any] = Depends(require_public_mode_token),
) -> Dict[str, Any]:
    """Propose a game mechanic update (runtime patch or Cursor planning kind)."""
    result = propose_mechanics(
        game_state,
        kind=req.kind,
        title=req.title,
        payload=req.payload,
        author=req.author,
        work_pack_id=req.work_pack_id,
        rationale=req.rationale,
    )
    if not result.get("error"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/mechanics/gate")
async def game_mechanics_gate(
    req: MechanicsGateRequest,
    _claims: Dict[str, Any] = Depends(require_public_mode_token),
) -> Dict[str, Any]:
    """FunForge gate on a mechanics proposal."""
    result = gate_mechanics(game_state, req.proposal_id, req.fun_score_override)
    if not result.get("error"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/mechanics/apply")
async def game_mechanics_apply(
    req: MechanicsApplyRequest,
    _claims: Dict[str, Any] = Depends(require_public_mode_token),
) -> Dict[str, Any]:
    """Apply a gated-approved runtime mechanics proposal."""
    result = apply_mechanics(game_state, req.proposal_id)
    if result.get("applied"):
        receipt_store.save_state("game_state", game_state)
    return result


@app.post("/game/agent/select")
async def game_agent_select(req: AgentSelectRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = select_agent(game_state, req.agent_id)
    if result.get("ok"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/agent/directive")
async def game_agent_directive(req: AgentDirectiveRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = issue_directive(game_state, req.agent_id, req.directive)
    if result.get("ok"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/agent/autonomy")
async def game_agent_autonomy(req: AgentAutonomyRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = toggle_autonomy(game_state, req.agent_id, req.autonomous)
    if result.get("ok"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.post("/game/competition/mode")
async def game_competition_mode(req: CompetitionModeRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    result = set_competition_mode(game_state, req.mode)
    if result.get("ok"):
        receipt_store.save_state("game_state", game_state)
    return result

@app.get("/game/competition/spectator")
async def game_competition_spectator(limit: int = 20) -> Dict[str, Any]:
    return {"spectator_log": spectator_log(game_state, limit=limit), "modes": list(COMPETITION_MODES)}

@app.get("/game/dashboard/components")
async def game_dashboard_components() -> Dict[str, Any]:
    reg = get_dashboard_registry()
    return {"tabs": reg.tabs(), "panels": reg.panels()}

@app.post("/game/reset")
async def game_reset(
    req: GameResetRequest = GameResetRequest(),
    _claims: Dict[str, Any] = Depends(require_public_mode_token),
) -> Dict[str, Any]:
    """Start a fresh game: reset in-memory state, orchestrator working memory, and SQLite snapshot."""
    summary = apply_game_reset(game_state, orchestrator)
    if req.seed_profile == "defeat_cascade":
        apply_defeat_cascade_seed(game_state)
        orchestrator.turn = game_state["turn"]
        defeat_before = game_state.get("victory_progress", {}).get("outcome")
        reason = check_defeat_conditions(game_state)
        if reason:
            apply_defeat(game_state, reason, game_state["turn"])
            maybe_emit_defeat_receipt(defeat_before, game_state, receipt_store)
    _sync_governance_proposals_to_state()
    reset_receipt = {
        "turn": game_state["turn"],
        "action": "game_reset",
        "status": "SUCCESS",
        "prior_session": summary.get("prior_session", {}),
        "sessions_logged": summary.get("sessions_logged", 0),
        "claim": "New game session started; prior run stats logged.",
    }
    game_state["receipts"].append(reset_receipt)
    receipt_store.append(reset_receipt, filename_hint="game-reset")
    receipt_store.save_state("game_state", game_state)
    extra = telemetry_extra_from_state()
    send_telemetry_to_nexus(
        game_state["turn"],
        game_state["player"]["fun_score"],
        game_state["player"]["resources"],
        extra,
    )
    return {
        "message": (
            f"Game reset with defeat-cascade seed (turn {game_state['turn']}, defeat={session_phase(game_state) == 'defeat'})."
            if req.seed_profile == "defeat_cascade"
            else "Game reset to turn 1."
        ),
        "summary": summary,
        "session_phase": session_phase(game_state),
        "session_history": game_state.get("session_history", []),
        "victory_progress": game_state["victory_progress"],
        "receipt": reset_receipt,
    }

def _integrate_civforge_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "civforge_version": "governance-fastapi-2026",
        "current_receipts": game_state["receipts"][-6:],
        "simulation_status": "FastAPI workspace active. Governing the separate gravity-mosaic project via receipt-first loops.",
        "core": "AgentBrain + FunForge + GovernanceGate + Orchestrator (pure Python, no Godot MVP)",
        "gravity_deploy_tool": "tools/deploy-gravity-mosaic/deploy.sh (literal verification enforced)",
        "next": "POST /found_city to start a work pack, POST /advance_turn for a cycle, or use the governance endpoints + deploy tool.",
        "received": payload or None,
    }


@app.get("/integrate/civforge")
async def integrate_civforge() -> Dict[str, Any]:
    """Hook for CivForge agents (Grok, receipts, governance). Primary integration point."""
    return _integrate_civforge_response()


@app.post("/integrate/civforge")
async def integrate_civforge_post(payload: Dict[str, Any], _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """POST-compatible bridge for swarm work packs. It reports intake; execution still requires proposal/gate."""
    return _integrate_civforge_response(payload)


# === New governance-aligned endpoints (do not break the earlier /state /found_city surface) ===

@app.post("/governance/propose")
async def governance_propose(req: ProposeWorkRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Propose a concrete work item (e.g. a gravity-mosaic change). Returns a proposal receipt for gating."""
    proposal = orchestrator.gate.propose(
        game_state["turn"],
        req.action,
        {"details": req.details, "investment": req.investment, "target": "gravity-mosaic"},
    )
    proposal_receipt = proposal.to_dict()
    proposal_receipt["receipt_type"] = "governance_proposal"
    game_state["work_packs"].append({"id": proposal.id, "proposal_id": proposal.id, "action": req.action, "status": "PROPOSED"})
    _persist_governance_event(proposal_receipt, filename_hint="governance-proposal")
    return {"proposal": proposal_receipt, "message": "Proposal created. Call /governance/gate to evaluate with FunForge."}

@app.post("/governance/gate")
async def governance_gate(req: GateRequest, _claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Run the FunForge quality gate on a proposal. This is the real receipt-first control."""
    fun = req.fun_score_override
    if fun is None:
        fun = FunForge.calculate_fun_metrics({"agency": 0.9, "emergence": 0.92, "pacing": 0.8, "juice": 0.85})
    result = orchestrator.gate.gate(req.proposal_id, fun)
    if result.get("approved"):
        game_state["player"]["fun_score"] = max(game_state["player"]["fun_score"], fun)
    if result.get("receipt"):
        proposal_receipt = result["receipt"]
        _update_work_pack_status(req.proposal_id, proposal_receipt.get("status", "GATED"))
        gate_receipt = {
            "id": f"{req.proposal_id}-gate-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "turn": game_state["turn"],
            "action": "governance_gate",
            "status": proposal_receipt.get("status"),
            "fun_score": fun,
            "proposal_id": req.proposal_id,
            "approved": bool(result.get("approved")),
            "comment": result.get("comment"),
            "proposal": proposal_receipt,
            "receipt_type": "governance_gate",
        }
        _persist_governance_event(gate_receipt, filename_hint="governance-gate")
    return result

@app.post("/governance/advance_and_log")
async def governance_advance_and_log(_claims: Dict[str, Any] = Depends(require_public_mode_token)) -> Dict[str, Any]:
    """Convenience: advance a cycle (agents decide + FunForge + gate) and ensure a receipt is on disk."""
    res = await advance_turn(_claims)
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
    decision = forge_coordinator.decide_action(state)
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
async def what_if_simulation(scenario: dict, _claims: Dict[str, Any] = Depends(require_public_mode_token)):
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

# Thin bridge to dawsos-nexus (8082) — machine satellite only (telemetry heartbeats + command proposals).
# Per boundary contract (wt governed-connectors-registry.v1 + CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md) + dawsOS agent feedback:
#   - governance_kernel type, allowed_actions=["sync_config"] only (strict per registry + user Q1).
#   - x-nexus-api-key (satellite key) for machine auth. Operator token path dropped for CivForge (per Q2 "remove entirely").
#   - Identity / JWT long-term via dawsos-auth-prototype :8081. No hybrid bypass.
# register-device / machine heartbeat via client or /api/apps (satellite key). Commands propose (not execute). See SEPARATION.md planes.
NEXUS_AUTH_BASE = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")

def require_govern_token(authorization: str = Header(None)):
    """require_machine_satellite_key (renamed focus per agent rec + user Q2 'remove entirely').
    Validate machine govern credential from dawsos-nexus for governance_kernel satellite.
    Requires: x-nexus-api-key (preferred satellite key) or Bearer that passes /api/health.
    Exact NEXUS_OPERATOR_TOKEN match path dropped (no operator fallback for CivForge satellite).
    Thin HTTP only. Machine/command context only. Identity via auth-prototype :8081 long-term.
    """
    if not authorization:
        raise HTTPException(401, "Auth token required (dawsos-nexus machine satellite key for governance_kernel)")
    token = authorization.split(" ")[-1] if " " in authorization else authorization
    # Verify via x-nexus-api-key or Bearer + health (satellite posture, no operator exact match)
    try:
        r = requests.get(f"{NEXUS_AUTH_BASE}/api/health", headers={"Authorization": f"Bearer {token}", "x-nexus-api-key": token}, timeout=4)
        if r.status_code == 200:
            return {"scope": "govern", "identity": "nexus-auth", "source": "nexus-verify"}
    except Exception:
        pass
    raise HTTPException(401, "Invalid or insufficient dawsos-nexus satellite key for govern action (operator path removed per boundary)")

@app.post("/governance/protected_advance")
async def protected_advance(claims: dict = Depends(require_govern_token)):
    # Protected path: requires valid govern credential from dawsos-nexus.
    # In real use: register CivForge as app via client, issue scoped token, use for sensitive turns.
    # Telemetry still sent on success.
    extra = telemetry_extra_from_state()
    send_telemetry_to_nexus(game_state["turn"], game_state["player"]["fun_score"], game_state["player"]["resources"], extra)
    return {
        "status": "advanced with auth",
        "claims": claims,
        "turn": game_state["turn"],
        "note": "Protected via dawsos-nexus (8082) thin bridge. Commands from nexus treated as proposals per sister contract."
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
