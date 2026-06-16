"""Victory / defeat / cultural path HUD summary (WP-GROK-VICTORY-UI-001)."""

from __future__ import annotations

from typing import Any, Dict

from backend.game_session import cultural_tick_cadence, session_phase
from backend.trust_erosion import TRUST_BETRAYAL_THRESHOLD, trust_summary


def victory_hud_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    vp = game_state.get("victory_progress", {})
    cultural = game_state.get("mechanics_lanes", {}).get("cultural", {})
    sim = game_state.get("civstudy_sim", {})
    trust = trust_summary(game_state)
    fun = game_state.get("player", {}).get("fun_score", 100)
    progress = vp.get("joint_progress", 0)
    target = vp.get("target", 100)
    max_risk = trust.get("max_betrayal_risk", 0)

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
        "defeat_reason": vp.get("defeat_reason"),
        "cultural_path": {
            "event_chains": cultural.get("event_chains", 0),
            "influence_spread": cultural.get("influence_spread", 0),
            "tick_cadence": cultural_tick_cadence(game_state),
            "active_chain_count": len(sim.get("active_chains") or {}),
            "unlocked_policies": len(sim.get("policy_tree", {}).get("unlocked", [])),
        },
        "defeat_warning": bool(warnings) and session_phase(game_state) == "active",
        "defeat_warnings": warnings,
        "fun_score": fun,
    }
