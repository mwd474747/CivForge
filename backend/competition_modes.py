"""Agent competition modes and spectator log (WP-SIM-GAME-CLARITY-001)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.multi_agent_state import AGENT_IDS

COMPETITION_MODES = (
    "none",
    "pva_duel",
    "free_for_all",
    "alliance_league",
    "shared_victory_coop",
)

MODE_LABELS = {
    "none": "Standard Campaign",
    "pva_duel": "PvA Duel",
    "free_for_all": "Free-For-All Tournament",
    "alliance_league": "Alliance League",
    "shared_victory_coop": "Shared-Victory Co-op",
}


def default_competition_state() -> Dict[str, Any]:
    return {
        "mode": "none",
        "label": MODE_LABELS["none"],
        "turn_sync": True,
        "scores": {aid: 0 for aid in AGENT_IDS if aid != "player"},
        "player_score": 0,
        "win_condition_broadcast": None,
        "spectator_log": [],
    }


def ensure_competition_state(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = game_state.setdefault("competition_mode", default_competition_state())
    comp.setdefault("spectator_log", [])
    comp.setdefault("scores", {aid: 0 for aid in AGENT_IDS if aid != "player"})
    comp.setdefault("player_score", 0)
    return comp


def set_competition_mode(game_state: Dict[str, Any], mode: str) -> Dict[str, Any]:
    if mode not in COMPETITION_MODES:
        return {"error": f"Invalid mode; choose from {COMPETITION_MODES}"}
    comp = ensure_competition_state(game_state)
    comp["mode"] = mode
    comp["label"] = MODE_LABELS.get(mode, mode)
    comp["win_condition_broadcast"] = _win_condition_for_mode(mode)
    msg = f"Competition mode set: {comp['label']}."
    _spectator(game_state, msg)
    game_state.setdefault("events", []).append(f"Turn {game_state['turn']}: {msg}")
    return {"ok": True, "competition_mode": competition_summary(game_state)}


def _win_condition_for_mode(mode: str) -> Optional[str]:
    return {
        "pva_duel": "First to 50 duel points between player and active rival wins the bout.",
        "free_for_all": "Highest aggregate score among all rival governors at turn 30.",
        "alliance_league": "Alliance bloc with highest combined score wins the league season.",
        "shared_victory_coop": "Joint victory progress ≥100 before any rival reaches 60 solo points.",
        "none": None,
    }.get(mode)


def _spectator(game_state: Dict[str, Any], message: str) -> None:
    comp = ensure_competition_state(game_state)
    entry = {"turn": game_state.get("turn", 0), "message": message}
    comp["spectator_log"] = (comp.get("spectator_log") or [])[-49:] + [entry]


def tick_competition(
    game_state: Dict[str, Any],
    decisions: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Score competition modes each simulation tick."""
    comp = ensure_competition_state(game_state)
    mode = comp.get("mode", "none")
    if mode == "none":
        return []

    events: List[str] = []
    turn = game_state.get("turn", 1)
    vp = game_state.get("victory_progress", {})
    progress = vp.get("joint_progress", 0)

    if mode == "pva_duel":
        rival = "harper"
        comp["scores"][rival] = comp["scores"].get(rival, 0) + 1
        comp["player_score"] = comp.get("player_score", 0) + (1 if decisions else 0)
        if comp["player_score"] >= 50 or comp["scores"].get(rival, 0) >= 50:
            winner = "player" if comp["player_score"] >= 50 else rival
            comp["win_condition_broadcast"] = f"Duel resolved — {winner} wins."
            _spectator(game_state, comp["win_condition_broadcast"])
            events.append(f"Turn {turn}: {comp['win_condition_broadcast']}")

    elif mode == "free_for_all":
        for aid in comp["scores"]:
            comp["scores"][aid] = comp["scores"].get(aid, 0) + 1
        if turn >= 30:
            top = max(comp["scores"], key=comp["scores"].get)
            comp["win_condition_broadcast"] = f"Tournament ends — {top} leads."
            _spectator(game_state, comp["win_condition_broadcast"])
            events.append(f"Turn {turn}: {comp['win_condition_broadcast']}")

    elif mode == "alliance_league":
        bloc_a = sum(comp["scores"].get(a, 0) for a in ("harper", "sebastian"))
        bloc_b = sum(comp["scores"].get(a, 0) for a in ("lysander", "aris"))
        comp["scores"]["harper"] = comp["scores"].get("harper", 0) + 1
        comp["scores"]["lysander"] = comp["scores"].get("lysander", 0) + 1
        if turn % 10 == 0:
            lead = "Systems-Governance bloc" if bloc_a >= bloc_b else "Research-Diplomacy bloc"
            msg = f"League standings — {lead} ahead (A:{bloc_a} B:{bloc_b})."
            _spectator(game_state, msg)
            events.append(f"Turn {turn}: {msg}")

    elif mode == "shared_victory_coop":
        comp["player_score"] = progress
        for aid in comp["scores"]:
            comp["scores"][aid] = comp["scores"].get(aid, 0) + (1 if aid in (decisions or {}) else 0)
        if progress >= 100:
            comp["win_condition_broadcast"] = "Co-op victory — joint progress complete."
            _spectator(game_state, comp["win_condition_broadcast"])
            events.append(f"Turn {turn}: {comp['win_condition_broadcast']}")

    return events


def competition_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = ensure_competition_state(game_state)
    return {
        "mode": comp.get("mode"),
        "label": comp.get("label"),
        "turn_sync": comp.get("turn_sync", True),
        "scores": dict(comp.get("scores", {})),
        "player_score": comp.get("player_score", 0),
        "win_condition_broadcast": comp.get("win_condition_broadcast"),
        "spectator_log_tail": (comp.get("spectator_log") or [])[-8:],
    }


def spectator_log(game_state: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
    comp = ensure_competition_state(game_state)
    return list((comp.get("spectator_log") or [])[-limit:])
