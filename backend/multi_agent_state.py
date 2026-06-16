"""Multi-agent civ layer: map, alliances, negotiations, joint victory.

Governed extensions on top of the governance workstream kernel. Persisted via game_state snapshot.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from backend.game_session import (
    BETRAYAL_COLLAPSE_THRESHOLD,
    BETRAYAL_WATCH_THRESHOLD,
    alliance_soft_cap,
    apply_defeat,
    check_defeat_conditions,
    milestone_truth,
    negotiation_influence_cost,
    player_alliance_count,
    policy_flags,
)

AGENT_IDS = ("player", "harper", "sebastian", "lysander", "aris")

AGENT_LABELS = {
    "player": "Governance Lead (Grok)",
    "harper": "Harper (Systems)",
    "sebastian": "Sebastian (Governance)",
    "lysander": "Lysander (Research)",
    "aris": "Aris (Diplomacy)",
}

FACTION_COLORS = {
    "player": "#3b82f6",
    "harper": "#22c55e",
    "sebastian": "#a855f7",
    "lysander": "#f59e0b",
    "aris": "#ec4899",
    "neutral": "#64748b",
    "contested": "#ef4444",
}


def default_map_tiles() -> List[Dict[str, Any]]:
    tiles: List[Dict[str, Any]] = []
    owners = ("player", "harper", "sebastian", "neutral", "contested")
    for y in range(5):
        for x in range(5):
            owner = owners[(x + y) % len(owners)]
            tile_type = "city" if (x + y) % 3 == 0 else "territory"
            tiles.append(
                {
                    "x": x,
                    "y": y,
                    "owner": owner,
                    "type": tile_type,
                    "label": f"{'City' if tile_type == 'city' else 'Tile'}-{x}{y}",
                    "strength": 1 + (x + y) % 4,
                }
            )
    return tiles


def default_alliances() -> List[Dict[str, Any]]:
    return [
        {
            "id": "alliance-player-harper",
            "parties": ["player", "harper"],
            "status": "active",
            "betrayal_risk": 8,
            "formed_turn": 1,
            "note": "Systems integration pact",
        },
        {
            "id": "alliance-harper-sebastian",
            "parties": ["harper", "sebastian"],
            "status": "provisional",
            "betrayal_risk": 22,
            "formed_turn": 1,
            "note": "Governance verification compact",
        },
    ]


def default_negotiations() -> List[Dict[str, Any]]:
    return [
        {
            "id": "neg-sebastian-player-1",
            "from": "sebastian",
            "to": "player",
            "offer": "Share verification budget for joint gate review",
            "status": "pending",
            "turn": 1,
        },
        {
            "id": "neg-lysander-player-1",
            "from": "lysander",
            "to": "player",
            "offer": "Trade science for influence on map tile T22",
            "status": "pending",
            "turn": 1,
        },
    ]


def default_victory_progress() -> Dict[str, Any]:
    return {
        "joint_progress": 18,
        "target": 100,
        "milestones": [
            {"name": "First alliance", "done": True},
            {"name": "Shared map control", "done": False},
            {"name": "Governance quorum", "done": False},
            {"name": "Joint victory", "done": False},
        ],
    }


def default_extra_ai_civs() -> List[Dict[str, Any]]:
    return [
        {
            "id": "lysander",
            "name": "Lysander (Research)",
            "resources": {"food": 8, "prod": 6, "sci": 14, "influence": 4},
            "territories": 2,
            "role": "research",
        },
        {
            "id": "aris",
            "name": "Aris (Diplomacy)",
            "resources": {"food": 7, "prod": 5, "sci": 6, "influence": 12},
            "territories": 2,
            "role": "diplomacy",
        },
    ]


def ensure_multi_agent_state(game_state: Dict[str, Any]) -> None:
    """Backfill multi-agent fields on restored or legacy snapshots."""
    if "map_tiles" not in game_state:
        game_state["map_tiles"] = default_map_tiles()
    if "alliances" not in game_state:
        game_state["alliances"] = default_alliances()
    if "negotiations" not in game_state:
        game_state["negotiations"] = default_negotiations()
    if "victory_progress" not in game_state:
        game_state["victory_progress"] = default_victory_progress()
    sync_victory_milestones(game_state["victory_progress"], game_state=game_state)

    existing_ids = {c.get("id") or c.get("name", "").split()[0].lower() for c in game_state.get("ai_civs", [])}
    for civ in default_extra_ai_civs():
        if civ["id"] not in existing_ids and civ["name"] not in existing_ids:
            game_state.setdefault("ai_civs", []).append(dict(civ))

    for civ in game_state.get("ai_civs", []):
        if "id" not in civ:
            civ["id"] = civ.get("name", "agent").split()[0].lower().replace("(", "").strip()


def next_negotiation_id(game_state: Dict[str, Any], from_agent: str, to: str) -> str:
    """Unique negotiation id per from/to/turn (suffix seq avoids same-turn collisions)."""
    turn = game_state["turn"]
    prefix = f"neg-{from_agent}-{to}-{turn}-"
    taken = {n.get("id") for n in game_state.get("negotiations", []) if n.get("id")}
    seq = 1
    while f"{prefix}{seq}" in taken:
        seq += 1
    return f"{prefix}{seq}"


def negotiations_for_api(game_state: Dict[str, Any], resolved_limit: int = 8) -> List[Dict[str, Any]]:
    """All pending negotiations plus a short tail of resolved history for /state."""
    negs = game_state.get("negotiations", [])
    pending = [n for n in negs if n.get("status") == "pending"]
    resolved = [n for n in negs if n.get("status") != "pending"]
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for n in pending:
        nid = n.get("id")
        if nid and nid not in seen:
            seen.add(nid)
            out.append(n)
    for n in resolved[-resolved_limit:]:
        nid = n.get("id")
        if nid and nid not in seen:
            seen.add(nid)
            out.append(n)
    return out


def sync_victory_milestones(
    vp: Dict[str, Any],
    turn: Optional[int] = None,
    game_state: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Align milestone flags with live game truth and joint_progress."""
    events: List[str] = []
    target = vp.get("target", 100)
    progress = vp.get("joint_progress", 0)
    milestones = vp.get("milestones", [])

    if game_state is not None:
        truth = milestone_truth(game_state, vp)
        for idx, label in (
            (0, "First alliance"),
            (1, "Shared map control"),
            (2, "Governance quorum"),
            (3, "Joint victory"),
        ):
            if truth.get(idx) and len(milestones) > idx and not milestones[idx].get("done"):
                milestones[idx]["done"] = True
                prefix = f"Turn {turn}: " if turn is not None else ""
                events.append(f"{prefix}Milestone unlocked — {label}.")
    else:
        checks = (
            (25, 1, "Shared map control"),
            (60, 2, "Governance quorum"),
            (target, 3, "Joint victory"),
        )
        for threshold, idx, label in checks:
            if progress >= threshold and len(milestones) > idx and not milestones[idx].get("done"):
                milestones[idx]["done"] = True
                prefix = f"Turn {turn}: " if turn is not None else ""
                events.append(f"{prefix}Milestone unlocked — {label}.")

    if progress >= target and vp.get("outcome") != "defeat":
        vp["outcome"] = "victory"
    elif vp.get("outcome") == "victory" and progress < target:
        vp.pop("outcome", None)
    return events


