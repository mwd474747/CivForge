"""Player-initiated game actions: district, policy, map claim."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from backend.civstudy_mechanics_bridge import apply_policy_effect, ensure_civstudy_sim_state
from backend.civstudy_metadata import default_districts, default_policy_tree
from backend.corpus_card_registry import get_corpus_card_registry
from backend.game_session import (
    DISTRICT_SELECT_INFLUENCE_COST,
    MAP_CLAIM_INFLUENCE_COST,
    POLICY_UNLOCK_INFLUENCE_COST,
    policy_flags,
)
from backend.multi_agent_state import AGENT_LABELS, ensure_multi_agent_state, sync_victory_milestones

SEND_ENVOY_INFLUENCE_COST = 6
SEND_ENVOY_RISK_REDUCTION = 15
SEND_ENVOY_SHIELD_TURNS = 3

WONDER_COMMISSION_COSTS = {
    "wonder-pyramids": 14,
    "wonder-great-wall": 12,
    "wonder-oracle": 10,
}
COMMISSIONABLE_WONDER_IDS = tuple(WONDER_COMMISSION_COSTS.keys())

_POLICY_TIER_TURN = {1: 6, 2: 12, 3: 18}


def _policy_catalog() -> Dict[str, Dict[str, Any]]:
    catalog: Dict[str, Dict[str, Any]] = {}
    for branch in default_policy_tree().get("branches", []):
        for policy in branch.get("policies", []):
            catalog[policy["id"]] = {**policy, "branch_id": branch["id"], "branch_name": branch["name"]}
    return catalog


def _district_catalog() -> Dict[str, Dict[str, Any]]:
    return {d["id"]: d for d in default_districts()}


def player_resources(game_state: Dict[str, Any]) -> Dict[str, Any]:
    return game_state.setdefault("player", {}).setdefault("resources", {})


def _wonder_catalog() -> Dict[str, Dict[str, Any]]:
    registry = get_corpus_card_registry()
    return {
        wid: registry.get(wid)
        for wid in COMMISSIONABLE_WONDER_IDS
        if registry.get(wid)
    }


def _wonder_influence_cost(wonder_id: str) -> int:
    card = _wonder_catalog().get(wonder_id) or {}
    if card.get("influence_cost") is not None:
        return int(card["influence_cost"])
    return WONDER_COMMISSION_COSTS.get(wonder_id, 10)


def _commissioned_wonder_ids(game_state: Dict[str, Any]) -> set:
    sim = ensure_civstudy_sim_state(game_state)
    return {entry.get("wonder_id") for entry in sim.get("commissioned_wonders", [])}


def action_catalog(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Costs and availability for dashboard / MCP."""
    from backend.policy_branching import policy_tree_checklist

    ensure_multi_agent_state(game_state)
    ensure_civstudy_sim_state(game_state)
    sim = game_state["civstudy_sim"]
    unlocked = set(sim.get("policy_tree", {}).get("unlocked", []))
    influence = player_resources(game_state).get("influence", 0)
    commissioned = _commissioned_wonder_ids(game_state)
    policies = []
    for pid, meta in _policy_catalog().items():
        tier = int(meta.get("tier", 1))
        policies.append({
            "id": pid,
            "branch": meta["branch_name"],
            "tier": tier,
            "effect": meta.get("effect", ""),
            "unlocked": pid in unlocked,
            "unlockable": _policy_unlockable(game_state, pid)[0],
            "influence_cost": int(meta.get("influence_cost") or POLICY_UNLOCK_INFLUENCE_COST.get(tier, 8)),
        })
    wonders = []
    for wid, card in _wonder_catalog().items():
        cost = _wonder_influence_cost(wid)
        wonders.append({
            "id": wid,
            "name": card.get("name", wid),
            "effect": card.get("effect", ""),
            "influence_cost": cost,
            "commissioned": wid in commissioned,
            "commissionable": wid not in commissioned and influence >= cost,
        })
    return {
        "district_select": {"influence_cost": DISTRICT_SELECT_INFLUENCE_COST, "districts": list(_district_catalog().keys())},
        "map_claim": {"influence_cost": MAP_CLAIM_INFLUENCE_COST},
        "send_envoy": {
            "influence_cost": SEND_ENVOY_INFLUENCE_COST,
            "risk_reduction": SEND_ENVOY_RISK_REDUCTION,
            "shield_turns": SEND_ENVOY_SHIELD_TURNS,
            "available": bool(policy_flags(game_state).get("envoy_network")),
            "alliances": [
                {
                    "id": a.get("id"),
                    "parties": a.get("parties"),
                    "betrayal_risk": a.get("betrayal_risk"),
                    "status": a.get("status"),
                }
                for a in game_state.get("alliances", [])
                if "player" in a.get("parties", []) and a.get("status") in ("active", "provisional")
            ],
        },
        "policies": policies,
        "policy_tree_checklist": policy_tree_checklist(game_state),
        "wonders": wonders,
        "active_district_id": sim.get("active_district_id"),
    }


