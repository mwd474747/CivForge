"""Machine-readable mechanics registry status (WP-TOOLING-AWARENESS-001)."""

from __future__ import annotations

from typing import Any, Dict

from backend.game_session import session_phase
from backend.simulation_boundary import SIMULATION_PHASES, TICK_ORDER, boundary_summary
from core.mechanics_registry import MechanicsRegistry


def mechanics_status_summary(
    game_state: Dict[str, Any],
    registry: MechanicsRegistry,
) -> Dict[str, Any]:
    audit = game_state.get("_mechanics_tick_audit", {})
    sim = game_state.get("_simulation_boundary", {})
    vp = game_state.get("victory_progress", {})
    return {
        "registry_modules": registry.module_names(),
        "mechanics_layer": {
            "last_turn": audit.get("turn"),
            "modules_last_tick": audit.get("modules", []),
        },
        "simulation_layer": {
            "phases": list(sim.get("phases", SIMULATION_PHASES)),
            "tick_order": sim.get("tick_order", TICK_ORDER),
            "last_turn": sim.get("turn"),
        },
        "tick_order": TICK_ORDER,
        "turn": game_state.get("turn"),
        "session_phase": session_phase(game_state),
        "victory_paths": {
            "joint_progress": vp.get("joint_progress"),
            "cultural_eligible": (vp.get("cultural_path") or {}).get("alternate_victory_eligible"),
            "domination_eligible": (vp.get("domination_path") or {}).get("alternate_victory_eligible"),
        },
        "boundary": boundary_summary(game_state),
    }
