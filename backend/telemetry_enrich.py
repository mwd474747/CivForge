"""Optional metadata-only enrich hook for :8082 telemetry (thin-bridge safe)."""

from __future__ import annotations

from typing import Any, Dict

from backend.agent_control import agent_controls_summary
from backend.competition_modes import competition_summary
from backend.simulation_boundary import boundary_summary


def enrich_telemetry_payload(game_state: Dict[str, Any], base: Dict[str, Any]) -> Dict[str, Any]:
    """Merge game-state context into telemetry extra without mutating bridge authority."""
    enriched = dict(base)
    enriched["agentControls"] = {
        "active": agent_controls_summary(game_state).get("active_agent_id"),
        "playerOverride": agent_controls_summary(game_state).get("player_override"),
    }
    comp = competition_summary(game_state)
    enriched["competitionMode"] = comp.get("mode")
    enriched["competitionLabel"] = comp.get("label")
    enriched["competitionResolved"] = comp.get("resolved")
    enriched["competitionWinner"] = comp.get("winner")
    enriched["competitionAutoplayActive"] = (comp.get("autoplay") or {}).get("active")
    from backend.player_agent import player_agent_summary

    pa = player_agent_summary(game_state)
    enriched["playerStrategy"] = pa.get("strategy")
    enriched["playerStrategyLabel"] = pa.get("label")
    enriched["simulationBoundary"] = boundary_summary(game_state)
    return enriched