def _policy_unlockable(game_state: Dict[str, Any], policy_id: str) -> Tuple[bool, str]:
    catalog = _policy_catalog()
    if policy_id not in catalog:
        return False, "unknown policy"
    meta = catalog[policy_id]
    sim = ensure_civstudy_sim_state(game_state)
    pt = sim.get("policy_tree", {})
    unlocked = set(pt.get("unlocked", []))
    if policy_id in unlocked:
        return False, "already unlocked"
    tier = int(meta.get("tier", 1))
    turn = game_state.get("turn", 1)
    if turn < _POLICY_TIER_TURN.get(tier, 999):
        return False, f"requires turn {_POLICY_TIER_TURN.get(tier)}"
    if tier > 1:
        branch_id = meta["branch_id"]
        for prev in catalog.values():
            if prev["branch_id"] == branch_id and int(prev.get("tier", 0)) == tier - 1:
                if prev["id"] not in unlocked:
                    return False, f"requires prior policy {prev['id']}"
    branch_focus = pt.get("branch_focus")
    if branch_focus:
        from backend.policy_branching import POLICY_BRANCH_EXTENSIONS

        allowed = None
        for branch in POLICY_BRANCH_EXTENSIONS:
            if branch["id"] == branch_focus:
                allowed = set(branch["policies"])
                break
        if allowed is not None and policy_id not in allowed:
            return False, f"requires branch focus {branch_focus}"
    cost = int(meta.get("influence_cost") or POLICY_UNLOCK_INFLUENCE_COST.get(tier, 8))
    if player_resources(game_state).get("influence", 0) < cost:
        return False, f"requires {cost} influence"
    return True, "ok"


def select_district(game_state: Dict[str, Any], district_id: str) -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    ensure_civstudy_sim_state(game_state)
    districts = _district_catalog()
    if district_id not in districts:
        return {"error": "unknown district", "district_id": district_id, "valid": list(districts.keys())}

    sim = game_state["civstudy_sim"]
    if sim.get("active_district_id") == district_id:
        return {"error": "district already active", "district_id": district_id}

    resources = player_resources(game_state)
    cost = DISTRICT_SELECT_INFLUENCE_COST
    if resources.get("influence", 0) < cost:
        return {"error": "not enough influence", "required": cost, "available": resources.get("influence", 0)}

    resources["influence"] -= cost
    prior = sim.get("active_district_id")
    sim["active_district_id"] = district_id
    district = districts[district_id]
    msg = (
        f"Turn {game_state['turn']}: Player selected district '{district['name']}' "
        f"(was {prior})."
    )
    sim.setdefault("recent", []).insert(0, msg)
    sim["recent"] = sim["recent"][:8]
    game_state.setdefault("events", []).append(msg)
    return {"district_id": district_id, "district": district, "influence_spent": cost}


def unlock_policy(game_state: Dict[str, Any], policy_id: str) -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    ok, reason = _policy_unlockable(game_state, policy_id)
    if not ok:
        return {"error": reason, "policy_id": policy_id}

    meta = _policy_catalog()[policy_id]
    tier = int(meta.get("tier", 1))
    cost = int(meta.get("influence_cost") or POLICY_UNLOCK_INFLUENCE_COST[tier])
    resources = player_resources(game_state)
    resources["influence"] -= cost

    sim = ensure_civstudy_sim_state(game_state)
    pt = sim.setdefault("policy_tree", {"unlocked": [], "policy_flags": {}})
    unlocked = set(pt.get("unlocked", []))
    unlocked.add(policy_id)
    pt["unlocked"] = sorted(unlocked)
    apply_policy_effect(game_state, meta, sim)

    msg = (
        f"Turn {game_state['turn']}: Player unlocked policy {policy_id} "
        f"({meta['branch_name']} tier {tier})."
    )
    sim.setdefault("recent", []).insert(0, msg)
    sim["recent"] = sim["recent"][:8]
    game_state.setdefault("events", []).append(msg)
    return {"policy_id": policy_id, "influence_spent": cost, "unlocked_policies": pt["unlocked"]}


