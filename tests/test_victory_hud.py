"""Tests for victory HUD summary (WP-GROK-VICTORY-UI-001)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.victory_hud import victory_hud_summary  # noqa: E402


def test_victory_hud_includes_cultural_path():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    hud = victory_hud_summary(state)
    assert "cultural_path" in hud
    assert "event_chains" in hud["cultural_path"]
    assert "tick_cadence" in hud["cultural_path"]
    assert hud["progress_pct"] >= 0


def test_defeat_warning_when_fun_low():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["player"]["fun_score"] = 30.0
    hud = victory_hud_summary(state)
    assert hud["defeat_warning"] is True
    assert "fun_floor_risk" in hud["defeat_warnings"]