def finalize_turn_outcomes(game_state: Dict[str, Any], turn: Optional[int] = None) -> List[str]:
    """Check defeat after ticks."""
    reason = check_defeat_conditions(game_state)
    if reason:
        apply_defeat(game_state, reason, turn)
    return []


def _agent_id_from_decisions(decisions: Dict[str, Any]) -> Optional[str]:
    for aid in decisions:
        if aid in AGENT_IDS:
            return aid
    return None


def tick_multi_agent_state(game_state: Dict[str, Any], decisions: Optional[Dict[str, Any]] = None) -> List[str]:
    """Advance map/alliance/negotiation/victory layer each governance turn."""
    ensure_multi_agent_state(game_state)
    turn = game_state["turn"]
    events: List[str] = []
    vp = game_state["victory_progress"]
    decisions = decisions or {}

    # Victory progress ticks with successful governance
    vp["joint_progress"] = min(vp["target"], vp.get("joint_progress", 0) + random.randint(1, 3))
    events.extend(sync_victory_milestones(vp, turn, game_state))

    # Drift betrayal risk on alliances; betrayal_watch can break alliances
    watch = policy_flags(game_state).get("betrayal_watch")
    for alliance in game_state["alliances"]:
        if alliance.get("status") == "broken":
            continue
        drift = random.randint(-2, 4)
        alliance["betrayal_risk"] = max(0, min(100, alliance.get("betrayal_risk", 10) + drift))
        if alliance["betrayal_risk"] > 40 and alliance["status"] == "active":
            events.append(
                f"Turn {turn}: Alliance {alliance['id']} betrayal risk elevated to {alliance['betrayal_risk']}%."
            )
        should_break = alliance["betrayal_risk"] >= BETRAYAL_COLLAPSE_THRESHOLD
        if watch and alliance["betrayal_risk"] >= BETRAYAL_WATCH_THRESHOLD and random.randint(1, 100) <= 12:
            should_break = True
        if should_break and alliance["status"] in ("active", "provisional"):
            alliance["status"] = "broken"
            events.append(
                f"Turn {turn}: BETRAYAL — alliance {alliance['id']} collapsed at risk {alliance['betrayal_risk']}%."
            )
            if "player" in alliance.get("parties", []):
                vp["joint_progress"] = max(0, vp.get("joint_progress", 0) - 10)
                player = game_state.setdefault("player", {})
                player["fun_score"] = max(0.0, player.get("fun_score", 0) - 5.0)

    # Occasional map shift (contested tile capture)
    tiles = game_state["map_tiles"]
    contested = [t for t in tiles if t["owner"] in ("neutral", "contested")]
    if contested and turn % 3 == 0:
        tile = random.choice(contested)
        new_owner = random.choice(["player", "harper", "sebastian"])
        tile["owner"] = new_owner
        events.append(f"Turn {turn}: {tile['label']} now held by {AGENT_LABELS.get(new_owner, new_owner)}.")

    # AI may open a negotiation
    if turn % 4 == 0:
        sender = random.choice(["harper", "sebastian", "lysander", "aris"])
        offers = [
            "Coordinate receipt audit across factions",
            "Pool influence for shared victory push",
            "Pause deploy lane for verification sprint",
        ]
        neg = {
            "id": next_negotiation_id(game_state, sender, "player"),
            "from": sender,
            "to": "player",
            "offer": random.choice(offers),
            "status": "pending",
            "turn": turn,
        }
        game_state["negotiations"].append(neg)
        events.append(f"Turn {turn}: {AGENT_LABELS.get(sender, sender)} opened negotiation.")

    # React to agent decisions in event log
    for aid, text in decisions.items():
        if aid in AGENT_LABELS:
            events.append(f"Turn {turn}: {AGENT_LABELS[aid]} — {text}")

    game_state["events"].extend(events)

    defeat_events = finalize_turn_outcomes(game_state, turn)
    return events


