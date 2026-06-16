"""Tests for game session helpers (milestone truth, epilogue, policy costs)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state  # noqa: E402
from backend.game_session import (  # noqa: E402
    cultural_tick_cadence,
    milestone_truth,
    negotiation_influence_cost,
    session_phase,
)
from backend.multi_agent_state import (  # noqa: E402
    add_negotiation,
    default_victory_progress,
    ensure_multi_agent_state,
    sync_victory_milestones,
)


def _blank_state() -> dict:
    return {"turn": 5, "events": [], "ai_civs": [], "player": {"resources": {"influence": 10}}}


def test_session_phase_epilogue_on_victory():
    gs = _blank_state()
    gs["victory_progress"] = {"outcome": "victory", "joint_progress": 100}
    assert session_phase(gs) == "epilogue"


def test_milestone_truth_first_alliance_from_live_alliances():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    truth = milestone_truth(gs, gs["victory_progress"])
    assert truth[0] is True


def test_milestone_truth_map_control_requires_player_tiles():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    for tile in gs["map_tiles"]:
        tile["owner"] = "neutral"
    truth = milestone_truth(gs, gs["victory_progress"])
    assert truth[1] is False

    player_tiles = int(len(gs["map_tiles"]) * 0.45) + 1
    for tile in gs["map_tiles"][:player_tiles]:
        tile["owner"] = "player"
    truth = milestone_truth(gs, gs["victory_progress"])
    assert truth[1] is True


def test_open_negotiation_waives_influence_cost():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    ensure_civstudy_sim_state(gs)
    assert negotiation_influence_cost(gs) == 2
    gs["civstudy_sim"]["policy_tree"]["policy_flags"]["open_negotiation"] = True
    assert negotiation_influence_cost(gs) == 0
    entry = add_negotiation(gs, "harper", "Free diplomacy lane")
    assert "error" not in entry
    assert entry.get("policy_waived") == "open_negotiation"


def test_negotiate_requires_influence_without_policy():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    gs["player"]["resources"]["influence"] = 0
    entry = add_negotiation(gs, "harper", "Too expensive")
    assert entry.get("error") == "Not enough influence to negotiate"


def test_symposium_chain_shortens_cultural_cadence():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    ensure_civstudy_sim_state(gs)
    assert cultural_tick_cadence(gs) == 6
    gs["civstudy_sim"]["policy_tree"]["policy_flags"]["symposium_chain"] = True
    assert cultural_tick_cadence(gs) == 4


def test_sync_milestones_uses_game_state_truth():
    gs = _blank_state()
    ensure_multi_agent_state(gs)
    vp = default_victory_progress()
    vp["milestones"][0]["done"] = False
    events = sync_victory_milestones(vp, turn=7, game_state=gs)
    assert vp["milestones"][0]["done"] is True
    assert any("First alliance" in e for e in events)
