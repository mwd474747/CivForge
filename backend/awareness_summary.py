"""AI-oriented state summary for Grok awareness tooling (WP-TOOLING-AWARENESS-PROPOSAL-001)."""

from __future__ import annotations

from typing import Any, Dict

from backend.mechanics_status import mechanics_status_summary
from core.mechanics_registry import MechanicsRegistry


def build_awareness_summary(
    game_state: Dict[str, Any],
    registry: MechanicsRegistry,
    *,
    receipt_index: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Compact JSON snapshot: state slices + mechanics status + optional receipt index."""
    sim = game_state.get("civstudy_sim") or {}
    vp = game_state.get("victory_progress") or {}
    proposals = game_state.get("mechanics_proposals") or []
    if isinstance(proposals, dict):
        proposal_list = proposals.get("items") or proposals.get("proposals") or []
    else:
        proposal_list = proposals

    summary: Dict[str, Any] = {
        "schema": "civforge.awareness_summary.v1",
        "turn": game_state.get("turn") or game_state.get("current_turn"),
        "session_phase": game_state.get("session_phase"),
        "fun_score": (game_state.get("player") or {}).get("fun_score") or game_state.get("fun_score"),
        "player": {
            "resources": (game_state.get("player") or {}).get("resources"),
            "cities": (game_state.get("player") or {}).get("cities"),
            "territories": (game_state.get("player") or {}).get("territories"),
        },
        "victory_hud": game_state.get("victory_hud"),
        "victory_progress": {
            "joint_progress": vp.get("joint_progress"),
            "outcome": vp.get("outcome"),
            "victory_type": vp.get("victory_type"),
            "cultural_path": vp.get("cultural_path"),
            "domination_path": vp.get("domination_path"),
        },
        "mechanics_proposals": proposal_list[-8:] if isinstance(proposal_list, list) else proposal_list,
        "mechanics_overrides": game_state.get("mechanics_overrides") or {},
        "recent_receipts": (game_state.get("receipts") or [])[-5:],
        "recent_events": (game_state.get("events") or game_state.get("recent_events") or [])[-8:],
        "civstudy_anchors": {
            "active_district": sim.get("active_district"),
            "unlocked_policies": sim.get("unlocked_policies"),
            "unlocked_forks": sim.get("unlocked_forks"),
            "commissioned_wonders": sim.get("commissioned_wonders"),
            "policy_tree_checklist": (sim.get("policy_tree") or {}).get("checklist"),
        },
        "work_pack_registry": game_state.get("work_pack_registry"),
        "mechanics_status": mechanics_status_summary(game_state, registry),
    }
    if receipt_index is not None:
        summary["receipt_index"] = receipt_index
    return summary
