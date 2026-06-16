"""CorpusCardRegistry — one-line CivStudy card registration (WP-DEEP-DIVE-ANALYSIS-003)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.civstudy_corpus_cards import default_adjacency_bonuses, default_corpus_cards

_REGISTRY: Optional["CorpusCardRegistry"] = None


class CorpusCardRegistry:
    def __init__(self) -> None:
        self._cards: Dict[str, Dict[str, Any]] = {}
        self._adjacency: Dict[str, Dict[str, Any]] = {}

    def register_card(self, card: Dict[str, Any]) -> None:
        cid = card["id"]
        self._cards[cid] = card

    def register_adjacency(self, bonus: Dict[str, Any]) -> None:
        self._adjacency[bonus["id"]] = bonus

    def all_cards(self) -> List[Dict[str, Any]]:
        return list(self._cards.values())

    def all_adjacency(self) -> List[Dict[str, Any]]:
        return list(self._adjacency.values())

    def get(self, card_id: str) -> Optional[Dict[str, Any]]:
        return self._cards.get(card_id)


def build_default_corpus_registry() -> CorpusCardRegistry:
    reg = CorpusCardRegistry()
    for card in default_corpus_cards():
        reg.register_card(card)
    for bonus in default_adjacency_bonuses():
        reg.register_adjacency(bonus)
    return reg


def get_corpus_card_registry() -> CorpusCardRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = build_default_corpus_registry()
    return _REGISTRY
