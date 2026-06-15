"""Multi-agent civ layer: map, alliances, negotiations, joint victory.

Governed extensions on top of the governance workstream kernel. Persisted via game_state snapshot.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

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

    existing_ids = {c.get("id") or c.get("name", "").split()[0].lower() for c in game_state.get("ai_civs", [])}
    for civ in default_extra_ai_civs():
        if civ["id"] not in existing_ids and civ["name"] not in existing_ids:
            game_state.setdefault("ai_civs", []).append(dict(civ))

    for civ in game_state.get("ai_civs", []):
        if "id" not in civ:
            civ["id"] = civ.get("name", "agent").split()[0].lower().replace("(", "").strip()


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
    if vp["joint_progress"] >= 25 and vp["milestones"][1]["done"] is False:
        vp["milestones"][1]["done"] = True
        events.append(f"Turn {turn}: Milestone unlocked — Shared map control.")
    if vp["joint_progress"] >= 60 and vp["milestones"][2]["done"] is False:
        vp["milestones"][2]["done"] = True
        events.append(f"Turn {turn}: Milestone unlocked — Governance quorum.")

    # Drift betrayal risk on alliances
    for alliance in game_state["alliances"]:
        drift = random.randint(-2, 4)
        alliance["betrayal_risk"] = max(0, min(100, alliance.get("betrayal_risk", 10) + drift))
        if alliance["betrayal_risk"] > 40 and alliance["status"] == "active":
            events.append(
                f"Turn {turn}: Alliance {alliance['id']} betrayal risk elevated to {alliance['betrayal_risk']}%."
            )

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
            "id": f"neg-{sender}-player-{turn}",
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
    return events


def add_negotiation(game_state: Dict[str, Any], to: str, offer: str, from_agent: str = "player") -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    entry = {
        "id": f"neg-{from_agent}-{to}-{game_state['turn']}",
        "from": from_agent,
        "to": to,
        "offer": offer,
        "status": "pending",
        "turn": game_state["turn"],
    }
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
            game_state["events"].append(
                f"Turn {game_state['turn']}: Negotiation {neg_id} {'accepted' if accept else 'declined'}."
            )
            return neg
    return {"error": "negotiation not found or already resolved", "id": neg_id}
