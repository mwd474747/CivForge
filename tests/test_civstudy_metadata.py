"""Unit tests for CivStudy reference metadata (read-only lane)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.civstudy_metadata import civstudy_reference_panel  # noqa: E402


def test_civstudy_reference_has_metadata_extensions():
    panel = civstudy_reference_panel()
    assert panel["status"] == "read_only_reference"
    assert len(panel["districts"]) >= 4
    assert "branches" in panel["policy_tree"]
    assert len(panel["policy_tree"]["branches"]) >= 3
    assert len(panel["discovery_forks"]) >= 4
    assert len(panel["cultural_event_chains"]) >= 3
    assert panel["cultural_event_chains"][0]["stages"]
