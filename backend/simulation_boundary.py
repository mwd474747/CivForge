"""Simulation vs game-mechanics boundary — orchestration layer only."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.multi_agent_state import sync_victory_milestones

SIMULATION_PHASES = ("milestones",)
TICK_ORDER = "mechanics_first_then_milestones"


def run_simulation_layer(game_state: Dict[str, Any]) -> List[str]:
    """Milestone coordination only — rule ticks run via MechanicsRegistry.pass_through_tick()."""
    events: List[str] = []
    vp = game_state.setdefault("victory_progress", {})
    events.extend(sync_victory_milestones(vp, game_state["turn"], game_state))
    game_state["_simulation_boundary"] = {
        "layer": "simulation",
        "phases": list(SIMULATION_PHASES),
        "turn": game_state.get("turn"),
        "tick_order": TICK_ORDER,
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
            "tick_order": sim.get("tick_order", TICK_ORDER),
            "description": "Orchestrator-adjacent: victory milestone sync after mechanics ticks",
        },
        "mechanics_layer": {
            "modules": mech.get("modules", []),
            "last_turn": mech.get("turn"),
            "description": "Pluggable rules via MechanicsRegistry.pass_through_tick() (incl. diplomacy_layer, competition)",
        },
        "replacement_note": (
            "Diplomacy and competition registered as mechanics modules (WP-GROK-REFRACTOR-SIM-001). "
            "Simulation layer retains milestone sync only; _turn_decisions passthrough supplies orchestrator context."
        ),
    }
