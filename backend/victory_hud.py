"""Victory / defeat / cultural path HUD summary (WP-GROK-VICTORY-UI-001)."""

from __future__ import annotations

from typing import Any, Dict

from backend.game_session import cultural_tick_cadence, session_phase
from backend.trust_erosion import TRUST_BETRAYAL_THRESHOLD, trust_summary

def victory_hud_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    from backend.alternate_victory import victory_type_label
    from backend.cultural_victory import sync_cultural_victory_path
    from backend.domination_victory import sync_domination_victory_path

    vp = game_state.get("victory_progress", {})
    cultural = game_state.get("mechanics_lanes", {}).get("cultural", {})
    sim = game_state.get("civstudy_sim", {})
    trust = trust_summary(game_state)
    fun = game_state.get("player", {}).get("fun_score", 100)
    progress = vp.get("joint_progress", 0)
    target = vp.get("target", 100)
    max_risk = trust.get("max_betrayal_risk", 0)
    cultural_path = sync_cultural_victory_path(game_state)
    domination_path = sync_domination_victory_path(game_state)

    warnings = []
    if fun < 45:
        warnings.append("fun_floor_risk")
    if max_risk >= TRUST_BETRAYAL_THRESHOLD:
        warnings.append("betrayal_risk_elevated")
    if progress <= 5 and game_state.get("turn", 1) >= 20:
        warnings.append("stalled_progress_risk")

    return {
        "session_phase": session_phase(game_state),
        "joint_progress": progress,
        "target": target,
        "progress_pct": round(100 * progress / target, 1) if target else 0,
        "milestones_done": sum(1 for m in vp.get("milestones", []) if m.get("done")),
        "milestones_total": len(vp.get("milestones", [])),
        "outcome": vp.get("outcome"),
        "victory_type": vp.get("victory_type"),
        "victory_type_label": victory_type_label(game_state),
        "epilogue_message": vp.get("epilogue_message"),
        "defeat_reason": vp.get("defeat_reason"),
        "cultural_path": {
            "event_chains": cultural.get("event_chains", 0),
            "influence_spread": cultural.get("influence_spread", 0),
            "tick_cadence": cultural_tick_cadence(game_state),
            "active_chain_count": len(sim.get("active_chains") or {}),
            "unlocked_policies": len(sim.get("policy_tree", {}).get("unlocked", [])),
            "commissioned_wonders": len(sim.get("commissioned_wonders") or []),
            "milestones": cultural_path.get("milestones", []),
            "progress_pct": cultural_path.get("progress_pct", 0),
            "alternate_victory_eligible": cultural_path.get("alternate_victory_eligible", False),
        },
        "domination_path": {
            "milestones": domination_path.get("milestones", []),
            "progress_pct": domination_path.get("progress_pct", 0),
            "alternate_victory_eligible": domination_path.get("alternate_victory_eligible", False),
        },
        "defeat_warning": bool(warnings) and session_phase(game_state) == "active",
        "defeat_warnings": warnings,
        "fun_score": fun,
    }
