#!/usr/bin/env python3
"""CivForge contract parity lint.

Report-only governance surface for checking that docs, routes, MCP tools, and
Nexus command policy describe the same CivForge contract.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "receipts"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def route_methods() -> Dict[str, List[str]]:
    text = read_text(ROOT / "backend" / "sim_api.py")
    routes: Dict[str, List[str]] = {}
    for method, route in re.findall(r"@app\.(get|post)\(\s*[\"']([^\"']+)[\"']", text):
        routes.setdefault(route, []).append(method.upper())
    return {route: sorted(set(methods)) for route, methods in sorted(routes.items())}


def mcp_tool_names() -> List[str]:
    from tools.mcp_server import TOOLS  # pylint: disable=import-outside-toplevel

    return sorted(t["name"] for t in TOOLS)


def documented_mcp_tools() -> List[str]:
    text = read_text(ROOT / "docs" / "GAME_PLAY_GUIDE_V1.md")
    return sorted(set(re.findall(r"`(civforge_[a-z_]+)`", text)))


def allowed_actions_from_boundary() -> List[str]:
    text = read_text(ROOT / "docs" / "CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md")
    match = re.search(r'"allowed_actions"\s*:\s*\[([^\]]*)\]', text)
    if not match:
        return []
    return sorted(re.findall(r'"([^"]+)"', match.group(1)))


def stale_auth_bridge_refs() -> List[str]:
    refs = []
    for rel in ("AGENTS.md", "tools/civforge_cli.py", "docs/GAME_PLAY_GUIDE_V1.md"):
        text = read_text(ROOT / rel)
        if "tools/auth-prototype/" in text or "./tools/auth-prototype" in text:
            refs.append(rel)
    return refs


def bridge_expectations() -> Dict[str, Any]:
    bridge_files = sorted((ROOT / "bridge").glob("*.py"))
    bridge_text = "\n".join(read_text(path) for path in bridge_files)
    wants_post_integrate = bool(re.search(r"requests\.post\([^)]*/integrate/civforge", bridge_text, re.S))
    routes = route_methods()
    return {
        "bridge_files": [str(path.relative_to(ROOT)) for path in bridge_files],
        "bridge_posts_integrate": wants_post_integrate,
        "integrate_methods": routes.get("/integrate/civforge", []),
        "post_integrate_supported": "POST" in routes.get("/integrate/civforge", []),
    }


def _findings_from_missing(prefix: str, missing: Iterable[str], severity: str) -> List[Dict[str, str]]:
    return [{"id": f"{prefix}:{item}", "severity": severity, "detail": item} for item in sorted(missing)]


def build_report(write_files: bool = True) -> Dict[str, Any]:
    actual_tools = set(mcp_tool_names())
    guide_tools = set(documented_mcp_tools())
    routes = route_methods()
    bridge = bridge_expectations()
    allowed = allowed_actions_from_boundary()
    poller_text = read_text(ROOT / "tools" / "nexus_command_poller.py")

    findings: List[Dict[str, str]] = []
    findings.extend(_findings_from_missing("mcp_tool_missing_from_guide", actual_tools - guide_tools, "warn"))
    findings.extend(_findings_from_missing("guide_tool_not_implemented", guide_tools - actual_tools, "fail"))
    if bridge["bridge_posts_integrate"] and not bridge["post_integrate_supported"]:
        findings.append({
            "id": "bridge_route_mismatch:integrate_civforge_post_missing",
            "severity": "fail",
            "detail": "bridge/civforge_http_bridge.py posts to /integrate/civforge but backend has no POST route",
        })
    if allowed != ["sync_config"]:
        findings.append({
            "id": "boundary_allowed_actions_unexpected",
            "severity": "fail",
            "detail": f"expected ['sync_config'], found {allowed}",
        })
    if 'action != "sync_config"' not in poller_text and "action != 'sync_config'" not in poller_text:
        findings.append({
            "id": "poller_allowed_actions_not_strict",
            "severity": "fail",
            "detail": "poller must block every Nexus action except sync_config",
        })
    for rel in stale_auth_bridge_refs():
        findings.append({
            "id": f"stale_auth_bridge_ref:{rel}",
            "severity": "warn",
            "detail": "active docs/tooling should point to sibling dawsos-auth-prototype, not removed tools/auth-prototype bridge scripts",
        })

    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    warn_count = sum(1 for f in findings if f["severity"] == "warn")
    status = "fail" if fail_count else ("warn" if warn_count else "pass")
    report = {
        "schema": "civforge.contract_parity.v1",
        "generated_at": utc_now(),
        "status": status,
        "summary": {
            "route_count": sum(len(methods) for methods in routes.values()),
            "mcp_tool_count": len(actual_tools),
            "documented_mcp_tool_count": len(guide_tools),
            "finding_count": len(findings),
            "fail_count": fail_count,
            "warn_count": warn_count,
        },
        "routes": routes,
        "mcp_tools": sorted(actual_tools),
        "documented_mcp_tools": sorted(guide_tools),
        "nexus_allowed_actions": allowed,
        "bridge": bridge,
        "findings": findings,
    }
    if write_files:
        write_report(report)
    return report


def write_report(report: Dict[str, Any]) -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    json_path = RECEIPTS / "civforge-contract-parity-latest.json"
    md_path = RECEIPTS / "civforge-contract-parity-latest.md"
    receipt_path = RECEIPTS / "civforge-contract-parity-receipt-latest.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# CivForge Contract Parity",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- status: `{report['status']}`",
        f"- routes: `{report['summary']['route_count']}`",
        f"- mcp_tools: `{report['summary']['mcp_tool_count']}`",
        f"- findings: `{report['summary']['finding_count']}`",
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
        "action": "civforge_contract_parity",
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
