"""MechanicsRegistry — pluggable military / economic / cultural modules.

Extensions register tick handlers; advance_turn runs them after governance cycle.
"""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List

TickFn = Callable[[Dict[str, Any]], List[str]]


class MechanicsRegistry:
    def __init__(self) -> None:
        self._modules: Dict[str, TickFn] = {}

    def register(self, name: str, tick: TickFn) -> None:
        self._modules[name] = tick

    def tick_all(self, game_state: Dict[str, Any]) -> List[str]:
        events: List[str] = []
        for name, tick in self._modules.items():
            try:
                events.extend(tick(game_state) or [])
            except Exception as exc:  # noqa: BLE001
                events.append(f"Mechanics {name} tick error: {exc}")
        return events


def default_mechanics_lanes() -> Dict[str, Any]:
    return {
        "military": {
            "strength": 42,
            "legacy_points": 3,
            "garrisons": 2,
            "recent": ["Border patrol reinforced", "Legacy doctrine review"],
        },
        "economic": {
            "institutions": 2,
            "trade_routes": 1,
            "yield_bonus_pct": 10,
            "recent": ["Production guild chartered", "Sci-trade route opened"],
        },
        "cultural": {
            "event_chains": 1,
            "influence_spread": 12,
            "recent": ["Festival of Receipts", "Cross-faction symposium"],
        },
    }


def _tick_military(game_state: Dict[str, Any]) -> List[str]:
    lane = game_state.setdefault("mechanics_lanes", default_mechanics_lanes())["military"]
    turn = game_state["turn"]
    lane["strength"] = min(100, lane.get("strength", 40) + random.randint(0, 2))
    if turn % 5 == 0:
        lane["legacy_points"] = lane.get("legacy_points", 0) + 1
        msg = f"Turn {turn}: Military legacy point earned (total {lane['legacy_points']})."
        lane.setdefault("recent", []).insert(0, msg)
        return [msg]
    return []


def _tick_economic(game_state: Dict[str, Any]) -> List[str]:
    lane = game_state.setdefault("mechanics_lanes", default_mechanics_lanes())["economic"]
    turn = game_state["turn"]
    if turn % 4 == 0:
        lane["institutions"] = lane.get("institutions", 1) + 1
        msg = f"Turn {turn}: Economic institution founded (#{lane['institutions']})."
        lane.setdefault("recent", []).insert(0, msg)
        return [msg]
    return []


def _tick_cultural(game_state: Dict[str, Any]) -> List[str]:
    lane = game_state.setdefault("mechanics_lanes", default_mechanics_lanes())["cultural"]
    turn = game_state["turn"]
    lane["influence_spread"] = min(100, lane.get("influence_spread", 10) + random.randint(0, 3))
    if turn % 6 == 0:
        lane["event_chains"] = lane.get("event_chains", 0) + 1
        msg = f"Turn {turn}: Cultural event chain started (#{lane['event_chains']})."
        lane.setdefault("recent", []).insert(0, msg)
        return [msg]
    return []


def build_default_registry() -> MechanicsRegistry:
    reg = MechanicsRegistry()
    reg.register("military", _tick_military)
    reg.register("economic", _tick_economic)
    reg.register("cultural", _tick_cultural)
    try:
        from backend.civstudy_mechanics_bridge import register_civstudy_mechanics

        register_civstudy_mechanics(reg)
    except ImportError:
        pass
    return reg
