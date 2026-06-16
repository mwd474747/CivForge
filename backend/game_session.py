"""Session phase, negotiation costs, and milestone truth helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

BASE_NEGOTIATE_INFLUENCE_COST = 2
ALLIANCE_SOFT_CAP_DEFAULT = 2
ALLIANCE_SOFT_CAP_WITH_POLICY = 3
PLAYER_MAP_CONTROL_THRESHOLD = 0.40


def session_phase(game_state: Dict[str, Any]) -> str:
    """active — normal play; epilogue — joint victory reached, advance blocked until reset."""
    if game_state.get("victory_progress", {}).get("outcome") == "victory":
        return "epilogue"
    return "active"


def policy_flags(game_state: Dict[str, Any]) -> Dict[str, Any]:
    return game_state.get("civstudy_sim", {}).get("policy_tree", {}).get("policy_flags", {})


def negotiation_influence_cost(game_state: Dict[str, Any]) -> int:
    """Influence cost to open a player negotiation (open_negotiation policy waives cost)."""
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
    """Player participates in multiple alliances or spans three factions."""
    player_alliances = [
        alliance
        for alliance in game_state.get("alliances", [])
        if "player" in alliance.get("parties", [])
        and alliance.get("status") in ("active", "provisional")
    ]
    if len(player_alliances) >= 2:
        return True
    factions = {party for alliance in player_alliances for party in alliance.get("parties", [])}
    return len(factions) >= 3


def alliance_soft_cap(game_state: Dict[str, Any]) -> int:
    if policy_flags(game_state).get("alliance_cap_3"):
        return ALLIANCE_SOFT_CAP_WITH_POLICY
    return ALLIANCE_SOFT_CAP_DEFAULT


def milestone_truth(
    game_state: Dict[str, Any],
    vp: Dict[str, Any],
) -> Dict[int, bool]:
    """Map milestone index → whether live game conditions satisfy it."""
    progress = vp.get("joint_progress", 0)
    target = vp.get("target", 100)
    return {
        0: player_alliance_count(game_state) >= 1,
        1: player_map_share(game_state) >= PLAYER_MAP_CONTROL_THRESHOLD or progress >= 25,
        2: governance_quorum_met(game_state) or progress >= 60,
        3: progress >= target,
    }


def cultural_tick_cadence(game_state: Dict[str, Any]) -> int:
    """Turn modulus for cultural chain ticks (symposium_chain starts chains earlier)."""
    if policy_flags(game_state).get("symposium_chain"):
        return 4
    return 6
