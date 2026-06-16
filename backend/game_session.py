"""Session phase, negotiation costs, and milestone truth helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

BASE_NEGOTIATE_INFLUENCE_COST = 2
ALLIANCE_SOFT_CAP_DEFAULT = 2
ALLIANCE_SOFT_CAP_WITH_POLICY = 3
PLAYER_MAP_CONTROL_THRESHOLD = 0.40

DISTRICT_SELECT_INFLUENCE_COST = 3
MAP_CLAIM_INFLUENCE_COST = 4
POLICY_UNLOCK_INFLUENCE_COST = {1: 5, 2: 8, 3: 12}

DEFEAT_FUN_FLOOR = 35.0
BETRAYAL_WATCH_THRESHOLD = 65
BETRAYAL_COLLAPSE_THRESHOLD = 100
RECEIPT_QUORUM_VERIFY_MIN = 7
RECEIPT_QUORUM_PROGRESS_BONUS = 2
TRADE_ROUTE_SCI_BONUS = 1


def session_phase(game_state: Dict[str, Any]) -> str:
    """active | epilogue | defeat"""
    outcome = game_state.get("victory_progress", {}).get("outcome")
    if outcome == "defeat":
        return "defeat"
    if outcome == "victory":
        return "epilogue"
    return "active"


def policy_flags(game_state: Dict[str, Any]) -> Dict[str, Any]:
    return game_state.get("civstudy_sim", {}).get("policy_tree", {}).get("policy_flags", {})


def unlocked_forks(game_state: Dict[str, Any]) -> set:
    return set(game_state.get("civstudy_sim", {}).get("unlocked_forks", []))


def receipt_quorum_active(game_state: Dict[str, Any]) -> bool:
    return "receipt-quorum" in unlocked_forks(game_state)


def trade_route_sci_active(game_state: Dict[str, Any]) -> bool:
    if policy_flags(game_state).get("trade_route_map"):
        return True
    eco = game_state.get("mechanics_lanes", {}).get("economic", {})
    return eco.get("trade_routes", 0) > 0


def negotiation_influence_cost(game_state: Dict[str, Any]) -> int:
    if policy_flags(game_state).get("open_negotiation"):
        return 0
    return BASE_NEGOTIATE_INFLUENCE_COST


def player_alliance_count(game_state: Dict[str, Any]) -> int:
    return sum(
        1
        for alliance in game_state.get("alliances", [])
        if "player" in alliance.get("parties", [])
        and alliance.get("status") in ("active", "provisional")
    )


def player_map_share(game_state: Dict[str, Any]) -> float:
    tiles = game_state.get("map_tiles", [])
    if not tiles:
        return 0.0
    owned = sum(1 for tile in tiles if tile.get("owner") == "player")
    return owned / len(tiles)


def governance_quorum_met(game_state: Dict[str, Any]) -> bool:
    player_alliances = [
        alliance
        for alliance in game_state.get("alliances", [])
        if "player" in alliance.get("parties", [])
        and alliance.get("status") in ("active", "provisional")
    ]
    if len(player_alliances) >= 2:
        return True
    if receipt_quorum_active(game_state):
        resources = game_state.get("player", {}).get("resources", {})
        if resources.get("verify_budget", 0) >= receipt_quorum_verify_min(game_state):
            return True
    factions = {party for alliance in player_alliances for party in alliance.get("parties", [])}
    return len(factions) >= 3


def alliance_soft_cap(game_state: Dict[str, Any]) -> int:
    if policy_flags(game_state).get("alliance_cap_3"):
        return ALLIANCE_SOFT_CAP_WITH_POLICY
    return ALLIANCE_SOFT_CAP_DEFAULT


def milestone_truth(game_state: Dict[str, Any], vp: Dict[str, Any]) -> Dict[int, bool]:
    progress = vp.get("joint_progress", 0)
    target = vp.get("target", 100)
    return {
        0: player_alliance_count(game_state) >= 1,
        1: player_map_share(game_state) >= PLAYER_MAP_CONTROL_THRESHOLD or progress >= 25,
        2: governance_quorum_met(game_state) or progress >= 60,
        3: progress >= target,
    }


def cultural_tick_cadence(game_state: Dict[str, Any]) -> int:
    overrides = game_state.get("mechanics_overrides", {})
    cadence = overrides.get("cultural_cadence")
    if isinstance(cadence, int) and cadence >= 2:
        return cadence
    if policy_flags(game_state).get("symposium_chain"):
        return 4
    return 6


def trade_route_sci_bonus(game_state: Dict[str, Any]) -> int:
    from backend.mechanics_proposals import session_param

    return int(session_param(game_state, "trade_route_sci_bonus", TRADE_ROUTE_SCI_BONUS))


def receipt_quorum_progress_bonus(game_state: Dict[str, Any]) -> int:
    from backend.mechanics_proposals import session_param

    return int(session_param(game_state, "receipt_quorum_progress_bonus", RECEIPT_QUORUM_PROGRESS_BONUS))


def receipt_quorum_verify_min(game_state: Dict[str, Any]) -> int:
    from backend.mechanics_proposals import session_param

    return int(session_param(game_state, "receipt_quorum_verify_min", RECEIPT_QUORUM_VERIFY_MIN))


def check_defeat_conditions(game_state: Dict[str, Any]) -> Optional[str]:
    """Return defeat reason or None."""
    vp = game_state.get("victory_progress", {})
    if vp.get("outcome") in ("victory", "defeat"):
        return None

    player = game_state.get("player", {})
    fun = player.get("fun_score", 100)
    if fun < DEFEAT_FUN_FLOOR:
        return "fun_floor"

    progress = vp.get("joint_progress", 0)
    turn = game_state.get("turn", 1)
    if player_alliance_count(game_state) == 0 and progress < 30 and turn >= 8:
        return "diplomatic_isolation"

    broken_player = sum(
        1
        for alliance in game_state.get("alliances", [])
        if "player" in alliance.get("parties", []) and alliance.get("status") == "broken"
    )
    if broken_player >= 2 and progress < 40:
        return "betrayal_collapse"

    if progress <= 5 and turn >= 25:
        return "stalled_progress"

    return None


def apply_defeat(game_state: Dict[str, Any], reason: str, turn: Optional[int] = None) -> None:
    vp = game_state.setdefault("victory_progress", {})
    vp["outcome"] = "defeat"
    vp["defeat_reason"] = reason
    prefix = f"Turn {turn}: " if turn is not None else ""
    game_state.setdefault("events", []).append(f"{prefix}Defeat — {reason.replace('_', ' ')}.")
