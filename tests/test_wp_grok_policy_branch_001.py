"""WP-GROK-POLICY-BRANCH-001 — policy branch checklist and focus."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.game_actions import action_catalog, unlock_policy  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from backend.multi_agent_state import ensure_multi_agent_state  # noqa: E402
from backend.policy_branching import policy_tree_checklist, select_policy_branch  # noqa: E402


def test_policy_tree_checklist_exposes_branches_and_prereqs():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 6
    checklist = policy_tree_checklist(state)
    assert len(checklist["branches"]) == 2
    tradition = next(b for b in checklist["branches"] if b["id"] == "tradition")
    symposium = next(p for p in tradition["policies"] if p["id"] == "symposium_chain")
    assert symposium["unlockable"] is True


def test_branch_focus_blocks_out_of_branch_unlock():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    state["turn"] = 12
    state["player"]["resources"]["influence"] = 30
    sim = state["civstudy_sim"]
    sim["policy_tree"]["unlocked"] = ["open_negotiation"]
    select_policy_branch(state, "tradition")
    blocked = unlock_policy(state, "shared_intel")
    assert blocked.get("error") == "requires branch focus tradition"


def test_action_catalog_includes_policy_checklist():
    state = build_initial_game_state()
    ensure_multi_agent_state(state)
    cat = action_catalog(state)
    assert "policy_tree_checklist" in cat
    assert cat["policy_tree_checklist"]["branches"]


def test_http_state_exposes_policy_checklist():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    state = client.get("/state").json()
    checklist = state["civstudy_sim"]["policy_tree"]["checklist"]
    assert checklist["branches"]
    branch = client.post("/game/policy/branch", json={"branch_id": "liberty"})
    assert branch.status_code == 200
    assert branch.json()["branch_focus"] == "liberty"
