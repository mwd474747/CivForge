"""Tests for turn simulation and victory outcome receipts."""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.multi_agent_state import default_victory_progress, sync_victory_milestones  # noqa: E402
from backend.turn_simulation import (  # noqa: E402
    enrich_cycle_receipt,
    maybe_emit_victory_receipt,
    run_turn_simulation,
)
from core.mechanics_registry import MechanicsRegistry  # noqa: E402
from core.receipts import ReceiptStore  # noqa: E402


def _game_state(joint_progress: int = 98) -> dict:
    vp = default_victory_progress()
    vp["joint_progress"] = joint_progress
    vp["milestones"] = [
        {"name": "First alliance", "done": True},
        {"name": "Shared map control", "done": joint_progress >= 25},
        {"name": "Governance quorum", "done": joint_progress >= 60},
        {"name": "Joint victory", "done": joint_progress >= 100},
    ]
    return {
        "turn": 50,
        "player": {"fun_score": 86.0, "resources": {"prod": 12, "sci": 9, "influence": 10}},
        "events": [],
        "victory_progress": vp,
        "map_tiles": [],
        "alliances": [],
        "negotiations": [],
    }


def test_enrich_cycle_receipt_includes_victory_snapshot():
    gs = _game_state(42)
    receipt = enrich_cycle_receipt({"status": "PASS", "fun_score": 86}, gs)
    assert receipt["victory_progress"]["joint_progress"] == 42


def test_post_tick_sync_sets_outcome_same_turn():
    gs = _game_state(99)
    reg = MechanicsRegistry()

    def bonus_tick(state):
        state["victory_progress"]["joint_progress"] = 100
        return ["bonus"]

    reg.register("bonus", bonus_tick)
    run_turn_simulation(gs, reg, {})
    assert gs["victory_progress"]["outcome"] == "victory"


def test_maybe_emit_victory_receipt_once():
    with tempfile.TemporaryDirectory() as tmp:
        store = ReceiptStore(base_dir=Path(tmp))
        gs = _game_state(100)
        gs["victory_progress"]["outcome"] = "victory"
        before = {"joint_progress": 99}
        path1 = maybe_emit_victory_receipt(before, gs, store)
        path2 = maybe_emit_victory_receipt(gs["victory_progress"], gs, store)
        assert path1 is not None
        assert path2 is None
        assert list(Path(tmp).glob("victory-outcome-*.md"))


def test_sync_victory_milestones_sets_outcome_at_target():
    vp = default_victory_progress()
    vp["joint_progress"] = 100
    sync_victory_milestones(vp, turn=10)
    assert vp["outcome"] == "victory"
    assert vp["milestones"][3]["done"] is True
