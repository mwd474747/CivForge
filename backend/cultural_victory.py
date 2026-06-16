"""Cultural victory path milestones (WP-GROK-CULTURAL-VICTORY-001)."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state
from backend.civstudy_metadata import default_cultural_event_chains


def _chains_all_complete(game_state: Dict[str, Any]) -> bool:
    sim = ensure_civstudy_sim_state(game_state)
    chains = sim.get("active_chains", {})
    for chain in default_cultural_event_chains():
        cid = chain["id"]
        state = chains.get(cid)
        if not state or not state.get("complete"):
            return False
    return bool(default_cultural_event_chains())


def evaluate_cultural_milestones(game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluate cultural path gates from live game state."""
    cultural = game_state.get("mechanics_lanes", {}).get("cultural", {})
    sim = ensure_civstudy_sim_state(game_state)
    influence = int(cultural.get("influence_spread", 0))
    wonders = sim.get("commissioned_wonders") or []

    checks = [
        {
            "id": "prestige_25",
            "label": "Cultural prestige spreads (25+ influence)",
            "done": influence >= 25,
            "progress": min(influence, 25),
            "target": 25,
        },
        {
            "id": "event_chain_mastery",
            "label": "Complete all cultural event chains",
            "done": _chains_all_complete(game_state),
        },
        {
            "id": "wonder_prestige",
            "label": "Commission a world wonder",
            "done": len(wonders) >= 1,
            "progress": len(wonders),
            "target": 1,
        },
    ]
    return checks


def sync_cultural_victory_path(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Update victory_progress.cultural_path from mechanics + sim state."""
    milestones = evaluate_cultural_milestones(game_state)
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
    vp["cultural_path"] = path
    return path
