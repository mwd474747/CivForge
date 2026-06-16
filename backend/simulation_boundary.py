"""Simulation vs game-mechanics boundary — orchestration layer only."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.competition_modes import tick_competition
from backend.multi_agent_state import sync_victory_milestones, tick_multi_agent_state

SIMULATION_PHASES = ("multi_agent", "competition", "milestones")


def run_simulation_layer(
    game_state: Dict[str, Any],
    decisions: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Orchestration tick: map/alliances/negotiations, competitions, milestone sync.

    Does NOT mutate mechanics_lanes — that is exclusively MechanicsRegistry.pass_through_tick().
    """
    events: List[str] = []
    events.extend(tick_multi_agent_state(game_state, decisions or {}))
    events.extend(tick_competition(game_state, decisions or {}))
    vp = game_state.setdefault("victory_progress", {})
    events.extend(sync_victory_milestones(vp, game_state["turn"], game_state))
    game_state["_simulation_boundary"] = {
        "layer": "simulation",
        "phases": list(SIMULATION_PHASES),
        "turn": game_state.get("turn"),
    }
    return events


def boundary_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Expose boundary audit fields for /state and receipts."""
    sim = game_state.get("_simulation_boundary", {})
    mech = game_state.get("_mechanics_tick_audit", {})
    return {
        "simulation_layer": {
            "phases": sim.get("phases", list(SIMULATION_PHASES)),
            "last_turn": sim.get("turn"),
            "description": "Orchestrator-adjacent: map, alliances, negotiations, competition scoring, milestones",
        },
        "mechanics_layer": {
            "modules": mech.get("modules", []),
            "last_turn": mech.get("turn"),
            "description": "Pluggable rules via MechanicsRegistry.pass_through_tick() only",
        },
        "replacement_note": (
            "Simulation layer is not fully replaceable by registry today — multi_agent_state "
            "requires decisions context. Low-risk path: keep explicit simulation_layer; "
            "register additional rules as mechanics modules."
        ),
    }
