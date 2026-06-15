"""Turn simulation orchestration — multi-agent + mechanics ticks + victory finalize."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from backend.multi_agent_state import sync_victory_milestones, tick_multi_agent_state
from core.mechanics_registry import MechanicsRegistry
from core.receipts import ReceiptStore


def run_turn_simulation(
    game_state: Dict[str, Any],
    registry: MechanicsRegistry,
    decisions: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Run civ + mechanics ticks, then post-tick victory milestone sync."""
    events: List[str] = []
    events.extend(tick_multi_agent_state(game_state, decisions or {}))
    events.extend(registry.tick_all(game_state))
    vp = game_state.setdefault("victory_progress", {})
    events.extend(sync_victory_milestones(vp, game_state["turn"]))
    return events


def enrich_cycle_receipt(receipt: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Attach victory snapshot to governance cycle receipt for audit trail."""
    vp = game_state.get("victory_progress", {})
    receipt["victory_progress"] = {
        "joint_progress": vp.get("joint_progress"),
        "target": vp.get("target"),
        "outcome": vp.get("outcome"),
        "milestones_done": sum(1 for m in vp.get("milestones", []) if m.get("done")),
    }
    return receipt


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
    }
    path = receipt_store.append(receipt, filename_hint="victory-outcome")
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Joint victory outcome logged — {path.name}."
    )
    return str(path)
