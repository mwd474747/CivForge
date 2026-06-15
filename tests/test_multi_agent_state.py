"""Unit tests for multi-agent state helpers (no live kernel required)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.multi_agent_state import (  # noqa: E402
    add_negotiation,
    default_victory_progress,
    ensure_multi_agent_state,
    negotiations_for_api,
    next_negotiation_id,
    respond_negotiation,
    sync_victory_milestones,
)


def _blank_state() -> dict:
    return {"turn": 10, "events": [], "ai_civs": [], "negotiations": []}


def test_next_negotiation_id_unique_same_turn():
    gs = _blank_state()
    a = next_negotiation_id(gs, "player", "harper")
    gs["negotiations"].append({"id": a, "status": "pending"})
    b = next_negotiation_id(gs, "player", "harper")
    assert a != b
    assert a.endswith("-1")
    assert b.endswith("-2")


def test_negotiations_for_api_includes_all_pending():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    for i in range(15):
        add_negotiation(gs, "harper", f"offer {i}")
    for i in range(5):
        gs["negotiations"][i]["status"] = "accepted"
    api = negotiations_for_api(gs, resolved_limit=3)
    pending = [n for n in api if n["status"] == "pending"]
    assert len(pending) == 10
    assert len(api) == 13  # 10 pending + 3 resolved tail


def test_sync_victory_milestones_at_target():
    vp = default_victory_progress()
    vp["joint_progress"] = 100
    events = sync_victory_milestones(vp, turn=99)
    assert vp["milestones"][3]["done"] is True
    assert any("Joint victory" in e for e in events)


def test_respond_negotiation_accepts_by_unique_id():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    entry = add_negotiation(gs, "sebastian", "Joint audit")
    result = respond_negotiation(gs, entry["id"], accept=True)
    assert result["status"] == "accepted"
    assert any(a["parties"] == ["player", "sebastian"] for a in gs["alliances"])
