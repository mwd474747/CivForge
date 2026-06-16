"""Domination / conquest victory path (Block C — corpus military_conquest goal)."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.game_session import player_map_share

DOMINATION_MAP_SHARE_TARGET = 0.55
DOMINATION_LEGACY_TARGET = 5
DOMINATION_STRENGTH_TARGET = 70


def evaluate_domination_milestones(game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    military = game_state.get("mechanics_lanes", {}).get("military", {})
    map_share = player_map_share(game_state)
    legacy = int(military.get("legacy_points", 0))
    strength = int(military.get("strength", 0))

    return [
        {
            "id": "map_dominance",
            "label": f"Hold {int(DOMINATION_MAP_SHARE_TARGET * 100)}%+ of the map",
            "done": map_share >= DOMINATION_MAP_SHARE_TARGET,
            "progress": round(map_share * 100, 1),
            "target": round(DOMINATION_MAP_SHARE_TARGET * 100, 1),
        },
        {
            "id": "military_legacy",
            "label": f"Earn {DOMINATION_LEGACY_TARGET}+ military legacy points",
            "done": legacy >= DOMINATION_LEGACY_TARGET,
            "progress": legacy,
            "target": DOMINATION_LEGACY_TARGET,
        },
        {
            "id": "force_projection",
            "label": f"Military strength {DOMINATION_STRENGTH_TARGET}+",
            "done": strength >= DOMINATION_STRENGTH_TARGET,
            "progress": strength,
            "target": DOMINATION_STRENGTH_TARGET,
        },
    ]


def sync_domination_victory_path(game_state: Dict[str, Any]) -> Dict[str, Any]:
    milestones = evaluate_domination_milestones(game_state)
    done_count = sum(1 for m in milestones if m.get("done"))
    total = len(milestones) or 1
    path = {
        "milestones": milestones,
        "progress_pct": round(100 * done_count / total, 1),
        "milestones_done": done_count,
        "milestones_total": total,
        "alternate_victory_eligible": done_count == total,
    }
    vp = game_state.setdefault("victory_progress", {})
    vp["domination_path"] = path
    return path