def _tile_at(game_state: Dict[str, Any], x: int, y: int) -> Optional[Dict[str, Any]]:
    for tile in game_state.get("map_tiles", []):
        if tile.get("x") == x and tile.get("y") == y:
            return tile
    return None


def _adjacent_player_tile(game_state: Dict[str, Any], x: int, y: int) -> bool:
    for tile in game_state.get("map_tiles", []):
        if tile.get("owner") != "player":
            continue
        if abs(tile.get("x", -9) - x) + abs(tile.get("y", -9) - y) == 1:
            return True
    return False


def claim_map_tile(game_state: Dict[str, Any], x: int, y: int) -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    tile = _tile_at(game_state, x, y)
    if tile is None:
        return {"error": "tile not found", "x": x, "y": y}

    if tile.get("owner") == "player":
        return {"error": "tile already owned by player", "x": x, "y": y}

    if tile.get("owner") not in ("neutral", "contested"):
        return {"error": "tile not claimable", "owner": tile.get("owner"), "x": x, "y": y}

    if not _adjacent_player_tile(game_state, x, y):
        return {"error": "tile not adjacent to player territory", "x": x, "y": y}

    resources = player_resources(game_state)
    cost = MAP_CLAIM_INFLUENCE_COST
    if resources.get("influence", 0) < cost:
        return {"error": "not enough influence", "required": cost, "available": resources.get("influence", 0)}

    resources["influence"] -= cost
    prior_owner = tile.get("owner")
    tile["owner"] = "player"
    game_state.setdefault("player", {})["territories"] = sum(
        1 for t in game_state.get("map_tiles", []) if t.get("owner") == "player"
    )

    vp = game_state["victory_progress"]
    vp["joint_progress"] = min(vp.get("target", 100), vp.get("joint_progress", 0) + 3)
    events = sync_victory_milestones(vp, game_state["turn"], game_state)

    msg = f"Turn {game_state['turn']}: Player claimed {tile.get('label')} from {prior_owner}."
    game_state.setdefault("events", []).append(msg)
    game_state["events"].extend(events)
    return {
        "tile": tile,
        "influence_spent": cost,
        "territories": game_state["player"]["territories"],
        "victory_progress": vp,
    }


def _find_player_alliance(game_state: Dict[str, Any], alliance_id: str) -> Optional[Dict[str, Any]]:
    for alliance in game_state.get("alliances", []):
        if alliance.get("id") != alliance_id:
            continue
        if "player" not in alliance.get("parties", []):
            continue
        if alliance.get("status") not in ("active", "provisional"):
            continue
        return alliance
    return None


def _apply_wonder_effect(game_state: Dict[str, Any], wonder_id: str) -> None:
    lanes = game_state.setdefault("mechanics_lanes", {})
    sim = ensure_civstudy_sim_state(game_state)
    if wonder_id == "wonder-pyramids":
        eco = lanes.setdefault("economic", {})
        eco["yield_bonus_pct"] = eco.get("yield_bonus_pct", 10) + 5
        game_state["player"]["resources"]["prod"] = game_state["player"]["resources"].get("prod", 0) + 2
    elif wonder_id == "wonder-great-wall":
        for alliance in game_state.get("alliances", []):
            if "player" in alliance.get("parties", []):
                alliance["betrayal_risk"] = max(0, int(alliance.get("betrayal_risk", 0)) - 10)
    elif wonder_id == "wonder-oracle":
        cul = lanes.setdefault("cultural", {})
        cul["influence_spread"] = cul.get("influence_spread", 0) + 3
        sim.setdefault("wonder_effects", {})["oracle"] = True


