"""Unit tests for CivStudy → MechanicsRegistry simulation bridge."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import (  # noqa: E402
    default_civstudy_sim_state,
    ensure_civstudy_sim_state,
    tick_civstudy_cultural_chains,
    tick_civstudy_discovery,
    tick_civstudy_district_pulse,
    tick_civstudy_policy_tree,
)
from core.mechanics_registry import build_default_registry  # noqa: E402


def _base_state(turn: int = 3) -> dict:
    return {
        "turn": turn,
        "player": {
            "resources": {"food": 12, "prod": 12, "sci": 9, "influence": 6, "verify_budget": 7},
        },
        "mechanics_lanes": {
            "military": {"strength": 50, "legacy_points": 1},
            "economic": {"institutions": 2, "yield_bonus_pct": 10},
            "cultural": {"influence_spread": 20, "event_chains": 1},
        },
        "victory_progress": {"joint_progress": 10, "target": 100, "milestones": []},
    }


def test_ensure_civstudy_sim_state_defaults():
    gs = {}
    sim = ensure_civstudy_sim_state(gs)
    assert sim["active_district_id"] == default_civstudy_sim_state()["active_district_id"]
    assert sim["unlocked_forks"] == []


def test_district_pulse_on_turn_multiple_of_three():
    gs = _base_state(turn=6)
    vb_before = gs["player"]["resources"]["verify_budget"]
    events = tick_civstudy_district_pulse(gs)
    assert events
    assert gs["player"]["resources"]["verify_budget"] > vb_before


def test_discovery_unlocks_legacy_doctrine():
    gs = _base_state(turn=10)
    events = tick_civstudy_discovery(gs)
    assert any("Legacy Doctrine" in e for e in events)
    assert "legacy-doctrine" in gs["civstudy_sim"]["unlocked_forks"]


def test_cultural_chain_progresses_on_sixth_turn():
    gs = _base_state(turn=6)
    events = tick_civstudy_cultural_chains(gs)
    assert events
    assert gs["civstudy_sim"]["active_chains"]


def test_build_default_registry_includes_civstudy_modules():
    reg = build_default_registry()
    assert "civstudy_district" in reg._modules
    assert "civstudy_discovery" in reg._modules
    assert "civstudy_cultural" in reg._modules
    assert "civstudy_policy_tree" in reg._modules
    assert "diplomacy_layer" in reg._modules
    assert "competition" in reg._modules


def test_policy_tree_unlocks_diplomacy_tier_one():
    gs = _base_state(turn=8)
    gs["player"]["resources"]["influence"] = 10
    events = tick_civstudy_policy_tree(gs)
    assert any("open_negotiation" in e for e in events)
    assert "open_negotiation" in gs["civstudy_sim"]["policy_tree"]["unlocked"]
