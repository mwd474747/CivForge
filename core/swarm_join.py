"""Sequential join strategy and delegate conflict detection (dawsOS swarm borrow)."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

# Mirrors dawsOS secretary_reconciliation_swarm join: evidence → review → coordinator
FORGE_COORDINATOR_ID = "forge-coordinator"
JOIN_ORDER: Tuple[str, ...] = ("harper", "sebastian", FORGE_COORDINATOR_ID)
FANOUT_MAX = 3
JOIN_STRATEGY = "evidence_then_review"
CONFLICT_RESOLUTION_MODE = "review_gate_on_disagreement"
RISKY_ACTIONS = frozenset({"deploy"})


def action_kind(decision: str) -> str:
    """Parse 'Decided: deploy (based on ...)' → 'deploy'."""
    if not decision or "Decided:" not in decision:
        return "unknown"
    tail = decision.split("Decided:", 1)[1].strip()
    return tail.split()[0].lower().rstrip(",") if tail else "unknown"


def detect_delegate_conflict(decisions: Dict[str, str]) -> bool:
    """True when evidence/review delegates disagree on risky deploy."""
    kinds = {aid: action_kind(text) for aid, text in decisions.items()}
    harper = kinds.get("harper", "unknown")
    sebastian = kinds.get("sebastian", "unknown")
    if harper in RISKY_ACTIONS and sebastian not in RISKY_ACTIONS and sebastian != "unknown":
        return True
    if sebastian in RISKY_ACTIONS and harper not in RISKY_ACTIONS and harper != "unknown":
        return True
    return False


def ordered_agent_ids(brain_ids: Iterable[str]) -> Tuple[str, ...]:
    """Join-order first, then extras up to fanout_max."""
    ids = list(brain_ids)
    ordered = [aid for aid in JOIN_ORDER if aid in ids]
    for aid in ids:
        if aid not in ordered:
            ordered.append(aid)
    return tuple(ordered[:FANOUT_MAX])
