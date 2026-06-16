"""Tests for trust erosion + negotiation success (WP-GROK-TRUST-EROSION-001/002)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state  # noqa: E402
from backend.game_actions import unlock_policy  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import add_negotiation, ensure_multi_agent_state, respond_negotiation  # noqa: E402
from backend.trust_erosion import (  # noqa: E402
    BASE_NEGOTIATION_SUCCESS_PCT,
    TRUST_BETRAYAL_THRESHOLD,
    TRUST_CRITICAL_THRESHOLD,
    negotiation_success_rate,
    trust_summary,
    trust_tier,
)


def test_trust_tiers():
    assert trust_tier(50) == "stable"
    assert trust_tier(TRUST_BETRAYAL_THRESHOLD) == "betrayal"
    assert trust_tier(TRUST_CRITICAL_THRESHOLD) == "critical"


def test_negotiation_success_rate_envoy_bonus():
    state = build_initial_game_state()
    state["turn"] = 12
    base = negotiation_success_rate(state, "lysander")
    assert base == BASE_NEGOTIATION_SUCCESS_PCT
    sim = ensure_civstudy_sim_state(state)
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    state["player"]["resources"]["influence"] = 20
    unlock_policy(state, "envoy_network")
    boosted = negotiation_success_rate(state, "lysander")
    assert boosted == base + 10.0


def test_trust_summary_on_state_shape():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    summary = trust_summary(state)
    assert summary["betrayal_threshold"] == TRUST_BETRAYAL_THRESHOLD
    assert len(summary["alliances"]) >= 1


def test_negotiation_recovery_on_accept():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["alliances"][0]["betrayal_risk"] = 70
    entry = {
        "id": "neg-recovery-test",
        "from": "player",
        "to": "harper",
        "offer": "Trust building offer",
        "status": "pending",
        "turn": state["turn"],
    }
    state["negotiations"].append(entry)
    respond_negotiation(state, entry["id"], accept=True)
    assert state["alliances"][0]["betrayal_risk"] == 65
