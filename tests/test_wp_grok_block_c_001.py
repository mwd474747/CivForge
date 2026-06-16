"""Block C — alternate victory, soak, AI diplomacy, domination, tooling."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.ai_diplomacy import tick_ai_negotiation_proposals  # noqa: E402
from backend.civstudy_metadata import default_cultural_event_chains  # noqa: E402
from backend.domination_victory import sync_domination_victory_path  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.game_session import session_phase  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.simulation_boundary import TICK_ORDER, run_simulation_layer  # noqa: E402
from backend.turn_simulation import maybe_emit_victory_receipt, run_turn_simulation  # noqa: E402
from core.mechanics_registry import build_default_registry  # noqa: E402
from core.receipts import ReceiptStore  # noqa: E402


def _complete_cultural(state):
    sim = state["civstudy_sim"]
    for chain in default_cultural_event_chains():
        sim["active_chains"][chain["id"]] = {
            "stage_idx": len(chain["stages"]),
            "complete": True,
        }
    state["mechanics_lanes"]["cultural"]["influence_spread"] = 30
    sim["commissioned_wonders"] = [{"wonder_id": "wonder-oracle", "turn": 1}]


def _complete_domination(state):
    for tile in state["map_tiles"]:
        tile["owner"] = "player"
    state["mechanics_lanes"]["military"]["legacy_points"] = 6
    state["mechanics_lanes"]["military"]["strength"] = 75


def test_cultural_alternate_triggers_epilogue_and_receipt(tmp_path: Path):
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 12
    _complete_cultural(state)
    before = dict(state["victory_progress"])
    events = run_simulation_layer(state)
    assert state["victory_progress"]["outcome"] == "victory"
    assert state["victory_progress"]["victory_type"] == "cultural_alternate"
    assert state["victory_progress"].get("epilogue_message")
    assert session_phase(state) == "epilogue"
    assert any("Alternate victory" in e for e in events)
    store = ReceiptStore(base_dir=tmp_path)
    path = maybe_emit_victory_receipt(before, state, store)
    assert path is not None
    assert list(tmp_path.glob("victory-outcome-*.md"))


def test_domination_alternate_victory(tmp_path: Path):
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 20
    _complete_domination(state)
    path = sync_domination_victory_path(state)
    assert path["alternate_victory_eligible"] is True
    before = dict(state["victory_progress"])
    run_simulation_layer(state)
    assert state["victory_progress"]["victory_type"] == "domination"
    store = ReceiptStore(base_dir=tmp_path)
    assert maybe_emit_victory_receipt(before, state, store)


def test_joint_victory_still_wins_at_100():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["victory_progress"]["joint_progress"] = 100
    run_simulation_layer(state)
    assert state["victory_progress"]["victory_type"] == "joint"


def test_ai_negotiation_proposal_to_player():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 4
    random.seed(7)
    events = tick_ai_negotiation_proposals(state)
    pending = [n for n in state["negotiations"] if n.get("to") == "player" and n.get("status") == "pending"]
    assert pending or events


@pytest.mark.parametrize("turn_count", [50, 75])
def test_soak_no_boundary_regression(turn_count: int):
    random.seed(turn_count)
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    registry = build_default_registry()
    for _ in range(turn_count):
        state["turn"] += 1
        run_turn_simulation(state, registry, {})
        boundary = state.get("_simulation_boundary", {})
        assert boundary.get("tick_order") == TICK_ORDER
        assert "alternate_victory" in boundary.get("phases", [])
        audit = state.get("_mechanics_tick_audit", {})
        assert "diplomacy_layer" in audit.get("modules", [])


def test_mechanics_status_route():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]
    client = TestClient(api.app)
    status = client.get("/game/mechanics/status").json()
    assert "registry_modules" in status
    assert "diplomacy_layer" in status["registry_modules"]
    assert status["tick_order"] == TICK_ORDER
    assert "boundary" in status


def test_victory_hud_exposes_domination_path():
    from backend.victory_hud import victory_hud_summary

    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    _complete_domination(state)
    hud = victory_hud_summary(state)
    assert "domination_path" in hud
    assert hud["domination_path"]["progress_pct"] == 100.0
