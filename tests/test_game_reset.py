"""Tests for game reset factory and apply helper."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import apply_game_reset, build_initial_game_state  # noqa: E402
from core.orchestrator import GovernanceOrchestrator  # noqa: E402


def test_build_initial_game_state_defaults():
    gs = build_initial_game_state()
    assert gs["turn"] == 1
    assert gs["player"]["cities"] == 2
    assert gs["victory_progress"]["joint_progress"] == 18
    assert "civstudy_sim" in gs
    assert len(gs["map_tiles"]) > 0


def test_apply_game_reset_clears_progress_and_orchestrator():
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
    assert gs["victory_progress"]["joint_progress"] == 18
    assert gs["victory_progress"].get("outcome") is None
    assert orch.turn == 1
    assert orch.receipts == []
    assert orch.events == []
    assert orch.gate.proposals == []
    assert summary["prior_turn"] == 99
    assert summary["prior_outcome"] == "victory"
    assert any("Game reset" in e for e in gs["events"])
