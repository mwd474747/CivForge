"""WP-GROK-PLAYER-AGENT-001 — strategy selection and cycle receipt parity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.player_agent import player_cycle_decision, set_player_strategy  # noqa: E402
from backend.telemetry_enrich import enrich_telemetry_payload  # noqa: E402
from backend.turn_simulation import enrich_cycle_receipt  # noqa: E402


def _client():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]
    ensure_multi_agent_state(api.game_state)
    return TestClient(api.app), api


def test_set_player_strategy_via_api():
    client, _api = _client()
    r = client.post("/game/player/strategy", json={"strategy": "science"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body["player_agent"]["strategy"] == "science"


def test_state_exposes_player_agent():
    client, api = _client()
    set_player_strategy(api.game_state, "diplomacy")
    state = client.get("/state").json()
    assert state["player_agent"]["strategy"] == "diplomacy"
    assert len(state["player_agent"]["strategies"]) == 5


def test_advance_turn_registers_player_decision_with_ai_parity():
    client, api = _client()
    set_player_strategy(api.game_state, "expand")
    r = client.post("/advance_turn")
    assert r.status_code == 200
    receipt = r.json()["receipt"]
    player_line = receipt["decisions"]["player"]
    assert player_line.startswith("Decided:")
    assert "strategy=expand" in player_line
    harper_line = receipt["decisions"].get("harper", "")
    assert harper_line.startswith("Decided:")


def test_cycle_receipt_includes_player_agent_snapshot():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    set_player_strategy(state, "culture")
    player_cycle_decision(state, 1)
    receipt = enrich_cycle_receipt({"decisions": {}}, state)
    assert receipt["player_agent"]["strategy"] == "culture"
    assert receipt["player_agent"]["cycles_active"] == 1


def test_invalid_strategy_rejected():
    client, _api = _client()
    r = client.post("/game/player/strategy", json={"strategy": "invalid"})
    assert r.status_code == 200
    assert "error" in r.json()


def test_telemetry_includes_player_strategy_metadata():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    set_player_strategy(state, "observe")
    enriched = enrich_telemetry_payload(state, {"territories": 5})
    assert enriched["playerStrategy"] == "observe"
    assert enriched["playerStrategyLabel"] == "Council Observation"
