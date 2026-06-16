"""Tests for governed mechanics proposal lane."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.mechanics_proposals import (  # noqa: E402
    apply_mechanics,
    gate_mechanics,
    propose_mechanics,
    session_param,
)
from backend.civstudy_mechanics_bridge import tick_civstudy_district_pulse  # noqa: E402
from backend.game_session import cultural_tick_cadence, trade_route_sci_bonus  # noqa: E402


@pytest.fixture
def state():
    return build_initial_game_state()


def test_propose_lane_param(state):
    result = propose_mechanics(
        state,
        kind="lane_param",
        title="Boost economic yield",
        payload={"lane": "economic", "params": {"yield_bonus_pct": 20}},
        work_pack_id="WP-GROK-MECH-002",
    )
    assert "error" not in result
    assert result["proposal"]["status"] == "PROPOSED"


def test_gate_and_apply_district_override(state):
    state["civstudy_sim"]["active_district_id"] = "research-campus"
    prop = propose_mechanics(
        state,
        kind="district_yield_override",
        title="Research campus sci boost",
        payload={"district_id": "research-campus", "yield_bonus": {"sci": 3}},
    )["proposal"]

    gated = gate_mechanics(state, prop["id"], fun_score_override=85.0)
    assert gated["approved"] is True

    applied = apply_mechanics(state, prop["id"])
    assert applied["applied"] is True
    assert state["mechanics_overrides"]["district_yields"]["research-campus"]["sci"] == 3


def test_param_override_affects_ticks(state):
    prop = propose_mechanics(
        state,
        kind="param_override",
        title="Higher trade sci",
        payload={"trade_route_sci_bonus": 3},
    )["proposal"]
    gate_mechanics(state, prop["id"], fun_score_override=82.0)
    apply_mechanics(state, prop["id"])
    assert trade_route_sci_bonus(state) == 3


def test_cadence_override(state):
    prop = propose_mechanics(
        state,
        kind="tick_cadence_override",
        title="Faster cultural chains",
        payload={"cultural_cadence": 5},
    )["proposal"]
    gate_mechanics(state, prop["id"], fun_score_override=80.0)
    apply_mechanics(state, prop["id"])
    assert cultural_tick_cadence(state) == 5


def test_planning_kind_not_auto_applied(state):
    prop = propose_mechanics(
        state,
        kind="policy_definition",
        title="New diplomacy policy",
        payload={
            "id": "envoy_network",
            "branch_id": "diplomacy",
            "tier": 2,
            "effect": "Extra negotiation slot",
        },
    )["proposal"]
    gate_mechanics(state, prop["id"], fun_score_override=88.0)
    result = apply_mechanics(state, prop["id"])
    assert "error" in result
    assert "planning-only" in result["error"]


def test_invalid_kind_rejected(state):
    result = propose_mechanics(state, kind="invalid", title="Bad", payload={})
    assert "error" in result
