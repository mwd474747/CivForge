"""Wire read-only CivStudy metadata into MechanicsRegistry simulation ticks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.civstudy_metadata import (
    civstudy_reference_panel,
    default_cultural_event_chains,
    default_discovery_forks,
    default_districts,
)


def default_civstudy_sim_state() -> Dict[str, Any]:
    return {
        "active_district_id": "governance-quarter",
        "unlocked_forks": [],
        "active_chains": {},
        "district_pulse_turn": 0,
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
        events.append(msg)

    return events


def tick_civstudy_cultural_chains(game_state: Dict[str, Any]) -> List[str]:
    """Progress cultural event chains from CivStudy metadata."""
    sim = ensure_civstudy_sim_state(game_state)
    turn = game_state["turn"]
    if turn % 6 != 0:
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
            vp["joint_progress"] = min(
                vp.get("target", 100),
                vp.get("joint_progress", 0) + chain["victory_bonus"],
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
