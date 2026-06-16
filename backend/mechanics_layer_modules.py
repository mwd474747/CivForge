"""Diplomacy + competition as MechanicsRegistry modules (WP-GROK-REFRACTOR-SIM-001)."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.ai_diplomacy import tick_ai_negotiation_proposals
from backend.competition_modes import tick_competition
from backend.multi_agent_state import tick_multi_agent_state
from core.mechanics_registry import MechanicsRegistry


def turn_decisions(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Read orchestrator decisions injected by run_turn_simulation."""
    raw = game_state.get("_turn_decisions")
    return raw if isinstance(raw, dict) else {}


def tick_diplomacy_layer(game_state: Dict[str, Any]) -> List[str]:
    events = tick_multi_agent_state(game_state, turn_decisions(game_state))
    events.extend(tick_ai_negotiation_proposals(game_state))
    return events


def tick_competition_layer(game_state: Dict[str, Any]) -> List[str]:
    return tick_competition(game_state, turn_decisions(game_state))


def register_layer_mechanics(registry: MechanicsRegistry) -> None:
    """Register map/alliance/negotiation and competition scoring as pluggable mechanics."""
    registry.register("diplomacy_layer", tick_diplomacy_layer)
    registry.register("competition", tick_competition_layer)
