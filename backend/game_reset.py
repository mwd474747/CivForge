"""Fresh game state factory and reset helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from backend.civstudy_mechanics_bridge import default_civstudy_sim_state, ensure_civstudy_sim_state
from backend.multi_agent_state import (
    default_alliances,
    default_map_tiles,
    default_negotiations,
    ensure_multi_agent_state,
    fresh_victory_progress,
)
from core.mechanics_registry import default_mechanics_lanes
from core.orchestrator import GovernanceOrchestrator


def collect_session_stats(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Snapshot stats from the ending session (for reset receipt / history)."""
    vp = game_state.get("victory_progress", {})
    player = game_state.get("player", {})
    sim = game_state.get("civstudy_sim", {})
    return {
        "turn": game_state.get("turn", 0),
        "outcome": vp.get("outcome"),
        "defeat_reason": vp.get("defeat_reason"),
        "joint_progress": vp.get("joint_progress", 0),
        "target": vp.get("target", 100),
        "fun_score": player.get("fun_score"),
        "cities": player.get("cities"),
        "territories": player.get("territories"),
        "alliances_count": len(game_state.get("alliances", [])),
        "negotiations_pending": sum(
            1 for n in game_state.get("negotiations", []) if n.get("status") == "pending"
        ),
        "unlocked_policies": list(sim.get("policy_tree", {}).get("unlocked", [])),
        "unlocked_forks": list(sim.get("unlocked_forks", [])),
        "active_district_id": sim.get("active_district_id"),
        "milestones_done": sum(1 for m in vp.get("milestones", []) if m.get("done")),
    }


def build_initial_game_state() -> Dict[str, Any]:
    """Canonical new-game snapshot (matches kernel boot defaults)."""
    state: Dict[str, Any] = {
        "turn": 1,
        "player": {
            "name": "Governance Lead (Grok)",
            "resources": {"food": 12, "prod": 12, "sci": 9, "influence": 6, "verify_budget": 7},
            "territories": 5,
            "cities": 2,
            "fun_score": 87.0,
        },
        "ai_civs": [
            {"name": "Harper (Systems)", "resources": {"food": 10, "prod": 8, "sci": 11, "influence": 5}, "territories": 3},
            {"name": "Sebastian (Governance)", "resources": {"food": 9, "prod": 7, "sci": 8, "influence": 9}, "territories": 3},
        ],
        "events": [],
        "receipts": [],
        "work_packs": [],
        "governance_proposals": [],
        "session_history": [],
        "map_tiles": default_map_tiles(),
        "alliances": default_alliances(),
        "negotiations": default_negotiations(),
        "mechanics_lanes": default_mechanics_lanes(),
        "mechanics_proposals": [],
        "mechanics_overrides": {},
    }
    ensure_multi_agent_state(state)
    state["victory_progress"] = fresh_victory_progress(state)
    ensure_civstudy_sim_state(state)
    return state


def apply_game_reset(game_state: Dict[str, Any], orchestrator: GovernanceOrchestrator) -> Dict[str, Any]:
    """Replace live state and orchestrator working memory with a fresh game."""
    prior_stats = collect_session_stats(game_state)
    prior_history: List[Dict[str, Any]] = list(game_state.get("session_history", []))
    prior_history.append(prior_stats)

    fresh = build_initial_game_state()
    fresh["session_history"] = prior_history[-10:]

    game_state.clear()
    game_state.update(deepcopy(fresh))

    # Hard guarantee: no victory/defeat residue on a new session
    game_state["victory_progress"] = fresh_victory_progress(game_state)
    game_state["victory_progress"].pop("outcome", None)
    game_state["victory_progress"].pop("defeat_reason", None)

    orchestrator.turn = 1
    orchestrator.receipts = []
    orchestrator.events = []
    orchestrator.workstream_resources = {"prod": 12, "sci": 8, "verify": 6, "deploy_budget": 5}
    orchestrator.gate.proposals = []

    outcome_note = ""
    if prior_stats.get("outcome"):
        outcome_note = f" (outcome={prior_stats['outcome']})"
    game_state["events"].append(
        f"Turn 1: New game — prior run turn {prior_stats['turn']}{outcome_note}, "
        f"progress {prior_stats.get('joint_progress', 0)}/{prior_stats.get('target', 100)}."
    )

    return {
        "prior_session": prior_stats,
        "sessions_logged": len(prior_history),
        "turn": game_state["turn"],
        "victory_progress": game_state["victory_progress"],
        "session_phase": "active",
    }


def apply_defeat_cascade_seed(game_state: Dict[str, Any]) -> None:
    """Low-fun / broken-alliance starting posture for defeat sim (WP-GROK-SIM-DEFEAT-CASCADE-002)."""
    game_state["turn"] = 22
    game_state["player"]["fun_score"] = 30.0
    vp = game_state.setdefault("victory_progress", {})
    vp["joint_progress"] = 8
    vp.pop("outcome", None)
    vp.pop("defeat_reason", None)
    broken = 0
    for alliance in game_state.get("alliances", []):
        if "player" in alliance.get("parties", []):
            alliance["status"] = "broken"
            broken += 1
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Defeat-cascade seed applied ({broken} player alliances broken, fun=30)."
    )