def commission_wonder(
    game_state: Dict[str, Any],
    wonder_id: str,
    district_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Commission a world wonder from corpus cards (WP-GROK-WONDER-PLACE-001)."""
    from backend.cultural_victory import sync_cultural_victory_path

    ensure_multi_agent_state(game_state)
    ensure_civstudy_sim_state(game_state)
    if wonder_id not in COMMISSIONABLE_WONDER_IDS:
        return {"error": "unknown wonder", "wonder_id": wonder_id, "valid": list(COMMISSIONABLE_WONDER_IDS)}

    sim = game_state["civstudy_sim"]
    if wonder_id in _commissioned_wonder_ids(game_state):
        return {"error": "wonder already commissioned", "wonder_id": wonder_id}

    districts = _district_catalog()
    active_district = district_id or sim.get("active_district_id")
    if active_district not in districts:
        return {"error": "unknown district", "district_id": active_district, "valid": list(districts.keys())}

    cost = WONDER_COMMISSION_COSTS[wonder_id]
    resources = player_resources(game_state)
    if resources.get("influence", 0) < cost:
        return {"error": "not enough influence", "required": cost, "available": resources.get("influence", 0)}

    card = _wonder_catalog().get(wonder_id, {})
    resources["influence"] -= cost
    entry = {
        "wonder_id": wonder_id,
        "name": card.get("name", wonder_id),
        "district_id": active_district,
        "turn": game_state["turn"],
        "effect": card.get("effect", ""),
    }
    sim.setdefault("commissioned_wonders", []).append(entry)
    _apply_wonder_effect(game_state, wonder_id)
    sync_cultural_victory_path(game_state)

    msg = (
        f"Turn {game_state['turn']}: Commissioned wonder '{entry['name']}' "
        f"in {districts[active_district]['name']} ({cost} influence)."
    )
    sim.setdefault("recent", []).insert(0, msg)
    sim["recent"] = sim["recent"][:8]
    game_state.setdefault("events", []).append(msg)
    return {
        "wonder_id": wonder_id,
        "wonder": entry,
        "influence_spent": cost,
        "commissioned_wonders": sim["commissioned_wonders"],
        "cultural_path": game_state.get("victory_progress", {}).get("cultural_path"),
    }


def send_envoy(game_state: Dict[str, Any], alliance_id: str) -> Dict[str, Any]:
    """Spend influence to reduce betrayal risk when envoy_network policy is active (WP-GROK-POLICY-003)."""
    ensure_multi_agent_state(game_state)
    if not policy_flags(game_state).get("envoy_network"):
        return {
            "error": "envoy_network policy required",
            "hint": "Unlock envoy_network via POST /game/policy/unlock",
        }

    alliance = _find_player_alliance(game_state, alliance_id)
    if not alliance:
        return {"error": "alliance not found or not player-owned", "alliance_id": alliance_id}

    resources = player_resources(game_state)
    if resources.get("influence", 0) < SEND_ENVOY_INFLUENCE_COST:
        return {
            "error": "not enough influence",
            "required": SEND_ENVOY_INFLUENCE_COST,
            "available": resources.get("influence", 0),
        }

    resources["influence"] -= SEND_ENVOY_INFLUENCE_COST
    before = int(alliance.get("betrayal_risk", 0))
    alliance["betrayal_risk"] = max(0, before - SEND_ENVOY_RISK_REDUCTION)
    alliance["envoy_shield_until_turn"] = game_state["turn"] + SEND_ENVOY_SHIELD_TURNS

    msg = (
        f"Turn {game_state['turn']}: Envoy dispatched to {alliance_id} — "
        f"betrayal risk {before}% → {alliance['betrayal_risk']}% "
        f"(shield {SEND_ENVOY_SHIELD_TURNS} turns)."
    )
    game_state.setdefault("events", []).append(msg)
    return {
        "alliance_id": alliance_id,
        "betrayal_risk": alliance["betrayal_risk"],
        "influence_spent": SEND_ENVOY_INFLUENCE_COST,
        "envoy_shield_until_turn": alliance["envoy_shield_until_turn"],
    }


def player_cycle_decision(game_state: Dict[str, Any], player_actions: int) -> str:
    """Re-export — implementation in backend.player_agent."""
    from backend.player_agent import player_cycle_decision as _decide

    return _decide(game_state, player_actions)
