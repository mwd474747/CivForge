"""Formal contract for MechanicsRegistry tick modules.

Every registered tick:
  - Receives the live ``game_state`` dict (mutate in place).
  - Returns a list of human-readable event strings (may be empty).
  - Must not raise for expected missing optional keys (registry catches unexpected errors).

See ``docs/MECHANICS_TICK_CONTRACT_V1.md``.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

TickFn = Callable[[Dict[str, Any]], List[str]]

REQUIRED_GAME_STATE_KEYS = ("turn", "player")
RECOMMENDED_GAME_STATE_KEYS = (
    "events",
    "victory_progress",
    "mechanics_lanes",
    "civstudy_sim",
    "map_tiles",
    "alliances",
    "negotiations",
)


def validate_game_state_for_tick(game_state: Dict[str, Any]) -> None:
    """Raise ValueError when required keys are absent or malformed."""
    if not isinstance(game_state, dict):
        raise ValueError("game_state must be a dict")
    for key in REQUIRED_GAME_STATE_KEYS:
        if key not in game_state:
            raise ValueError(f"game_state missing required key: {key}")
    if not isinstance(game_state["turn"], int):
        raise ValueError("game_state.turn must be int")
    player = game_state["player"]
    if not isinstance(player, dict):
        raise ValueError("game_state.player must be a dict")
    if "resources" not in player or not isinstance(player["resources"], dict):
        raise ValueError("game_state.player.resources must be a dict")


def coerce_tick_events(events: Any) -> List[str]:
    """Normalize tick output to a list of strings."""
    if events is None:
        return []
    if not isinstance(events, list):
        raise ValueError("tick must return a list of event strings")
    out: List[str] = []
    for item in events:
        if not isinstance(item, str):
            raise ValueError("tick events must be strings")
        out.append(item)
    return out


def wrap_tick(tick: TickFn) -> TickFn:
    """Wrap a tick function with input/output contract enforcement."""

    def wrapped(game_state: Dict[str, Any]) -> List[str]:
        validate_game_state_for_tick(game_state)
        return coerce_tick_events(tick(game_state))

    wrapped.__name__ = getattr(tick, "__name__", "tick")
    wrapped.__doc__ = tick.__doc__
    return wrapped
