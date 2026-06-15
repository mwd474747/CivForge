"""Fresh game state factory and reset helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from backend.civstudy_mechanics_bridge import default_civstudy_sim_state, ensure_civstudy_sim_state
from backend.multi_agent_state import (
    default_alliances,
    default_map_tiles,
    default_negotiations,
    default_victory_progress,
    ensure_multi_agent_state,
)
from core.mechanics_registry import default_mechanics_lanes
from core.orchestrator import GovernanceOrchestrator


def build_initial_game_state() -> Dict[str, Any]:
    """Canonical new-game snapshot (matches kernel boot defaults)."""
    return {
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
        "map_tiles": default_map_tiles(),
        "alliances": default_alliances(),
        "negotiations": default_negotiations(),
        "victory_progress": default_victory_progress(),
        "mechanics_lanes": default_mechanics_lanes(),
        "civstudy_sim": default_civstudy_sim_state(),
    }


def apply_game_reset(game_state: Dict[str, Any], orchestrator: GovernanceOrchestrator) -> Dict[str, Any]:
    """Replace live state and orchestrator working memory with a fresh game."""
    prior_turn = game_state.get("turn", 0)
    prior_outcome = game_state.get("victory_progress", {}).get("outcome")

    fresh = build_initial_game_state()
    game_state.clear()
    game_state.update(deepcopy(fresh))
    ensure_multi_agent_state(game_state)
    ensure_civstudy_sim_state(game_state)

    orchestrator.turn = 1
    orchestrator.receipts = []
    orchestrator.events = []
    orchestrator.workstream_resources = {"prod": 12, "sci": 8, "verify": 6, "deploy_budget": 5}
    orchestrator.gate.proposals = []

    game_state["events"].append(
        f"Turn 1: Game reset — prior run ended at turn {prior_turn}"
        + (f" (outcome={prior_outcome})" if prior_outcome else "") + "."
    )

    return {
        "prior_turn": prior_turn,
        "prior_outcome": prior_outcome,
        "turn": game_state["turn"],
        "victory_progress": game_state["victory_progress"],
    }
