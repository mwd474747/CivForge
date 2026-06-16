"""AI-initiated negotiation proposals each cycle (Block C)."""

from __future__ import annotations

import random
from typing import Any, Dict, List

from backend.multi_agent_state import AGENT_IDS, AGENT_LABELS, add_negotiation, ensure_multi_agent_state
from backend.trust_erosion import negotiation_success_rate

AI_NEGOTIATION_OFFERS: Dict[str, List[str]] = {
    "harper": [
        "Systems audit compact — shared verify budget",
        "Infrastructure mutual defense pact",
    ],
    "sebastian": [
        "Governance charter amendment",
        "Receipt quorum co-sponsorship",
    ],
    "lysander": [
        "Research campus exchange",
        "Discovery fork collaboration",
    ],
    "aris": [
        "Embassy trade corridor",
        "Cultural exchange treaty",
        "Non-aggression compact",
    ],
}

PROPOSAL_CADENCE_TURNS = 2
PROPOSAL_BASE_CHANCE = 40


def _pending_to_player(game_state: Dict[str, Any]) -> bool:
    return any(
        n.get("status") == "pending" and n.get("to") == "player"
        for n in game_state.get("negotiations", [])
    )


def tick_ai_negotiation_proposals(game_state: Dict[str, Any]) -> List[str]:
    """Agents propose negotiations to the player when trust allows."""
    ensure_multi_agent_state(game_state)
    events: List[str] = []
    turn = game_state.get("turn", 1)

    if turn % PROPOSAL_CADENCE_TURNS != 0:
        return events
    if _pending_to_player(game_state):
        return events

    for aid in AGENT_IDS:
        if aid == "player":
            continue
        if random.randint(1, 100) > PROPOSAL_BASE_CHANCE:
            continue
        rate = negotiation_success_rate(game_state, aid)
        if rate < 35:
            continue
        offers = AI_NEGOTIATION_OFFERS.get(aid, ["Alliance proposal"])
        offer = random.choice(offers)
        entry = add_negotiation(game_state, "player", offer, from_agent=aid)
        if entry.get("error"):
            continue
        if entry.get("status") == "pending":
            events.append(
                f"Turn {turn}: {AGENT_LABELS.get(aid, aid)} proposes negotiation — "
                f"\"{offer}\" (respond via POST /game/negotiate/respond)."
            )
            entry["ai_initiated"] = True
            return events
    return events
