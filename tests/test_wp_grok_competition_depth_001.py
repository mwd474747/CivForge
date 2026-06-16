"""WP-GROK-COMPETITION-DEPTH-001 — win detection, autoplay, spectator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.competition_modes import (  # noqa: E402
    competition_blocks_advance,
    set_competition_mode,
    start_autoplay,
    tick_competition,
)
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.telemetry_enrich import enrich_telemetry_payload  # noqa: E402


def _client():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]
    ensure_multi_agent_state(api.game_state)
    return TestClient(api.app), api


def test_advance_turn_blocked_when_competition_resolved():
    client, api = _client()
    set_competition_mode(api.game_state, "pva_duel")
    comp = api.game_state["competition_mode"]
    comp["player_score"] = 50
    comp["resolved"] = True
    comp["winner"] = "player"
    comp["resolved_at_turn"] = api.game_state["turn"]

    r = client.post("/advance_turn")
    assert r.status_code == 409
    assert "Competition resolved" in r.json()["detail"]


def test_tournament_resolution_via_tick_then_blocks_advance():
    client, api = _client()
    set_competition_mode(api.game_state, "free_for_all")
    api.game_state["turn"] = 30
    tick_competition(api.game_state, {"harper": "deploy"})
    assert api.game_state["competition_mode"]["resolved"] is True
    assert competition_blocks_advance(api.game_state) is not None

    r = client.post("/advance_turn")
    assert r.status_code == 409


def test_autoplay_respects_cooldown():
    client, api = _client()
    set_competition_mode(api.game_state, "pva_duel")
    api.game_state["turn"] = 5

    first = client.post("/game/competition/autoplay/start")
    assert first.status_code == 200
    assert first.json().get("ok") is True

    second = client.post("/game/competition/autoplay/start")
    assert second.status_code == 200
    body = second.json()
    assert body.get("error") == "autoplay cooldown"
    assert body.get("turns_remaining", 0) >= 1


def test_spectator_log_persisted_on_autoplay_and_mode_change():
    client, api = _client()
    set_competition_mode(api.game_state, "pva_duel")
    client.post("/game/competition/autoplay/start")

    log = api.game_state["competition_mode"]["spectator_log"]
    assert len(log) >= 2
    assert any("Competition mode set" in e["message"] for e in log)
    assert any("Autoplay started" in e["message"] for e in log)

    status = client.get("/game/competition/status").json()
    assert status["mode"] == "pva_duel"
    assert len(status["spectator_log"]) >= 2


def test_telemetry_metadata_competition_fields():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    set_competition_mode(state, "alliance_league")
    start_autoplay(state)

    enriched = enrich_telemetry_payload(state, {"territories": 5})
    assert enriched["competitionMode"] == "alliance_league"
    assert enriched["competitionResolved"] is False
    assert enriched["competitionWinner"] is None
    assert enriched["competitionAutoplayActive"] is True
    assert "simulationBoundary" in enriched


def test_competition_status_route_exposes_autoplay():
    client, api = _client()
    set_competition_mode(api.game_state, "pva_duel")
    client.post("/game/competition/autoplay/speed", json={"speed": 3})

    status = client.get("/game/competition/status").json()
    assert status["autoplay"]["speed"] == 3
    assert status["autoplay"]["cooldown_turns"] == 0
    assert "blocks_advance" in status
