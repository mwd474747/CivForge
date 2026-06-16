"""Tests for envoy_network policy (WP-GROK-POLICY-002)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_metadata import civstudy_reference_panel, default_policy_tree  # noqa: E402
from backend.game_actions import action_catalog, unlock_policy  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state  # noqa: E402
from backend.mechanics_proposals import apply_mechanics, gate_mechanics, propose_mechanics  # noqa: E402


def _envoy_meta():
    for branch in default_policy_tree()["branches"]:
        if branch["id"] == "diplomacy":
            for policy in branch["policies"]:
                if policy["id"] == "envoy_network":
                    return policy
    raise AssertionError("envoy_network missing from metadata")


def test_envoy_network_in_reference_panel():
    panel = civstudy_reference_panel()
    ids = {
        p["id"]
        for branch in panel["policy_tree"]["branches"]
        for p in branch["policies"]
    }
    assert "envoy_network" in ids


def test_envoy_unlock_sets_policy_flag():
    state = build_initial_game_state()
    state["turn"] = 12
    state["player"]["resources"]["influence"] = 20
    sim = ensure_civstudy_sim_state(state)
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    result = unlock_policy(state, "envoy_network")
    assert "error" not in result
    assert state["civstudy_sim"]["policy_tree"]["policy_flags"].get("envoy_network") is True


def test_envoy_influence_cost_in_catalog():
    state = build_initial_game_state()
    state["turn"] = 12
    sim = ensure_civstudy_sim_state(state)
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    catalog = action_catalog(state)
    envoy = next(p for p in catalog["policies"] if p["id"] == "envoy_network")
    assert envoy["influence_cost"] == 12


def test_planning_proposal_gate_without_apply():
    state = build_initial_game_state()
    meta = _envoy_meta()
    prop = propose_mechanics(
        state,
        kind="policy_definition",
        title="tier-2 diplomacy branch envoy_network",
        payload={
            "id": meta["id"],
            "branch_id": "diplomacy",
            "tier": meta["tier"],
            "effect": "diplomatic_outpost_network",
        },
        work_pack_id="WP-GROK-POLICY-002",
    )["proposal"]
    gated = gate_mechanics(state, prop["id"], fun_score_override=86.0)
    assert gated["approved"] is True
    assert gated["proposal"]["status"] == "GATED_APPROVED"
    applied = apply_mechanics(state, prop["id"])
    assert "planning-only" in applied["error"]
