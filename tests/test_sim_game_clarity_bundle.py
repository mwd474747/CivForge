"""Tests for WP-SIM-GAME-CLARITY + DEEP-DIVE + OVERLAP bundle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.agent_control import (  # noqa: E402
    default_agent_controls,
    issue_directive,
    select_agent,
    toggle_autonomy,
)
from backend.competition_modes import COMPETITION_MODES, set_competition_mode, tick_competition  # noqa: E402
from backend.corpus_card_registry import CorpusCardRegistry, get_corpus_card_registry  # noqa: E402
from backend.dashboard_components import get_dashboard_registry  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.simulation_boundary import boundary_summary, run_simulation_layer  # noqa: E402
from backend.telemetry_enrich import enrich_telemetry_payload  # noqa: E402
from backend.turn_simulation import run_turn_simulation  # noqa: E402
from core.mechanics_registry import build_default_registry  # noqa: E402


def test_agent_control_primitives():
    state = build_initial_game_state()
    assert len(default_agent_controls()["governors"]) == 4
    r = select_agent(state, "harper")
    assert r["active_agent_id"] == "harper"
    r2 = issue_directive(state, "harper", "Fortify the northern marches")
    assert r2["governor"]["last_directive"]
    r3 = toggle_autonomy(state, "harper", True)
    assert r3["autonomous"] is True


def test_competition_modes_registered():
    state = build_initial_game_state()
    for mode in ("pva_duel", "free_for_all", "alliance_league", "shared_victory_coop"):
        result = set_competition_mode(state, mode)
        assert result["ok"]
        assert state["competition_mode"]["mode"] == mode
    events = tick_competition(state, {"harper": "deploy"})
    assert isinstance(events, list)


def test_corpus_card_registry_extensibility():
    reg = CorpusCardRegistry()
    reg.register_card({"id": "test-wonder", "kind": "wonder", "name": "Test", "flavor": "x"})
    assert reg.get("test-wonder")["name"] == "Test"
    default_reg = get_corpus_card_registry()
    assert len(default_reg.all_cards()) >= 12


def test_dashboard_component_registry():
    reg = get_dashboard_registry()
    tabs = reg.tabs()
    panels = reg.panels()
    assert any(t["id"] == "mechanics" for t in tabs)
    assert any(p["id"] == "competition" for p in panels)


def test_telemetry_enrich_metadata_only():
    state = build_initial_game_state()
    set_competition_mode(state, "pva_duel")
    enriched = enrich_telemetry_payload(state, {"territories": 5})
    assert enriched["competitionMode"] == "pva_duel"
    assert "simulationBoundary" in enriched


def test_simulation_mechanics_boundary_on_turn():
    state = build_initial_game_state()
    reg = build_default_registry()
    run_turn_simulation(state, reg, {})
    summary = boundary_summary(state)
    assert summary["simulation_layer"]["phases"]
    assert summary["mechanics_layer"]["modules"]
    assert "diplomacy_layer" in summary["mechanics_layer"]["modules"]
    assert "military" in summary["mechanics_layer"]["modules"]
    assert summary["simulation_layer"]["phases"] == ["milestones"]


def test_simulation_layer_runs_without_registry():
    state = build_initial_game_state()
    run_simulation_layer(state)
    assert state.get("_simulation_boundary", {}).get("layer") == "simulation"
