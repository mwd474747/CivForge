"""Truth anchor and work-pack registry coherence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.work_pack_status import work_pack_status_summary  # noqa: E402


def test_work_pack_status_summary_block_a_closed():
    summary = work_pack_status_summary()
    assert summary["closed_block_a"] is True
    assert summary["blocks"]["block_b"]["status"] == "closed"
    assert summary.get("closed_block_c") is True
    assert summary.get("closed_block_d") is True
    assert summary.get("grok_handoff_pack") == "receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md"
    assert "WP-GROK-PLAYER-AGENT-001" not in summary["next_planning"]
    assert "WP-GROK-COMPETITION-DEPTH-001" not in summary["next_planning"]


def test_registry_pytest_total_is_documented():
    summary = work_pack_status_summary()
    assert summary["pytest_total_expected"] >= 147


def test_registry_head_matches_git_when_committed():
    import subprocess

    summary = work_pack_status_summary()
    live = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    try:
        parent = subprocess.check_output(["git", "rev-parse", "--short", "HEAD~1"], text=True).strip()
    except subprocess.CalledProcessError:
        parent = ""
    anchor = summary.get("anchor_head")
    assert anchor, "registry missing anchor.head"
    status = subprocess.run(
        ["git", "status", "--porcelain", "config/work_pack_registry.yaml"],
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        ok = anchor == live or (parent and anchor == parent)
        assert ok, (
            f"anchor.head {anchor} must match git HEAD {live} "
            f"or land commit HEAD~1 {parent} — run verify-truth-anchor.sh --sync"
        )


def test_policy_branch_extensions_in_metadata():
    from backend.civstudy_metadata import civstudy_reference_panel, policy_branch_extensions

    ext = policy_branch_extensions()
    assert len(ext) == 2
    panel = civstudy_reference_panel()
    assert "policy_branch_extensions" in panel


def test_wonder_cards_have_influence_cost():
    from backend.corpus_card_registry import get_corpus_card_registry

    reg = get_corpus_card_registry()
    for wid in ("wonder-pyramids", "wonder-great-wall", "wonder-oracle"):
        card = reg.get(wid)
        assert card is not None
        assert card.get("influence_cost") is not None
