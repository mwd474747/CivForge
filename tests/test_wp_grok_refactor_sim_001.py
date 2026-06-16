"""WP-GROK-REFRACTOR-SIM-001 — registry diplomacy/competition + milestone-only simulation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.competition_modes import set_competition_mode  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.mechanics_layer_modules import tick_diplomacy_layer, turn_decisions  # noqa: E402
from backend.simulation_boundary import SIMULATION_PHASES, TICK_ORDER, run_simulation_layer  # noqa: E402
from backend.turn_simulation import run_turn_simulation  # noqa: E402
from core.mechanics_registry import build_default_registry  # noqa: E402


def test_default_registry_includes_diplomacy_and_competition():
    reg = build_default_registry()
    names = reg.module_names()
    assert "diplomacy_layer" in names
    assert "competition" in names
    assert names.index("diplomacy_layer") < names.index("military")


def test_simulation_layer_is_milestones_only():
    state = build_initial_game_state()
    run_simulation_layer(state)
    assert state["_simulation_boundary"]["phases"] == list(SIMULATION_PHASES)
    assert state["_simulation_boundary"]["tick_order"] == TICK_ORDER


def test_turn_decisions_passthrough_to_diplomacy():
    state = build_initial_game_state()
    state["_turn_decisions"] = {"harper": "deploy"}
    assert turn_decisions(state) == {"harper": "deploy"}
    events = tick_diplomacy_layer(state)
    assert isinstance(events, list)


def test_tick_order_mechanics_before_milestones():
    state = build_initial_game_state()
    set_competition_mode(state, "pva_duel")
    reg = build_default_registry()
    before = state["competition_mode"]["scores"].get("harper", 0)
    run_turn_simulation(state, reg, {"harper": "deploy"})
    assert state["_simulation_boundary"]["tick_order"] == TICK_ORDER
    assert "diplomacy_layer" in state["_mechanics_tick_audit"]["modules"]
    assert "competition" in state["_mechanics_tick_audit"]["modules"]
    assert "_turn_decisions" not in state
    assert state["competition_mode"]["scores"]["harper"] >= before + 1


def test_milestones_sync_after_mechanics_progress():
    state = build_initial_game_state()
    state["victory_progress"]["joint_progress"] = 99
    reg = build_default_registry()

    def bump_progress(gs):
        gs["victory_progress"]["joint_progress"] = 100
        return ["bump"]

    reg.register("zz_bump", bump_progress)
    run_turn_simulation(state, reg, {})
    assert state["victory_progress"]["outcome"] == "victory"
