"""Batch validation for WP-GROK-BATCH-005."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import apply_defeat_cascade_seed, build_initial_game_state  # noqa: E402
from backend.mechanics_proposals import apply_mechanics, gate_mechanics, propose_mechanics  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.trust_erosion import trust_summary  # noqa: E402
from backend.victory_hud import victory_hud_summary  # noqa: E402
from backend.game_session import trade_route_sci_bonus  # noqa: E402


def test_trust_erosion_003_success_rates_on_summary():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    summary = trust_summary(state)
    rates = summary.get("negotiation_success_rates", {})
    assert "harper" in rates
    assert 5 <= rates["harper"] <= 95


def test_mechanics_runtime_005_param_override_on_state():
    state = build_initial_game_state()
    prop = propose_mechanics(
        state,
        kind="param_override",
        title="batch runtime sci bonus",
        payload={"trade_route_sci_bonus": 4},
        work_pack_id="WP-GROK-MECHANICS-RUNTIME-005",
    )["proposal"]
    gate_mechanics(state, prop["id"], fun_score_override=82.0)
    apply_mechanics(state, prop["id"])
    assert trade_route_sci_bonus(state) == 4
    assert state["mechanics_overrides"]["session_params"]["trade_route_sci_bonus"] == 4


def test_defeat_cascade_seed_local():
    state = build_initial_game_state()
    apply_defeat_cascade_seed(state)
    assert state["player"]["fun_score"] == 30.0
    assert state["turn"] == 22


def test_defeat_cascade_seed_triggers_fun_floor():
    from backend.game_session import check_defeat_conditions, apply_defeat

    state = build_initial_game_state()
    apply_defeat_cascade_seed(state)
    reason = check_defeat_conditions(state)
    assert reason == "fun_floor"
    apply_defeat(state, reason, state["turn"])
    assert state["victory_progress"]["outcome"] == "defeat"


def test_victory_hud_shape_for_ui():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    hud = victory_hud_summary(state)
    assert set(hud.keys()) >= {"cultural_path", "defeat_warning", "progress_pct", "session_phase"}
