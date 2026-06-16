"""Turn simulation orchestration — multi-agent + mechanics ticks + victory finalize."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from backend.civstudy_flavor import defeat_receipt_title, victory_receipt_title
from backend.simulation_boundary import run_simulation_layer
from core.mechanics_registry import MechanicsRegistry
from core.receipts import ReceiptStore


def run_turn_simulation(
    game_state: Dict[str, Any],
    registry: MechanicsRegistry,
    decisions: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Mechanics first, then milestone sync (WP-GROK-REFRACTOR-SIM-001)."""
    events: List[str] = []
    game_state["_turn_decisions"] = dict(decisions or {})
    try:
        events.extend(registry.pass_through_tick(game_state))
        events.extend(run_simulation_layer(game_state))
    finally:
        game_state.pop("_turn_decisions", None)
    return events


def enrich_cycle_receipt(receipt: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Attach victory snapshot to governance cycle receipt for audit trail."""
    vp = game_state.get("victory_progress", {})
    receipt["victory_progress"] = {
        "joint_progress": vp.get("joint_progress"),
        "target": vp.get("target"),
        "outcome": vp.get("outcome"),
        "defeat_reason": vp.get("defeat_reason"),
        "milestones_done": sum(1 for m in vp.get("milestones", []) if m.get("done")),
    }
    return receipt


def maybe_emit_defeat_receipt(
    defeat_before: Optional[str],
    game_state: Dict[str, Any],
    receipt_store: ReceiptStore,
) -> Optional[str]:
    vp = game_state.get("victory_progress", {})
    reason = vp.get("defeat_reason")
    if vp.get("outcome") != "defeat" or not reason:
        return None
    if defeat_before == "defeat":
        return None

    player = game_state.get("player", {})
    receipt = {
        "turn": game_state["turn"],
        "action": "session_defeat",
        "status": "DEFEAT",
        "outcome": "defeat",
        "defeat_reason": reason,
        "fun_score": player.get("fun_score", 0),
        "victory_progress": deepcopy(vp),
        "receipt_title": defeat_receipt_title({
            "defeat_reason": reason,
            "turn": game_state["turn"],
        }),
    }
    path = receipt_store.append(receipt, filename_hint="defeat-outcome")
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Empire Council records the fall of the realm — {path.name}."
    )
    return str(path)


def maybe_emit_victory_receipt(
    victory_before: Dict[str, Any],
    game_state: Dict[str, Any],
    receipt_store: ReceiptStore,
) -> Optional[str]:
    """Write a one-time victory-outcome receipt when outcome first becomes victory."""
    vp = game_state.get("victory_progress", {})
    if vp.get("outcome") != "victory":
        return None
    if victory_before.get("outcome") == "victory":
        return None

    player = game_state.get("player", {})
    receipt = {
        "turn": game_state["turn"],
        "action": "joint_victory",
        "status": "VICTORY",
        "fun_score": player.get("fun_score", 0),
        "outcome": "victory",
        "victory_progress": deepcopy(vp),
        "alliances_count": len(game_state.get("alliances", [])),
        "negotiations_pending": sum(
            1 for n in game_state.get("negotiations", []) if n.get("status") == "pending"
        ),
        "policy_unlocked": list(
            game_state.get("civstudy_sim", {}).get("policy_tree", {}).get("unlocked", [])
        ),
        "receipt_title": victory_receipt_title({}),
    }
    path = receipt_store.append(receipt, filename_hint="victory-outcome")
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Empire Council proclaims an age of glory — {path.name}."
    )
    return str(path)
