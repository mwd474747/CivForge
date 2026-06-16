"""Agent competition modes, win resolution, autoplay, spectator log."""

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

AUTOPLAY_SPEED_MIN = 1
AUTOPLAY_SPEED_MAX = 3


def default_autoplay_state() -> Dict[str, Any]:
    return {
        "active": False,
        "paused": False,
        "speed": 1,
        "cooldown_turns": 2,
        "last_trigger_turn": 0,
    }


def default_competition_state() -> Dict[str, Any]:
    return {
        "mode": "none",
        "label": MODE_LABELS["none"],
        "turn_sync": True,
        "scores": {aid: 0 for aid in AGENT_IDS if aid != "player"},
        "player_score": 0,
        "win_condition_broadcast": None,
        "resolved": False,
        "winner": None,
        "resolved_at_turn": None,
        "spectator_log": [],
        "autoplay": default_autoplay_state(),
    }


def ensure_competition_state(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = game_state.setdefault("competition_mode", default_competition_state())
    comp.setdefault("spectator_log", [])
    comp.setdefault("scores", {aid: 0 for aid in AGENT_IDS if aid != "player"})
    comp.setdefault("player_score", 0)
    comp.setdefault("resolved", False)
    comp.setdefault("autoplay", default_autoplay_state())
    return comp


def _cooldown_for_speed(speed: int) -> int:
    speed = max(AUTOPLAY_SPEED_MIN, min(AUTOPLAY_SPEED_MAX, int(speed)))
    return max(0, AUTOPLAY_SPEED_MAX - speed)


def _spectator(game_state: Dict[str, Any], message: str) -> None:
    comp = ensure_competition_state(game_state)
    entry = {"turn": game_state.get("turn", 0), "message": message}
    comp["spectator_log"] = (comp.get("spectator_log") or [])[-49:] + [entry]


def _resolve_competition(
    game_state: Dict[str, Any],
    winner: str,
    message: str,
) -> None:
    comp = ensure_competition_state(game_state)
    comp["resolved"] = True
    comp["winner"] = winner
    comp["resolved_at_turn"] = game_state.get("turn", 0)
    comp["win_condition_broadcast"] = message
    autoplay = comp.setdefault("autoplay", default_autoplay_state())
    autoplay["active"] = False
    autoplay["paused"] = True
    _spectator(game_state, message)


def is_competition_resolved(game_state: Dict[str, Any]) -> bool:
    comp = ensure_competition_state(game_state)
    return bool(comp.get("resolved")) and comp.get("mode", "none") != "none"


def competition_blocks_advance(game_state: Dict[str, Any]) -> Optional[str]:
    if not is_competition_resolved(game_state):
        return None
    comp = ensure_competition_state(game_state)
    winner = comp.get("winner") or "unknown"
    return (
        f"Competition resolved ({comp.get('label', comp.get('mode'))}) — "
        f"winner: {winner}. POST /game/reset or change mode to continue."
    )


def set_competition_mode(game_state: Dict[str, Any], mode: str) -> Dict[str, Any]:
    if mode not in COMPETITION_MODES:
        return {"error": f"Invalid mode; choose from {COMPETITION_MODES}"}
    comp = ensure_competition_state(game_state)
    comp["mode"] = mode
    comp["label"] = MODE_LABELS.get(mode, mode)
    comp["win_condition_broadcast"] = _win_condition_for_mode(mode)
    comp["resolved"] = False
    comp["winner"] = None
    comp["resolved_at_turn"] = None
    comp["scores"] = {aid: 0 for aid in AGENT_IDS if aid != "player"}
    comp["player_score"] = 0
    comp["autoplay"] = default_autoplay_state()
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


def start_autoplay(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = ensure_competition_state(game_state)
    if comp.get("mode", "none") == "none":
        return {"error": "Set a competition mode before autoplay"}
    if is_competition_resolved(game_state):
        return {"error": "Competition already resolved"}
    autoplay = comp.setdefault("autoplay", default_autoplay_state())
    turn = game_state.get("turn", 1)
    if autoplay.get("active") and not autoplay.get("paused"):
        cooldown = int(autoplay.get("cooldown_turns", 1))
        last = int(autoplay.get("last_trigger_turn", 0))
        if turn - last < cooldown:
            return {
                "error": "autoplay cooldown",
                "cooldown_turns": cooldown,
                "turns_remaining": cooldown - (turn - last),
            }
    autoplay["active"] = True
    autoplay["paused"] = False
    autoplay["last_trigger_turn"] = turn
    _spectator(game_state, f"Autoplay started (speed {autoplay.get('speed', 1)}).")
    return {"ok": True, "autoplay": dict(autoplay), "competition": competition_summary(game_state)}


def pause_autoplay(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = ensure_competition_state(game_state)
    autoplay = comp.setdefault("autoplay", default_autoplay_state())
    autoplay["paused"] = True
    _spectator(game_state, "Autoplay paused.")
    return {"ok": True, "autoplay": dict(autoplay), "competition": competition_summary(game_state)}


def set_autoplay_speed(game_state: Dict[str, Any], speed: int) -> Dict[str, Any]:
    comp = ensure_competition_state(game_state)
    if comp.get("mode", "none") == "none":
        return {"error": "Set a competition mode before autoplay speed"}
    speed = max(AUTOPLAY_SPEED_MIN, min(AUTOPLAY_SPEED_MAX, int(speed)))
    autoplay = comp.setdefault("autoplay", default_autoplay_state())
    autoplay["speed"] = speed
    autoplay["cooldown_turns"] = _cooldown_for_speed(speed)
    return {"ok": True, "autoplay": dict(autoplay), "competition": competition_summary(game_state)}


def competition_status(game_state: Dict[str, Any]) -> Dict[str, Any]:
    comp = ensure_competition_state(game_state)
    autoplay = comp.get("autoplay") or default_autoplay_state()
    turn = game_state.get("turn", 1)
    cooldown = int(autoplay.get("cooldown_turns", 1))
    last = int(autoplay.get("last_trigger_turn", 0))
    turns_until_ready = max(0, cooldown - (turn - last)) if autoplay.get("active") else 0
    return {
        **competition_summary(game_state),
        "resolved": bool(comp.get("resolved")),
        "winner": comp.get("winner"),
        "resolved_at_turn": comp.get("resolved_at_turn"),
        "blocks_advance": is_competition_resolved(game_state),
        "autoplay": {
            **autoplay,
            "turns_until_ready": turns_until_ready,
            "can_start": turns_until_ready == 0 or not autoplay.get("active"),
        },
        "spectator_log": spectator_log(game_state, limit=20),
    }


def tick_competition(
    game_state: Dict[str, Any],
    decisions: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Score competition modes each simulation tick."""
    comp = ensure_competition_state(game_state)
    mode = comp.get("mode", "none")
    if mode == "none" or comp.get("resolved"):
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
            msg = f"Duel resolved — {winner} wins."
            _resolve_competition(game_state, winner, msg)
            events.append(f"Turn {turn}: {msg}")

    elif mode == "free_for_all":
        for aid in comp["scores"]:
            comp["scores"][aid] = comp["scores"].get(aid, 0) + 1
        if turn >= 30:
            top = max(comp["scores"], key=comp["scores"].get)
            msg = f"Tournament ends — {top} leads."
            _resolve_competition(game_state, top, msg)
            events.append(f"Turn {turn}: {msg}")

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
        if turn >= 40:
            winner = "Systems-Governance bloc" if bloc_a >= bloc_b else "Research-Diplomacy bloc"
            msg = f"League season complete — {winner} wins."
            _resolve_competition(game_state, winner, msg)
            events.append(f"Turn {turn}: {msg}")

    elif mode == "shared_victory_coop":
        comp["player_score"] = progress
        for aid in comp["scores"]:
            comp["scores"][aid] = comp["scores"].get(aid, 0) + (1 if aid in (decisions or {}) else 0)
        if progress >= 100:
            msg = "Co-op victory — joint progress complete."
            _resolve_competition(game_state, "player+allies", msg)
            events.append(f"Turn {turn}: {msg}")
        elif max(comp["scores"].values() or [0]) >= 60:
            top = max(comp["scores"], key=comp["scores"].get)
            msg = f"Co-op failed — rival {top} reached 60 solo points."
            _resolve_competition(game_state, top, msg)
            events.append(f"Turn {turn}: {msg}")

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
        "resolved": bool(comp.get("resolved")),
        "winner": comp.get("winner"),
        "resolved_at_turn": comp.get("resolved_at_turn"),
        "autoplay": dict(comp.get("autoplay") or default_autoplay_state()),
        "spectator_log_tail": (comp.get("spectator_log") or [])[-8:],
    }


def spectator_log(game_state: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
    comp = ensure_competition_state(game_state)
    return list((comp.get("spectator_log") or [])[-limit:])
