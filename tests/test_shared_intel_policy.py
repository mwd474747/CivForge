"""Tests for shared_intel policy (WP-GROK-POLICY-004)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_metadata import civstudy_reference_panel  # noqa: E402
from backend.game_actions import unlock_policy  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state  # noqa: E402
from backend.trust_erosion import SHARED_INTEL_SUCCESS_BONUS_PCT, negotiation_success_rate  # noqa: E402


def test_shared_intel_in_reference_panel():
    panel = civstudy_reference_panel()
    ids = {p["id"] for b in panel["policy_tree"]["branches"] for p in b["policies"]}
    assert "shared_intel" in ids


def test_shared_intel_unlock_boosts_negotiation_rate():
    state = build_initial_game_state()
    state["turn"] = 12
    state["player"]["resources"]["influence"] = 30
    sim = ensure_civstudy_sim_state(state)
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    base = negotiation_success_rate(state, "lysander")
    unlock_policy(state, "shared_intel")
    boosted = negotiation_success_rate(state, "lysander")
    assert boosted >= base + SHARED_INTEL_SUCCESS_BONUS_PCT - 1
    assert state["civstudy_sim"]["policy_tree"]["policy_flags"].get("shared_intel") is True
