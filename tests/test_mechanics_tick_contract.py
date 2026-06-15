"""Tests for mechanics tick module contract."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.mechanics_registry import MechanicsRegistry  # noqa: E402
from core.mechanics_tick_contract import (  # noqa: E402
    coerce_tick_events,
    validate_game_state_for_tick,
    wrap_tick,
)


def _gs():
    return {"turn": 1, "player": {"resources": {"prod": 5}}}


def test_validate_game_state_for_tick_requires_turn_and_player():
    with pytest.raises(ValueError):
        validate_game_state_for_tick({})
    validate_game_state_for_tick(_gs())


def test_coerce_tick_events_normalizes_output():
    assert coerce_tick_events(None) == []
    assert coerce_tick_events(["a"]) == ["a"]
    with pytest.raises(ValueError):
        coerce_tick_events("bad")
    with pytest.raises(ValueError):
        coerce_tick_events([1])


def test_wrap_tick_enforces_contract():
    def bad_tick(gs):
        return [123]

    with pytest.raises(ValueError):
        wrap_tick(bad_tick)(_gs())

    def good_tick(gs):
        gs["player"]["resources"]["prod"] += 1
        return ["ok"]

    events = wrap_tick(good_tick)(_gs())
    assert events == ["ok"]


def test_registry_wraps_ticks_by_default():
    reg = MechanicsRegistry()

    def tick(gs):
        return [f"turn-{gs['turn']}"]

    reg.register("demo", tick)
    assert reg.tick_all(_gs()) == ["turn-1"]
