"""Agent governor entities and player control primitives (WP-SIM-GAME-CLARITY-001)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.multi_agent_state import AGENT_IDS, AGENT_LABELS

DEFAULT_GOALS: Dict[str, str] = {
    "player": "empire_expansion",
    "harper": "systems_integration",
    "sebastian": "governance_quorum",
    "lysander": "science_dominance",
    "aris": "diplomatic_league",
}


def default_agent_controls() -> Dict[str, Any]:
    governors = []
    for aid in AGENT_IDS:
        if aid == "player":
            continue
        governors.append(
            {
                "agent_id": aid,
                "label": AGENT_LABELS.get(aid, aid),
                "goal": DEFAULT_GOALS.get(aid, "survival"),
                "control_level": "autonomous",
                "player_override": False,
                "score": 0,
                "last_directive": None,
            }
        )
    return {
        "active_agent_id": "player",
        "player_override": True,
        "governors": governors,
    }


def ensure_agent_controls(game_state: Dict[str, Any]) -> Dict[str, Any]:
    controls = game_state.setdefault("agent_controls", default_agent_controls())
    by_id = {g["agent_id"]: g for g in controls.get("governors", [])}
    for aid in AGENT_IDS:
        if aid == "player":
            continue
        if aid not in by_id:
            by_id[aid] = {
                "agent_id": aid,
                "label": AGENT_LABELS.get(aid, aid),
                "goal": DEFAULT_GOALS.get(aid, "survival"),
                "control_level": "autonomous",
                "player_override": False,
                "score": 0,
                "last_directive": None,
            }
    controls["governors"] = [by_id[aid] for aid in AGENT_IDS if aid != "player"]
    return controls


def _find_governor(controls: Dict[str, Any], agent_id: str) -> Optional[Dict[str, Any]]:
    for gov in controls.get("governors", []):
        if gov.get("agent_id") == agent_id:
            return gov
    return None


def select_agent(game_state: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
    controls = ensure_agent_controls(game_state)
    if agent_id not in AGENT_IDS:
        return {"error": f"Unknown agent_id: {agent_id}"}
    controls["active_agent_id"] = agent_id
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Court selects {AGENT_LABELS.get(agent_id, agent_id)} as active governor."
    )
    return {"ok": True, "active_agent_id": agent_id, "agent_controls": controls}


def issue_directive(game_state: Dict[str, Any], agent_id: str, directive: str) -> Dict[str, Any]:
    controls = ensure_agent_controls(game_state)
    gov = _find_governor(controls, agent_id)
    if not gov:
        return {"error": f"No governor for agent_id: {agent_id}"}
    gov["last_directive"] = directive.strip()[:240]
    gov["control_level"] = "directed"
    gov["player_override"] = True
    controls["player_override"] = True
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Directive to {gov['label']}: {directive[:80]}."
    )
    return {"ok": True, "governor": gov, "agent_controls": controls}


def toggle_autonomy(game_state: Dict[str, Any], agent_id: str, autonomous: bool) -> Dict[str, Any]:
    controls = ensure_agent_controls(game_state)
    gov = _find_governor(controls, agent_id)
    if not gov:
        return {"error": f"No governor for agent_id: {agent_id}"}
    gov["control_level"] = "autonomous" if autonomous else "directed"
    gov["player_override"] = not autonomous
    if autonomous:
        gov.pop("last_directive", None)
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: {gov['label']} autonomy "
        f"{'restored' if autonomous else 'suspended — player override active'}."
    )
    return {"ok": True, "governor": gov, "autonomous": autonomous, "agent_controls": controls}


def agent_controls_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    controls = ensure_agent_controls(game_state)
    return {
        "active_agent_id": controls.get("active_agent_id"),
        "player_override": controls.get("player_override"),
        "governors": controls.get("governors", []),
    }
