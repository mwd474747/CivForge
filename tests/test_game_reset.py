"""Tests for game reset factory and apply helper."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import apply_game_reset, build_initial_game_state, collect_session_stats  # noqa: E402
from backend.game_session import session_phase  # noqa: E402
from core.orchestrator import GovernanceOrchestrator  # noqa: E402


def test_build_initial_game_state_defaults():
    gs = build_initial_game_state()
    assert gs["turn"] == 1
    assert gs["player"]["cities"] == 2
    assert gs["victory_progress"]["joint_progress"] == 0
    assert gs["victory_progress"].get("outcome") is None
    assert "civstudy_sim" in gs
    assert len(gs["map_tiles"]) > 0


def test_apply_game_reset_clears_victory_and_logs_prior_session():
    orch = GovernanceOrchestrator()
    orch.turn = 42
    orch.receipts = [{"old": True}]
    orch.events = ["old event"]
    orch.gate.proposals = [{"id": "p1"}]

    gs = build_initial_game_state()
    gs["turn"] = 99
    gs["victory_progress"]["joint_progress"] = 100
    gs["victory_progress"]["outcome"] = "victory"
    gs["events"] = ["Turn 99: something happened."]

    summary = apply_game_reset(gs, orch)

    assert gs["turn"] == 1
    assert gs["victory_progress"]["joint_progress"] == 0
    assert gs["victory_progress"].get("outcome") is None
    assert gs["victory_progress"].get("defeat_reason") is None
    assert session_phase(gs) == "active"
    assert orch.turn == 1
    assert orch.receipts == []
    assert summary["prior_session"]["turn"] == 99
    assert summary["prior_session"]["outcome"] == "victory"
    assert summary["prior_session"]["joint_progress"] == 100
    assert len(gs["session_history"]) == 1
    assert any("New game" in e for e in gs["events"])


def test_collect_session_stats_captures_outcome():
    gs = build_initial_game_state()
    gs["turn"] = 12
    gs["victory_progress"]["outcome"] = "defeat"
    gs["victory_progress"]["defeat_reason"] = "fun_floor"
    stats = collect_session_stats(gs)
    assert stats["turn"] == 12
    assert stats["outcome"] == "defeat"
    assert stats["defeat_reason"] == "fun_floor"
