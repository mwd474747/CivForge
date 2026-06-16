"""Tests for player game actions and remaining mechanics wiring."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state, tick_civstudy_discovery  # noqa: E402
from backend.game_actions import (  # noqa: E402
    action_catalog,
    claim_map_tile,
    select_district,
    unlock_policy,
)
from backend.game_session import session_phase, trade_route_sci_active  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state, tick_multi_agent_state  # noqa: E402


def _state() -> dict:
    gs = {
        "turn": 12,
        "events": [],
        "ai_civs": [],
        "player": {
            "resources": {"influence": 20, "verify_budget": 8, "sci": 10, "prod": 12},
            "fun_score": 80.0,
            "territories": 3,
        },
    }
    ensure_multi_agent_state(gs)
    ensure_civstudy_sim_state(gs)
    return gs


def test_select_district_costs_influence():
    gs = _state()
    result = select_district(gs, "research-campus")
    assert "error" not in result
    assert gs["civstudy_sim"]["active_district_id"] == "research-campus"
    assert gs["player"]["resources"]["influence"] == 17


def test_unlock_policy_tier_one():
    gs = _state()
    gs["turn"] = 8
    result = unlock_policy(gs, "open_negotiation")
    assert "error" not in result
    assert "open_negotiation" in gs["civstudy_sim"]["policy_tree"]["unlocked"]
    assert gs["civstudy_sim"]["policy_tree"]["policy_flags"]["open_negotiation"] is True


def test_claim_map_tile_adjacent_neutral():
    gs = _state()
    gs["map_tiles"][0].update({"x": 0, "y": 0, "owner": "player", "label": "Tile-00"})
    gs["map_tiles"][1].update({"x": 1, "y": 0, "owner": "neutral", "label": "Tile-10"})
    before = gs["player"]["resources"]["influence"]
    result = claim_map_tile(gs, 1, 0)
    assert "error" not in result
    assert gs["map_tiles"][1]["owner"] == "player"
    assert gs["player"]["resources"]["influence"] == before - 4


def test_receipt_quorum_fork_boosts_progress():
    gs = _state()
    gs["player"]["resources"]["verify_budget"] = 8
    gs["victory_progress"]["joint_progress"] = 50
    events = tick_civstudy_discovery(gs)
    assert any("receipt-quorum" in e.lower() or "Receipt Quorum" in e for e in events)
    assert "receipt-quorum" in gs["civstudy_sim"]["unlocked_forks"]
    assert gs["victory_progress"]["joint_progress"] >= 55


def test_trade_route_sci_after_policy_unlock():
    gs = _state()
    gs["turn"] = 14
    unlock_policy(gs, "institution_charter")
    unlock_policy(gs, "trade_route_map")
    assert trade_route_sci_active(gs)


def test_betrayal_watch_can_break_alliance(monkeypatch):
    gs = _state()
    gs["turn"] = 10
    ensure_civstudy_sim_state(gs)["policy_tree"]["policy_flags"]["betrayal_watch"] = True
    gs["alliances"] = [{
        "id": "alliance-player-test",
        "parties": ["player", "harper"],
        "status": "active",
        "betrayal_risk": 70,
        "formed_turn": 1,
        "note": "test",
    }]
    monkeypatch.setattr("backend.multi_agent_state.random.randint", lambda a, b: 1)
    tick_multi_agent_state(gs, {})
    assert gs["alliances"][0]["status"] == "broken"


def test_defeat_fun_floor():
    gs = _state()
    gs["player"]["fun_score"] = 20.0
    tick_multi_agent_state(gs, {})
    assert session_phase(gs) == "defeat"
    assert gs["victory_progress"]["defeat_reason"] == "fun_floor"


def test_action_catalog_lists_policies():
    gs = _state()
    cat = action_catalog(gs)
    assert "district_select" in cat
    assert len(cat["policies"]) >= 9
