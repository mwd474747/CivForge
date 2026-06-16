"""Trust erosion + negotiation success (WP-GROK-TRUST-EROSION-001/002 — Cursor execution)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.game_session import policy_flags

BASE_NEGOTIATION_SUCCESS_PCT = 65.0
ENVOY_SUCCESS_BONUS_PCT = 10.0
ALLIANCE_SUCCESS_BONUS_PCT = 8.0
BETRAYAL_PENALTY_SCALE = 0.35
SHARED_INTEL_SUCCESS_BONUS_PCT = 25.0
NEGOTIATION_RECOVERY_RISK_DELTA = 5
TRUST_BETRAYAL_THRESHOLD = 65
TRUST_CRITICAL_THRESHOLD = 90


def player_alliance_with(game_state: Dict[str, Any], agent_id: str) -> Optional[Dict[str, Any]]:
    for alliance in game_state.get("alliances", []):
        if alliance.get("status") not in ("active", "provisional"):
            continue
        parties = alliance.get("parties", [])
        if "player" in parties and agent_id in parties:
            return alliance
    return None


def max_player_alliance_betrayal_risk(game_state: Dict[str, Any]) -> int:
    risks = [
        int(a.get("betrayal_risk", 0))
        for a in game_state.get("alliances", [])
        if "player" in a.get("parties", []) and a.get("status") in ("active", "provisional")
    ]
    return max(risks) if risks else 0


def negotiation_success_rate(game_state: Dict[str, Any], to_agent: str) -> float:
    """Base 65 + envoy bonus + alliance modifier − betrayal penalty (WP-GROK-TRUST-EROSION-002)."""
    rate = BASE_NEGOTIATION_SUCCESS_PCT
    if policy_flags(game_state).get("envoy_network"):
        rate += ENVOY_SUCCESS_BONUS_PCT
    if policy_flags(game_state).get("shared_intel"):
        rate += SHARED_INTEL_SUCCESS_BONUS_PCT
    if player_alliance_with(game_state, to_agent):
        rate += ALLIANCE_SUCCESS_BONUS_PCT
    max_risk = max_player_alliance_betrayal_risk(game_state)
    if max_risk > 40:
        rate -= (max_risk - 40) * BETRAYAL_PENALTY_SCALE
    return max(5.0, min(95.0, round(rate, 1)))


def trust_tier(betrayal_risk: int) -> str:
    if betrayal_risk >= TRUST_CRITICAL_THRESHOLD:
        return "critical"
    if betrayal_risk >= TRUST_BETRAYAL_THRESHOLD:
        return "betrayal"
    return "stable"


def apply_negotiation_recovery(game_state: Dict[str, Any], counterparty: str) -> None:
    """Successful negotiation lowers betrayal risk on shared alliances (WP-GROK-TRUST-EROSION-001)."""
    for alliance in game_state.get("alliances", []):
        parties = alliance.get("parties", [])
        if "player" not in parties or counterparty not in parties:
            continue
        if alliance.get("status") not in ("active", "provisional"):
            continue
        before = alliance.get("betrayal_risk", 0)
        alliance["betrayal_risk"] = max(0, before - NEGOTIATION_RECOVERY_RISK_DELTA)
        if alliance["betrayal_risk"] < before:
            game_state.setdefault("events", []).append(
                f"Turn {game_state['turn']}: Trust recovery — {alliance['id']} risk "
                f"{before}% → {alliance['betrayal_risk']}% after negotiation."
            )


def negotiation_rates_for_agents(game_state: Dict[str, Any]) -> Dict[str, float]:
    """Per-agent success rates for negotiate panel (WP-GROK-TRUST-EROSION-003)."""
    from backend.multi_agent_state import AGENT_IDS

    return {
        aid: negotiation_success_rate(game_state, aid)
        for aid in AGENT_IDS
        if aid != "player"
    }


def trust_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    alliances = []
    for alliance in game_state.get("alliances", []):
        if "player" not in alliance.get("parties", []):
            continue
        risk = int(alliance.get("betrayal_risk", 0))
        alliances.append({
            "id": alliance.get("id"),
            "status": alliance.get("status"),
            "betrayal_risk": risk,
            "trust_tier": trust_tier(risk),
            "envoy_shield_until_turn": alliance.get("envoy_shield_until_turn"),
        })
    return {
        "negotiation_success_base_pct": BASE_NEGOTIATION_SUCCESS_PCT,
        "betrayal_threshold": TRUST_BETRAYAL_THRESHOLD,
        "critical_threshold": TRUST_CRITICAL_THRESHOLD,
        "max_betrayal_risk": max_player_alliance_betrayal_risk(game_state),
        "negotiation_success_rates": negotiation_rates_for_agents(game_state),
        "shared_intel_bonus_pct": SHARED_INTEL_SUCCESS_BONUS_PCT,
        "alliances": alliances,
    }
