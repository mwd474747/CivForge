"""Civ-era flavor strings for events, receipts, and dashboard copy (WP-GROK-AUTHENTIC-AUDIT-003)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

DEFEAT_REASON_FLAVOR: Dict[str, str] = {
    "fun_floor": "Your empire falls into stagnation — the people lose faith in the throne.",
    "diplomatic_isolation": "Rival emissaries withdraw; your court stands alone among city-states.",
    "betrayal_collapse": "Treaties shatter — rebellion erupts in the outer provinces.",
    "stalled_progress": "Centuries pass without glory; the chronicles record only decline.",
}

DEFEAT_CASCADE_SEED_LINES: List[str] = [
    "Your empire falls into stagnation — harvests fail and morale collapses.",
    "Rebellion erupts in the outer provinces as rival city-states encircle your borders.",
]

DASHBOARD_FLAVOR_SNIPPETS: List[str] = [
    "The people demand expansion.",
    "A rival has denounced you.",
    "Merchants petition the court for new trade routes.",
    "Scholars at the Campus seek patronage for a wonder.",
]

RECEIPT_HEADERS: Dict[str, str] = {
    "defeat-outcome": "Empire Chronicle — Fall of the Realm",
    "victory-outcome": "Empire Chronicle — Age of Glory",
    "governance-cycle": "Empire Council — Session Record",
    "game-reset": "Empire Chronicle — New Dynasty",
}


def defeat_event_line(reason: str, turn: Optional[int] = None) -> str:
    """Player-visible defeat event (replaces raw reason codes in the event log)."""
    flavor = DEFEAT_REASON_FLAVOR.get(reason, reason.replace("_", " "))
    prefix = f"Turn {turn}: " if turn is not None else ""
    return f"{prefix}{flavor}"


def defeat_receipt_title(receipt: Dict[str, Any]) -> str:
    reason = receipt.get("defeat_reason", "defeat")
    flavor = DEFEAT_REASON_FLAVOR.get(reason, reason.replace("_", " "))
    return f"# {RECEIPT_HEADERS['defeat-outcome']}\n\n*{flavor}*"


def victory_receipt_title(_receipt: Dict[str, Any]) -> str:
    return f"# {RECEIPT_HEADERS['victory-outcome']}\n\n*Joint victory — all milestones achieved across rival courts.*"


def receipt_title_for_hint(filename_hint: str, receipt: Dict[str, Any]) -> Optional[str]:
    if filename_hint == "defeat-outcome":
        return defeat_receipt_title(receipt)
    if filename_hint == "victory-outcome":
        return victory_receipt_title(receipt)
    header = RECEIPT_HEADERS.get(filename_hint)
    if header:
        return f"# {header}"
    return None


def game_state_note() -> str:
    """Short /state note — Civ immersion, no infra jargon."""
    return (
        "CivForge empire simulation — rival city-states, treaties, cultural paths, "
        "and joint victory across the shared map."
    )
