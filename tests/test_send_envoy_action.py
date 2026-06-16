"""Tests for send_envoy player action (WP-GROK-POLICY-003)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state  # noqa: E402
from backend.game_actions import action_catalog, send_envoy, unlock_policy  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.mechanics_proposals import apply_mechanics, gate_mechanics, propose_mechanics  # noqa: E402


def _envoy_ready_state():
    state = build_initial_game_state()
    state["turn"] = 12
    state["player"]["resources"]["influence"] = 20
    sim = ensure_civstudy_sim_state(state)
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    unlock_policy(state, "envoy_network")
    return state


def test_send_envoy_requires_policy():
    state = build_initial_game_state()
    result = send_envoy(state, "alliance-player-harper")
    assert "envoy_network" in result["error"]


def test_send_envoy_reduces_risk():
    state = _envoy_ready_state()
    before = state["alliances"][0]["betrayal_risk"]
    result = send_envoy(state, "alliance-player-harper")
    assert "error" not in result
    assert state["alliances"][0]["betrayal_risk"] == max(0, before - 15)
    assert state["alliances"][0]["envoy_shield_until_turn"] == state["turn"] + 3


def test_send_envoy_in_catalog_when_unlocked():
    state = _envoy_ready_state()
    cat = action_catalog(state)
    assert cat["send_envoy"]["available"] is True
    assert cat["send_envoy"]["influence_cost"] == 6


def test_planning_code_change_gate_only():
    state = build_initial_game_state()
    prop = propose_mechanics(
        state,
        kind="code_change",
        title="send_envoy action",
        payload={"description": "POST /game/diplomacy/send_envoy", "work_pack_id": "WP-GROK-POLICY-003"},
        work_pack_id="WP-GROK-POLICY-003",
    )["proposal"]
    gate_mechanics(state, prop["id"], fun_score_override=85.0)
    applied = apply_mechanics(state, prop["id"])
    assert "planning-only" in applied["error"]
