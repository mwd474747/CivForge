"""WP-GROK-AUTHENTIC-AUDIT-003 — CivStudy corpus + flavor authenticity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_corpus_cards import default_adjacency_bonuses, default_corpus_cards  # noqa: E402
from backend.civstudy_flavor import (  # noqa: E402
    DEFEAT_CASCADE_SEED_LINES,
    DEFEAT_REASON_FLAVOR,
    game_state_note,
)
from backend.civstudy_metadata import civstudy_reference_panel  # noqa: E402
from backend.game_reset import apply_defeat_cascade_seed, build_initial_game_state  # noqa: E402
from backend.game_session import apply_defeat, check_defeat_conditions  # noqa: E402


def test_twelve_corpus_cards_present():
    cards = default_corpus_cards()
    assert len(cards) == 12
    kinds = {c["kind"] for c in cards}
    assert "district" in kinds
    assert "wonder" in kinds
    assert "policy" in kinds
    assert "unit_line" in kinds
    assert "strategic" in kinds


def test_reference_panel_includes_corpus_and_adjacency():
    panel = civstudy_reference_panel()
    assert len(panel["corpus_cards"]) == 12
    assert len(panel["adjacency_bonuses"]) >= 2
    patterns = " ".join(panel["borrowed_patterns"])
    assert "Nexus" not in patterns
    assert "Empire Council" in patterns


def test_game_state_note_avoids_infra_jargon():
    note = game_state_note()
    for term in ("MCP", "OpenClaw", "governance_kernel", "Nexus"):
        assert term not in note
    assert "rival city-states" in note


def test_defeat_flavor_messages():
    state = build_initial_game_state()
    apply_defeat_cascade_seed(state)
    for line in DEFEAT_CASCADE_SEED_LINES:
        assert any(line in ev for ev in state["events"])
    reason = check_defeat_conditions(state)
    apply_defeat(state, reason, state["turn"])
    last = state["events"][-1]
    assert DEFEAT_REASON_FLAVOR["fun_floor"] in last


def test_district_and_wonder_card_ids():
    cards = {c["id"]: c for c in default_corpus_cards()}
    for cid in (
        "district-campus",
        "wonder-pyramids",
        "wonder-great-wall",
        "wonder-oracle",
        "policy-classical-governments",
        "unit-promotion-warrior-knight",
        "strategic-corridors",
    ):
        assert cid in cards
    assert "river_trade_bonus" in {a["id"] for a in default_adjacency_bonuses()}
