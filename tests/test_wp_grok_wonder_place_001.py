"""WP-GROK-WONDER-PLACE-001 — wonder commission action."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_actions import action_catalog, commission_wonder  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402


def test_commission_wonder_deducts_influence_and_records_entry():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["player"]["resources"]["influence"] = 20
    result = commission_wonder(state, "wonder-oracle")
    assert "error" not in result
    assert result["influence_spent"] == 10
    assert len(state["civstudy_sim"]["commissioned_wonders"]) == 1
    assert state["civstudy_sim"]["commissioned_wonders"][0]["wonder_id"] == "wonder-oracle"
    assert state["player"]["resources"]["influence"] == 10


def test_commission_wonder_triggers_wonder_prestige_milestone():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["player"]["resources"]["influence"] = 20
    state["mechanics_lanes"]["cultural"]["influence_spread"] = 25
    commission_wonder(state, "wonder-pyramids")
    path = state["victory_progress"]["cultural_path"]
    by_id = {m["id"]: m for m in path["milestones"]}
    assert by_id["wonder_prestige"]["done"] is True


def test_action_catalog_lists_commissionable_wonders():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["player"]["resources"]["influence"] = 15
    cat = action_catalog(state)
    assert len(cat["wonders"]) == 3
    assert any(w["id"] == "wonder-great-wall" and w["commissionable"] for w in cat["wonders"])


def test_http_wonder_commission_route():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.game_state["player"]["resources"]["influence"] = 20
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    resp = client.post("/game/wonder/commission", json={"wonder_id": "wonder-oracle"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["wonder_id"] == "wonder-oracle"
    state = client.get("/state").json()
    assert len(state["civstudy_sim"]["commissioned_wonders"]) == 1
