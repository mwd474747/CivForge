"""Wire read-only CivStudy metadata into MechanicsRegistry simulation ticks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.civstudy_metadata import (
    civstudy_reference_panel,
    default_cultural_event_chains,
    default_discovery_forks,
    default_districts,
    default_policy_tree,
)
from backend.game_session import (
    RECEIPT_QUORUM_PROGRESS_BONUS,
    RECEIPT_QUORUM_VERIFY_MIN,
    TRADE_ROUTE_SCI_BONUS,
    cultural_tick_cadence,
    receipt_quorum_active,
    trade_route_sci_active,
)


def default_civstudy_sim_state() -> Dict[str, Any]:
    return {
        "active_district_id": "governance-quarter",
        "unlocked_forks": [],
        "active_chains": {},
        "district_pulse_turn": 0,
        "policy_tree": {"unlocked": [], "policy_flags": {}},
        "recent": [],
    }


def ensure_civstudy_sim_state(game_state: Dict[str, Any]) -> Dict[str, Any]:
    sim = game_state.setdefault("civstudy_sim", default_civstudy_sim_state())
    for key, default in default_civstudy_sim_state().items():
        sim.setdefault(key, default if not isinstance(default, list) else [])
    if not isinstance(sim.get("active_chains"), dict):
        sim["active_chains"] = {}
    if not isinstance(sim.get("unlocked_forks"), list):
        sim["unlocked_forks"] = []
    pt = sim.setdefault("policy_tree", {"unlocked": [], "policy_flags": {}})
    if not isinstance(pt.get("unlocked"), list):
        pt["unlocked"] = []
    if not isinstance(pt.get("policy_flags"), dict):
        pt["policy_flags"] = {}
    return sim


def _district_by_id(district_id: str) -> Optional[Dict[str, Any]]:
    for d in default_districts():
        if d["id"] == district_id:
            return d
    return None


def _mechanics_snapshot(game_state: Dict[str, Any]) -> Dict[str, Any]:
    lanes = game_state.get("mechanics_lanes", {})
    military = lanes.get("military", {})
    cultural = lanes.get("cultural", {})
    return {
        "military_strength": military.get("strength", 0),
        "influence_spread": cultural.get("influence_spread", 0),
    }


def _fork_prereqs_met(game_state: Dict[str, Any], prereq: Dict[str, Any]) -> bool:
    resources = game_state.get("player", {}).get("resources", {})
    mech = _mechanics_snapshot(game_state)
    for key, need in prereq.items():
        if key in resources:
            if resources[key] < need:
                return False
        elif key in mech:
            if mech[key] < need:
                return False
        else:
            return False
    return True


def tick_civstudy_district_pulse(game_state: Dict[str, Any]) -> List[str]:
    """Apply active district yield bonuses to player resources on a cadence."""
    sim = ensure_civstudy_sim_state(game_state)
    turn = game_state["turn"]
    if turn % 3 != 0:
        return []

    district = _district_by_id(sim["active_district_id"])
    if not district:
        return []

    bonuses = district.get("yield_bonus", {})
    resources = game_state["player"]["resources"]
    applied: List[str] = []
    for key, delta in bonuses.items():
        if key in resources:
            resources[key] += delta
            applied.append(f"{key}+{delta}")

    if trade_route_sci_active(game_state) and "sci" in resources:
        resources["sci"] += TRADE_ROUTE_SCI_BONUS
        applied.append(f"sci+{TRADE_ROUTE_SCI_BONUS} (trade route)")

    if receipt_quorum_active(game_state) and resources.get("verify_budget", 0) >= RECEIPT_QUORUM_VERIFY_MIN:
        vp = game_state.setdefault("victory_progress", {})
        vp["joint_progress"] = min(
            vp.get("target", 100),
            vp.get("joint_progress", 0) + RECEIPT_QUORUM_PROGRESS_BONUS,
        )
        applied.append(f"victory+{RECEIPT_QUORUM_PROGRESS_BONUS} (receipt quorum)")

    if not applied:
        return []

    msg = f"Turn {turn}: CivStudy district '{district['name']}' pulse → {', '.join(applied)}."
    sim["district_pulse_turn"] = turn
    sim.setdefault("recent", []).insert(0, msg)
    sim["recent"] = sim["recent"][:8]
    return [msg]


def tick_civstudy_discovery(game_state: Dict[str, Any]) -> List[str]:
    """Unlock discovery forks when prereqs from metadata are satisfied."""
    sim = ensure_civstudy_sim_state(game_state)
    turn = game_state["turn"]
    events: List[str] = []
    unlocked = set(sim.get("unlocked_forks", []))

    for fork in default_discovery_forks():
        fid = fork["id"]
        if fid in unlocked:
            continue
        if not _fork_prereqs_met(game_state, fork.get("prereq", {})):
            continue

        unlocked.add(fid)
        sim["unlocked_forks"] = sorted(unlocked)
        msg = f"Turn {turn}: CivStudy fork unlocked — {fork['name']} ({fork['unlocks']})."
        sim.setdefault("recent", []).insert(0, msg)
        sim["recent"] = sim["recent"][:8]

        lanes = game_state.setdefault("mechanics_lanes", {})
        unlock = fork.get("unlocks", "")
        if unlock == "economic_institution_boost":
            eco = lanes.setdefault("economic", {})
            eco["yield_bonus_pct"] = eco.get("yield_bonus_pct", 10) + 5
        elif unlock == "military_legacy_accelerator":
            mil = lanes.setdefault("military", {})
            mil["legacy_points"] = mil.get("legacy_points", 0) + 1
        elif unlock == "cultural_event_chain_bonus":
            cul = lanes.setdefault("cultural", {})
            cul["event_chains"] = cul.get("event_chains", 0) + 1
        elif unlock == "governance_quorum_milestone_hint":
            vp = game_state.setdefault("victory_progress", {})
            vp["joint_progress"] = min(
                vp.get("target", 100),
                vp.get("joint_progress", 0) + 5,
            )
            sim.setdefault("fork_effects", {})["receipt_quorum"] = True
        events.append(msg)

    return events


_POLICY_TIER_TURN = {1: 6, 2: 12, 3: 18}
_POLICY_RESOURCE_GATES = {
    ("diplomacy", 2): {"influence": 8},
    ("diplomacy", 3): {"influence": 12},
    ("economy", 2): {"prod": 10},
    ("economy", 3): {"prod": 14},
    ("culture", 2): {"sci": 8},
    ("culture", 3): {"sci": 12},
}


def _policy_tree_state(sim: Dict[str, Any]) -> Dict[str, Any]:
    return sim.setdefault("policy_tree", {"unlocked": [], "policy_flags": {}})


def _branch_policy(branch: Dict[str, Any], tier: int) -> Optional[Dict[str, Any]]:
    for policy in branch.get("policies", []):
        if policy.get("tier") == tier:
            return policy
    return None


def _policy_prereqs_met(game_state: Dict[str, Any], branch: Dict[str, Any], tier: int, unlocked: set) -> bool:
    turn = game_state["turn"]
    if turn < _POLICY_TIER_TURN.get(tier, 999):
        return False
    if tier > 1:
        prev = _branch_policy(branch, tier - 1)
        if not prev or prev["id"] not in unlocked:
            return False
    gates = _POLICY_RESOURCE_GATES.get((branch["id"], tier), {})
    resources = game_state.get("player", {}).get("resources", {})
    for key, need in gates.items():
        if resources.get(key, 0) < need:
            return False
    return True


def apply_policy_effect(game_state: Dict[str, Any], policy: Dict[str, Any], sim: Dict[str, Any]) -> None:
    pid = policy["id"]
    flags = _policy_tree_state(sim).setdefault("policy_flags", {})
    lanes = game_state.setdefault("mechanics_lanes", {})

    if pid == "yield_surge":
        eco = lanes.setdefault("economic", {})
        eco["yield_bonus_pct"] = eco.get("yield_bonus_pct", 10) + 5
    elif pid == "influence_spread":
        cul = lanes.setdefault("cultural", {})
        cul["influence_spread"] = min(100, cul.get("influence_spread", 0) + 2)
    elif pid == "institution_charter":
        eco = lanes.setdefault("economic", {})
        eco["institutions"] = eco.get("institutions", 1) + 1
    elif pid in ("betrayal_watch", "festival_receipts", "open_negotiation", "symposium_chain"):
        flags[pid] = True
    elif pid == "alliance_cap_3":
        flags["alliance_cap_3"] = True
    elif pid == "trade_route_map":
        eco = lanes.setdefault("economic", {})
        eco["trade_routes"] = eco.get("trade_routes", 0) + 1


def tick_civstudy_policy_tree(game_state: Dict[str, Any]) -> List[str]:
    """Unlock CivStudy policy-tree tiers when turn/resource gates are met."""
    sim = ensure_civstudy_sim_state(game_state)
    turn = game_state["turn"]
    if turn % 4 != 0:
        return []

    pt = _policy_tree_state(sim)
    unlocked = set(pt.get("unlocked", []))
    events: List[str] = []

    for branch in default_policy_tree().get("branches", []):
        for policy in branch.get("policies", []):
            pid = policy["id"]
            if pid in unlocked:
                continue
            tier = int(policy.get("tier", 1))
            if not _policy_prereqs_met(game_state, branch, tier, unlocked):
                continue
            unlocked.add(pid)
            pt["unlocked"] = sorted(unlocked)
            apply_policy_effect(game_state, policy, sim)
            msg = (
                f"Turn {turn}: Policy unlocked — {branch['name']} / {pid} "
                f"(tier {tier}: {policy.get('effect', '')})."
            )
            sim.setdefault("recent", []).insert(0, msg)
            sim["recent"] = sim["recent"][:8]
            events.append(msg)

    return events


def tick_civstudy_cultural_chains(game_state: Dict[str, Any]) -> List[str]:
    """Progress cultural event chains from CivStudy metadata."""
    sim = ensure_civstudy_sim_state(game_state)
    turn = game_state["turn"]
    if turn % cultural_tick_cadence(game_state) != 0:
        return []

    chains = sim.setdefault("active_chains", {})
    events: List[str] = []
    resources = game_state["player"]["resources"]
    vp = game_state.get("victory_progress", {})

    for chain in default_cultural_event_chains():
        cid = chain["id"]
        state = chains.setdefault(cid, {"stage_idx": 0, "complete": False})
        if state.get("complete"):
            continue

        stages = chain.get("stages", [])
        idx = state.get("stage_idx", 0)
        if idx >= len(stages):
            state["complete"] = True
            continue

        state["stage_idx"] = idx + 1
        stage_name = stages[idx]
        msg = f"Turn {turn}: Cultural chain '{chain['name']}' — stage {stage_name}."
        sim.setdefault("recent", []).insert(0, msg)
        sim["recent"] = sim["recent"][:8]

        if "influence_reward" in chain and idx == len(stages) - 1:
            resources["influence"] = resources.get("influence", 0) + chain["influence_reward"]
        if "sci_reward" in chain and idx == len(stages) - 1:
            resources["sci"] = resources.get("sci", 0) + chain["sci_reward"]
        if "victory_bonus" in chain and idx == len(stages) - 1:
            bonus = chain["victory_bonus"]
            flags = _policy_tree_state(sim).get("policy_flags", {})
            if flags.get("festival_receipts"):
                bonus += 2
            vp["joint_progress"] = min(
                vp.get("target", 100),
                vp.get("joint_progress", 0) + bonus,
            )

        if state["stage_idx"] >= len(stages):
            state["complete"] = True
            msg += " (complete)"
        events.append(msg)

    return events


def civstudy_sim_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Compact summary for /state and Nexus telemetry."""
    sim = ensure_civstudy_sim_state(game_state)
    district = _district_by_id(sim["active_district_id"])
    return {
        "active_district": district["name"] if district else sim["active_district_id"],
        "unlocked_forks": list(sim.get("unlocked_forks", [])),
        "unlocked_policies": list(sim.get("policy_tree", {}).get("unlocked", [])),
        "policy_flags": dict(sim.get("policy_tree", {}).get("policy_flags", {})),
        "active_chains": {
            k: v for k, v in sim.get("active_chains", {}).items() if not v.get("complete")
        },
        "recent": sim.get("recent", [])[:4],
        "metadata_status": civstudy_reference_panel()["status"],
    }


def register_civstudy_mechanics(registry: Any) -> None:
    """Register CivStudy bridge ticks on a MechanicsRegistry instance."""
    registry.register("civstudy_district", tick_civstudy_district_pulse)
    registry.register("civstudy_discovery", tick_civstudy_discovery)
    registry.register("civstudy_cultural", tick_civstudy_cultural_chains)
    registry.register("civstudy_policy_tree", tick_civstudy_policy_tree)