def add_negotiation(game_state: Dict[str, Any], to: str, offer: str, from_agent: str = "player") -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    cost = negotiation_influence_cost(game_state) if from_agent == "player" else 0
    resources = game_state.setdefault("player", {}).setdefault("resources", {})
    if cost > 0 and resources.get("influence", 0) < cost:
        return {
            "error": "Not enough influence to negotiate",
            "required": cost,
            "available": resources.get("influence", 0),
            "hint": "Unlock open_negotiation policy to waive influence cost",
        }

    if cost > 0:
        resources["influence"] -= cost

    entry = {
        "id": next_negotiation_id(game_state, from_agent, to),
        "from": from_agent,
        "to": to,
        "offer": offer,
        "status": "pending",
        "turn": game_state["turn"],
    }
    if cost == 0 and from_agent == "player" and policy_flags(game_state).get("open_negotiation"):
        entry["policy_waived"] = "open_negotiation"
    game_state["negotiations"].append(entry)
    game_state["events"].append(
        f"Turn {game_state['turn']}: {AGENT_LABELS.get(from_agent, from_agent)} proposed to {AGENT_LABELS.get(to, to)}: {offer}"
    )
    return entry


def respond_negotiation(game_state: Dict[str, Any], neg_id: str, accept: bool) -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    for neg in game_state["negotiations"]:
        if neg["id"] == neg_id and neg["status"] == "pending":
            neg["status"] = "accepted" if accept else "declined"
            if accept:
                if "player" in (neg["from"], neg["to"]) and player_alliance_count(game_state) >= alliance_soft_cap(game_state):
                    neg["status"] = "declined"
                    game_state["events"].append(
                        f"Turn {game_state['turn']}: Negotiation {neg_id} blocked — alliance soft cap "
                        f"({alliance_soft_cap(game_state)}) reached."
                    )
                    return neg
                alliance = {
                    "id": f"alliance-{neg['from']}-{neg['to']}-{game_state['turn']}",
                    "parties": sorted([neg["from"], neg["to"]]),
                    "status": "active",
                    "betrayal_risk": 15,
                    "formed_turn": game_state["turn"],
                    "note": f"Formed from negotiation: {neg['offer'][:60]}",
                }
                game_state["alliances"].append(alliance)
                vp = game_state["victory_progress"]
                vp["joint_progress"] = min(vp["target"], vp.get("joint_progress", 0) + 8)
                game_state["events"].extend(sync_victory_milestones(vp, game_state["turn"], game_state))
            game_state["events"].append(
                f"Turn {game_state['turn']}: Negotiation {neg_id} {'accepted' if accept else 'declined'}."
            )
            return neg
    return {"error": "negotiation not found or already resolved", "id": neg_id}
