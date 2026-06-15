"""Tests for sequential swarm join in orchestrator."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.orchestrator import GovernanceOrchestrator  # noqa: E402
from core.swarm_join import (  # noqa: E402
    FORGE_COORDINATOR_ID,
    JOIN_ORDER,
    action_kind,
    detect_delegate_conflict,
    ordered_agent_ids,
)


def test_join_order_and_fanout():
    ids = ordered_agent_ids([FORGE_COORDINATOR_ID, "harper", "sebastian", "extra"])
    assert ids[:3] == JOIN_ORDER
    assert len(ids) == 3


def test_delegate_conflict_detected():
    decisions = {
        "harper": "Decided: deploy (based on prod=12, sci=9, 1 receipts)",
        "sebastian": "Decided: verify (based on prod=12, sci=9, 1 receipts)",
    }
    assert detect_delegate_conflict(decisions) is True


def test_delegate_conflict_absent_when_aligned():
    decisions = {
        "harper": "Decided: research (based on prod=3, sci=4, 0 receipts)",
        "sebastian": "Decided: verify (based on prod=3, sci=4, 0 receipts)",
    }
    assert detect_delegate_conflict(decisions) is False


def test_action_kind_parser():
    assert action_kind("Decided: govern (based on prod=1)") == "govern"


def test_advance_cycle_includes_join_metadata():
    orch = GovernanceOrchestrator()
    orch.register_agent("harper", "Harper")
    orch.register_agent("sebastian", "Sebastian")
    orch.register_agent(FORGE_COORDINATOR_ID, "Forge Coordinator")
    result = orch.advance_cycle(player_actions=0)
    receipt = result["receipt"]
    assert receipt["join_strategy"] == "evidence_then_review"
    assert receipt["fanout_max"] == 3
    assert "delegate_conflict" in receipt
    assert list(receipt["decisions"].keys())[:2] == ["harper", "sebastian"]
