"""PlayerAgent — strategy selection and cycle receipt parity with AI governors."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from backend.multi_agent_state import ensure_multi_agent_state

PLAYER_STRATEGIES: Dict[str, str] = {
    "expand": "Territorial Expansion",
    "diplomacy": "Diplomatic League",
    "culture": "Cultural Prestige",
    "science": "Research Priority",
    "observe": "Council Observation",
}

STRATEGY_TO_ACTION = {
    "expand": "deploy",
    "diplomacy": "govern",
    "culture": "research",
    "science": "research",
    "observe": "govern",
}


def default_player_agent_state() -> Dict[str, Any]:
    return {
        "strategy": "expand",
        "label": PLAYER_STRATEGIES["expand"],
        "last_decision": None,
        "cycles_active": 0,
    }


def ensure_player_agent(game_state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_multi_agent_state(game_state)
    agent = game_state.setdefault("player_agent", default_player_agent_state())
    strategy = agent.get("strategy", "expand")
    if strategy not in PLAYER_STRATEGIES:
        strategy = "expand"
        agent["strategy"] = strategy
    agent["label"] = PLAYER_STRATEGIES[strategy]
    return agent


def player_agent_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    agent = ensure_player_agent(game_state)
    return {
        "strategy": agent.get("strategy"),
        "label": agent.get("label"),
        "last_decision": agent.get("last_decision"),
        "cycles_active": agent.get("cycles_active", 0),
        "strategies": [
            {"id": sid, "label": label, "active": sid == agent.get("strategy")}
            for sid, label in PLAYER_STRATEGIES.items()
        ],
    }


def set_player_strategy(game_state: Dict[str, Any], strategy: str) -> Dict[str, Any]:
    if strategy not in PLAYER_STRATEGIES:
        return {"error": f"Invalid strategy; choose from {tuple(PLAYER_STRATEGIES.keys())}"}
    agent = ensure_player_agent(game_state)
    agent["strategy"] = strategy
    agent["label"] = PLAYER_STRATEGIES[strategy]
    game_state.setdefault("events", []).append(
        f"Turn {game_state['turn']}: Player strategy set to {agent['label']}."
    )
    return {"ok": True, "player_agent": player_agent_summary(game_state)}


def _strategy_context(game_state: Dict[str, Any]) -> Tuple[str, int, int, int, int]:
    sim = game_state.get("civstudy_sim", {})
    district = sim.get("active_district_id", "governance-quarter")
    policies = len(sim.get("policy_tree", {}).get("unlocked", []))
    tiles = sum(1 for t in game_state.get("map_tiles", []) if t.get("owner") == "player")
    alliances = len(game_state.get("alliances", []))
    influence = game_state.get("player", {}).get("resources", {}).get("influence", 0)
    return district, policies, tiles, alliances, influence


def _resolve_action(strategy: str, game_state: Dict[str, Any]) -> str:
    """Map strategy + live state to an action verb aligned with AgentBrain outputs."""
    _, policies, tiles, alliances, influence = _strategy_context(game_state)
    base = STRATEGY_TO_ACTION.get(strategy, "govern")

    if strategy == "expand" and tiles < 8 and influence >= 4:
        return "deploy"
    if strategy == "diplomacy" and alliances >= 1:
        return "govern"
    if strategy == "culture" and policies >= 2:
        return "research"
    if strategy == "science":
        sci = game_state.get("player", {}).get("resources", {}).get("sci", 0)
        return "research" if sci < 12 else "deploy"
    if strategy == "observe":
        return "govern"
    return base


def player_cycle_decision(game_state: Dict[str, Any], player_actions: int) -> str:
    """AI-parity decision line for orchestrator cycle receipts."""
    agent = ensure_player_agent(game_state)
    if player_actions <= 0:
        line = "Decided: govern (based on strategy=observe, player_actions=0)"
        agent["last_decision"] = line
        return line

    strategy = agent.get("strategy", "expand")
    action = _resolve_action(strategy, game_state)
    district, policies, tiles, alliances, influence = _strategy_context(game_state)
    prod = game_state.get("player", {}).get("resources", {}).get("prod", 0)
    sci = game_state.get("player", {}).get("resources", {}).get("sci", 0)

    line = (
        f"Decided: {action} (based on prod={prod}, sci={sci}, "
        f"strategy={strategy}, district={district}, policies={policies}, "
        f"tiles={tiles}, alliances={alliances}, influence={influence})"
    )
    agent["last_decision"] = line
    agent["cycles_active"] = int(agent.get("cycles_active", 0)) + 1
    return line
