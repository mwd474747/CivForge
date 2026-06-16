"""WP-GROK-CULTURAL-VICTORY-001 — cultural path milestones."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import tick_civstudy_cultural_chains  # noqa: E402
from backend.civstudy_metadata import default_cultural_event_chains  # noqa: E402
from backend.cultural_victory import evaluate_cultural_milestones, sync_cultural_victory_path  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.victory_hud import victory_hud_summary  # noqa: E402


def _complete_all_chains(state):
    sim = state["civstudy_sim"]
    for chain in default_cultural_event_chains():
        sim["active_chains"][chain["id"]] = {
            "stage_idx": len(chain["stages"]),
            "complete": True,
        }


def test_cultural_path_sync_after_tick():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 6
    tick_civstudy_cultural_chains(state)
    path = state["victory_progress"].get("cultural_path")
    assert path is not None
    assert "milestones" in path
    assert path["progress_pct"] >= 0


def test_alternate_victory_eligible_when_all_milestones_done():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["mechanics_lanes"]["cultural"]["influence_spread"] = 30
    _complete_all_chains(state)
    state["civstudy_sim"]["commissioned_wonders"] = [{"wonder_id": "wonder-oracle", "turn": 1}]
    path = sync_cultural_victory_path(state)
    assert path["alternate_victory_eligible"] is True
    assert path["milestones_done"] == 3


def test_victory_hud_exposes_cultural_milestones():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["mechanics_lanes"]["cultural"]["influence_spread"] = 25
    hud = victory_hud_summary(state)
    cp = hud["cultural_path"]
    assert "milestones" in cp
    assert cp["progress_pct"] >= 33.3
    prestige = next(m for m in cp["milestones"] if m["id"] == "prestige_25")
    assert prestige["done"] is True


def test_http_state_includes_cultural_path():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]
    api.game_state["mechanics_lanes"]["cultural"]["influence_spread"] = 25

    client = TestClient(api.app)
    state = client.get("/state").json()
    assert "cultural_path" in state["victory_progress"]
    assert "milestones" in state["victory_hud"]["cultural_path"]
