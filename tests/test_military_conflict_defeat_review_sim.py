"""Tests for WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001 review + simulation block."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.military_conflict_defeat_review import (  # noqa: E402
    REVIEW_INVENTORY,
    WORK_PACK_ID,
    classify_events,
    extract_metrics,
    run_local_simulation,
)
from backend.game_reset import build_initial_game_state  # noqa: E402


def test_review_inventory_covers_wp_scope():
    assert REVIEW_INVENTORY["military_legacy_chains"]["wired"] is True
    assert REVIEW_INVENTORY["defeat_cascades"]["wired"] is True
    assert len(REVIEW_INVENTORY["agents"]) == 5


def test_extract_metrics_includes_military_and_defeat_fields():
    gs = build_initial_game_state()
    m = extract_metrics(gs)
    assert "military_strength" in m
    assert "military_legacy_points" in m
    assert m["session_phase"] == "active"
    assert m["defeat_reason"] is None


def test_classify_events_betrayal_and_legacy():
    events = [
        "Turn 5: BETRAYAL — alliance x collapsed",
        "Turn 10: Military legacy point earned",
        "Turn 12: Defeat — fun floor",
    ]
    counts = classify_events(events)
    assert counts["betrayal"] >= 1
    assert counts["military_legacy"] >= 1
    assert counts["defeat"] >= 1


def test_local_simulation_50_rounds_completes():
    result = run_local_simulation(rounds=50, seed=99)
    assert result["work_pack_id"] == WORK_PACK_ID
    if result["stopped_early"]:
        assert result["stop_reason"] in ("epilogue", "defeat")
        assert result["rounds_completed"] >= 10
        assert result["final_metrics"]["outcome"] in ("victory", "defeat")
    else:
        assert result["rounds_completed"] == 50
    assert result["final_metrics"]["military_strength"] is not None
    assert result["final_metrics"]["joint_progress"] is not None
    assert len(result["round_snapshots"]) >= 3


@pytest.mark.parametrize("rounds", [10, 25])
def test_local_simulation_shorter_runs(rounds: int):
    result = run_local_simulation(rounds=rounds, seed=1)
    assert result["rounds_completed"] == rounds
