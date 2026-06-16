"""End-to-end simulation loop: advance ticks until victory outcome receipt."""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.game_session import session_phase  # noqa: E402
from backend.turn_simulation import maybe_emit_victory_receipt, run_turn_simulation  # noqa: E402
from core.mechanics_registry import build_default_registry  # noqa: E402
from core.receipts import ReceiptStore  # noqa: E402


def test_turn_loop_emits_victory_receipt(tmp_path: Path):
    gs = build_initial_game_state()
    gs["victory_progress"]["joint_progress"] = 96
    registry = build_default_registry()
    store = ReceiptStore(base_dir=tmp_path)

    victory_path = None
    for _ in range(30):
        gs["turn"] += 1
        before = dict(gs["victory_progress"])
        run_turn_simulation(gs, registry, {})
        victory_path = maybe_emit_victory_receipt(before, gs, store)
        if victory_path:
            break

    assert gs["victory_progress"]["outcome"] == "victory"
    assert session_phase(gs) == "epilogue"
    assert victory_path is not None
    assert list(tmp_path.glob("victory-outcome-*.md"))


def test_http_epilogue_blocks_advance_turn():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.game_state["victory_progress"]["joint_progress"] = 100
    api.game_state["victory_progress"]["outcome"] = "victory"
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    state = client.get("/state").json()
    assert state["session_phase"] == "epilogue"

    blocked = client.post("/advance_turn")
    assert blocked.status_code == 409

    reset = client.post("/game/reset")
    assert reset.status_code == 200
    body = reset.json()
    assert body["session_phase"] == "active"
    assert body["victory_progress"].get("outcome") is None
    assert body["summary"]["prior_session"]["outcome"] == "victory"
    assert client.get("/state").json()["session_phase"] == "active"


def test_http_defeat_cascade_reset_message():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    reset = client.post("/game/reset", json={"seed_profile": "defeat_cascade"})
    assert reset.status_code == 200
    body = reset.json()
    assert "defeat-cascade" in body["message"]
    assert body["session_phase"] == "defeat"
    assert body["victory_progress"]["defeat_reason"] == "fun_floor"
    state = client.get("/state").json()
    assert state["current_turn"] == 22
    assert state["player"]["fun_score"] == 30.0
