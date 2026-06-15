#!/usr/bin/env python3
"""CivForge governance posture builder.

Local CivForge analogue to dawsOS `*-latest.json` posture artifacts. It is
report-only: no game, repo, Nexus, or dawsOS mutation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "receipts"
KERNEL = os.environ.get("CIVFORGE_KERNEL_URL", "http://127.0.0.1:8080").rstrip("/")
NEXUS = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082").rstrip("/")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.civforge_contract_parity import build_report as build_contract_report  # noqa: E402
from tools.civforge_poller_posture import build_report as build_poller_report  # noqa: E402
from tools.civforge_receipt_index import build_report as build_receipt_index  # noqa: E402
from tools.mcp_server import TOOLS  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_json(url: str, timeout: int = 4) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return {"ok": True, "status_code": resp.status, "json": json.loads(resp.read().decode())}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def git_status_count() -> Dict[str, Any]:
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=False)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    source_dirty = [line for line in lines if not line.startswith("?? receipts/")]
    return {
        "line_count": len(lines),
        "source_dirty_count": len(source_dirty),
        "source_dirty": source_dirty[:40],
    }


def source_feature_checks() -> Dict[str, bool]:
    sim_api = (ROOT / "backend" / "sim_api.py").read_text(encoding="utf-8")
    governance = (ROOT / "core" / "governance.py").read_text(encoding="utf-8")
    return {
        "proposal_restore_present": "load_proposals" in governance and "governance_proposals" in sim_api,
        "proposal_receipt_persistence_present": "governance-proposal" in sim_api and "governance-gate" in sim_api,
        "public_mode_guard_present": "CIVFORGE_PUBLIC_MODE" in sim_api and "require_public_mode_token" in sim_api,
        "post_integrate_route_present": '@app.post("/integrate/civforge")' in sim_api,
    }


def build_report(write_files: bool = True, probe_live: bool = True) -> Dict[str, Any]:
    contract = build_contract_report(write_files=False)
    poller = build_poller_report(write_files=False)
    receipt_index = build_receipt_index(write_files=False)
    kernel = get_json(f"{KERNEL}/state") if probe_live else {"ok": None, "skipped": True}
    nexus = get_json(f"{NEXUS}/api/health") if probe_live else {"ok": None, "skipped": True}
    features = source_feature_checks()
    findings: List[Dict[str, str]] = []

    if contract["status"] == "fail":
        findings.append({"severity": "fail", "id": "contract_parity_fail", "detail": "contract parity has fail findings"})
    elif contract["status"] == "warn":
        findings.append({"severity": "warn", "id": "contract_parity_warn", "detail": "contract parity has warning findings"})

    if poller["status"] == "fail":
        findings.append({"severity": "fail", "id": "poller_posture_fail", "detail": "poller posture has fail findings"})
    elif poller["status"] == "warn":
        findings.append({"severity": "warn", "id": "poller_posture_warn", "detail": "poller posture has warning findings"})

    if probe_live and not kernel.get("ok"):
        findings.append({"severity": "warn", "id": "kernel_state_unreachable", "detail": kernel.get("error", "")})
    if probe_live and not nexus.get("ok"):
        findings.append({"severity": "warn", "id": "nexus_health_unreachable", "detail": nexus.get("error", "")})

    for key, ok in features.items():
        if not ok:
            findings.append({"severity": "fail", "id": f"source_feature_missing:{key}", "detail": key})

    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    warn_count = sum(1 for f in findings if f["severity"] == "warn")
    state = kernel.get("json") if isinstance(kernel.get("json"), dict) else {}
    report = {
        "schema": "civforge.governance_posture.v1",
        "generated_at": utc_now(),
        "status": "fail" if fail_count else ("warn" if warn_count else "pass"),
        "summary": {
            "fail_count": fail_count,
            "warn_count": warn_count,
            "finding_count": len(findings),
            "mcp_tool_count": len(TOOLS),
            "turn": state.get("current_turn"),
            "fun_score": state.get("fun_score"),
            "pending_negotiations": len([n for n in state.get("negotiations", []) if n.get("status") == "pending"]) if state else None,
        },
        "git": git_status_count(),
        "kernel": kernel,
        "nexus": nexus,
        "features": features,
        "contract_parity": contract,
        "poller_posture": poller,
        "receipt_index": receipt_index,
        "findings": findings,
    }
    if write_files:
        write_report(report)
    return report


def write_report(report: Dict[str, Any]) -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    json_path = RECEIPTS / "civforge-governance-posture-latest.json"
    md_path = RECEIPTS / "civforge-governance-posture-latest.md"
    receipt_path = RECEIPTS / "civforge-governance-posture-receipt-latest.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# CivForge Governance Posture",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- status: `{report['status']}`",
        f"- turn: `{report['summary']['turn']}`",
        f"- fun_score: `{report['summary']['fun_score']}`",
        f"- mcp_tool_count: `{report['summary']['mcp_tool_count']}`",
        f"- source_dirty_count: `{report['git']['source_dirty_count']}`",
        "",
        "## Findings",
    ]
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- `{finding['severity']}` `{finding['id']}`: {finding['detail']}")
    else:
        lines.append("- none")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {
        "schema": "civforge.receipt.v1",
        "generated_at": report["generated_at"],
        "action": "civforge_governance_posture",
        "status": report["status"],
        "artifact": str(json_path.relative_to(ROOT)),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report(write_files=True)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
