"""Boundary enforcement — mechanics only via pass_through_tick (WP-SIM-GAME-OVERLAP-004)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import build_initial_game_state  # noqa: E402
from core.mechanics_registry import MechanicsRegistry, build_default_registry  # noqa: E402


def test_pass_through_tick_sets_audit():
    reg = build_default_registry()
    state = build_initial_game_state()
    reg.pass_through_tick(state)
    audit = state["_mechanics_tick_audit"]
    assert audit["layer"] == "mechanics"
    assert "military" in audit["modules"]
    assert "economic" in audit["modules"]


def test_registry_is_only_mechanics_entry_for_lanes():
    reg = MechanicsRegistry()
    touched = []

    def spy_tick(gs):
        touched.append("lane")
        gs.setdefault("mechanics_lanes", {})["military"] = {"strength": 99}
        return ["spy"]

    reg.register("spy", spy_tick)
    state = build_initial_game_state()
    reg.pass_through_tick(state)
    assert touched == ["lane"]
    assert state["mechanics_lanes"]["military"]["strength"] == 99


def test_default_registry_module_count():
    reg = build_default_registry()
    names = reg.module_names()
    assert len(names) >= 5
    assert "diplomacy_layer" in names
    assert "competition" in names
