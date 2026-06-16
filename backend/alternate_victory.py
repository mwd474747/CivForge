"""Alternate victory paths — cultural epilogue + domination (Block C)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.cultural_victory import sync_cultural_victory_path
from backend.domination_victory import sync_domination_victory_path

VICTORY_TYPES = ("joint", "cultural_alternate", "domination")

EPILOGUE_MESSAGES = {
    "cultural_alternate": (
        "Cultural supremacy — every chain complete, wonders commissioned, "
        "and prestige spreads across rival courts."
    ),
    "domination": (
        "Military conquest — the map bends to your banners and legacy doctrine "
        "echoes through subdued city-states."
    ),
    "joint": "Joint victory — governance quorum achieved across rival courts.",
}


def _pick_alternate_type(cultural: Dict[str, Any], domination: Dict[str, Any]) -> Optional[str]:
    c_ok = cultural.get("alternate_victory_eligible")
    d_ok = domination.get("alternate_victory_eligible")
    if not c_ok and not d_ok:
        return None
    if c_ok and not d_ok:
        return "cultural_alternate"
    if d_ok and not c_ok:
        return "domination"
    if domination.get("progress_pct", 0) > cultural.get("progress_pct", 0):
        return "domination"
    return "cultural_alternate"


def sync_alternate_victory_outcomes(
    game_state: Dict[str, Any],
    turn: Optional[int] = None,
) -> List[str]:
    """Apply cultural/domination epilogue when eligible; joint path unchanged."""
    events: List[str] = []
    vp = game_state.setdefault("victory_progress", {})
    if vp.get("outcome") in ("victory", "defeat"):
        return events

    cultural = sync_cultural_victory_path(game_state)
    domination = sync_domination_victory_path(game_state)

    if vp.get("joint_progress", 0) >= vp.get("target", 100):
        return events

    victory_type = _pick_alternate_type(cultural, domination)
    if not victory_type:
        return events

    vp["outcome"] = "victory"
    vp["victory_type"] = victory_type
    vp["epilogue_message"] = EPILOGUE_MESSAGES[victory_type]
    prefix = f"Turn {turn}: " if turn is not None else ""
    events.append(
        f"{prefix}Alternate victory — {victory_type.replace('_', ' ')}. "
        f"{EPILOGUE_MESSAGES[victory_type]}"
    )
    return events


def victory_type_label(game_state: Dict[str, Any]) -> str:
    vp = game_state.get("victory_progress", {})
    vtype = vp.get("victory_type")
    if vtype == "cultural_alternate":
        return "Cultural Victory"
    if vtype == "domination":
        return "Domination Victory"
    if vp.get("outcome") == "victory":
        return "Joint Victory"
    return "In Progress"
