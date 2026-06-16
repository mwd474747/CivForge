"""Tests for CivForge-local governance posture tools."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.civforge_contract_parity import build_report as build_contract_report  # noqa: E402
from tools.civforge_governance_posture import build_report as build_posture_report  # noqa: E402
from tools.civforge_receipt_index import build_report as build_receipt_index  # noqa: E402


def test_contract_parity_has_no_fail_findings():
    report = build_contract_report(write_files=False)
    swarm = report.get("swarm_alignment", {})
    assert swarm.get("swarm_class_doc_present") is True
    assert swarm.get("work_pack_template_present") is True
    assert swarm.get("role_openclaw_chief_of_staff") is True
    assert swarm.get("role_forge_coordinator") is True
    assert swarm.get("dawsos_role_map_present") is True
    assert report["summary"]["mcp_tool_count"] == 12
    assert report["bridge"]["post_integrate_supported"] is True
    assert report["nexus_allowed_actions"] == ["sync_config"]
    assert report["summary"]["fail_count"] == 0


def test_governance_posture_static_features_present():
    report = build_posture_report(write_files=False, probe_live=False)
    assert report["features"]["proposal_restore_present"] is True
    assert report["features"]["proposal_receipt_persistence_present"] is True
    assert report["features"]["public_mode_guard_present"] is True
    assert report["features"]["post_integrate_route_present"] is True
    assert report["summary"]["mcp_tool_count"] == 12
    assert report["summary"]["fail_count"] == 0


def test_receipt_index_builds_without_live_kernel():
    report = build_receipt_index(write_files=False)
    assert report["schema"] == "civforge.receipt_index.v1"
    assert "latest_file_count" in report["summary"]
    assert "receipt_classes" in report["summary"]
    assert isinstance(report.get("classified_samples"), list)
