"""Policy tree branch checklist (WP-GROK-POLICY-BRANCH-001)."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.civstudy_mechanics_bridge import ensure_civstudy_sim_state
from backend.civstudy_metadata import policy_branch_extensions

POLICY_BRANCH_EXTENSIONS = policy_branch_extensions()


def policy_tree_checklist(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Branch checklist for /state and dashboard."""
    from backend.game_actions import _policy_catalog, _policy_unlockable

    sim = ensure_civstudy_sim_state(game_state)
    pt = sim.setdefault("policy_tree", {"unlocked": [], "policy_flags": {}})
    unlocked = set(pt.get("unlocked", []))
    catalog = _policy_catalog()
    branches: List[Dict[str, Any]] = []

    for branch in POLICY_BRANCH_EXTENSIONS:
        policies_out: List[Dict[str, Any]] = []
        for pid in branch["policies"]:
            meta = catalog.get(pid, {})
            ok, prereq = _policy_unlockable(game_state, pid)
            policies_out.append(
                {
                    "id": pid,
                    "tier": meta.get("tier"),
                    "effect": meta.get("effect", ""),
                    "unlocked": pid in unlocked,
                    "unlockable": ok,
                    "prereq": None if pid in unlocked else prereq,
                }
            )
        branches.append(
            {
                "id": branch["id"],
                "label": branch["label"],
                "maps_to": branch["maps_to"],
                "policies": policies_out,
            }
        )

    return {
        "branches": branches,
        "branch_focus": pt.get("branch_focus"),
        "unlocked_count": len(unlocked),
    }


def select_policy_branch(game_state: Dict[str, Any], branch_id: str) -> Dict[str, Any]:
    valid = {b["id"] for b in POLICY_BRANCH_EXTENSIONS}
    if branch_id not in valid:
        return {"error": f"Unknown branch; choose from {sorted(valid)}"}
    sim = ensure_civstudy_sim_state(game_state)
    pt = sim.setdefault("policy_tree", {"unlocked": [], "policy_flags": {}})
    pt["branch_focus"] = branch_id
    msg = f"Turn {game_state['turn']}: Policy branch focus set to {branch_id}."
    game_state.setdefault("events", []).append(msg)
    return {"ok": True, "branch_focus": branch_id, "checklist": policy_tree_checklist(game_state)}
