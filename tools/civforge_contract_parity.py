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
    bridge = read_text(ROOT / "bridge" / "civforge_http_bridge.py")
    wants_post_integrate = bool(re.search(r"requests\.post\([^)]*/integrate/civforge", bridge, re.S))
    routes = route_methods()
    return {
        "bridge_posts_integrate": wants_post_integrate,
        "integrate_methods": routes.get("/integrate/civforge", []),
        "post_integrate_supported": "POST" in routes.get("/integrate/civforge", []),
    }


def swarm_alignment_checks() -> Dict[str, Any]:
    """Verify swarm-class docs and role_registry align with EXECUTION_LANE_V2."""
    registry_path = ROOT / "agents" / "role_registry.json"
    lane_doc = read_text(ROOT / "docs" / "EXECUTION_LANE_V2.md")
    swarm_doc = read_text(ROOT / "docs" / "CIVFORGE_SWARM_CLASS_V1.md")
    wp_template = read_text(ROOT / "docs" / "WORK_PACK_TEMPLATE_V1.md")
    agents_md = read_text(ROOT / "AGENTS.md")

    registry: Dict[str, Any] = {}
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

    sim_api = read_text(ROOT / "backend" / "sim_api.py")
    forge_role = next(
        (r for r in registry.get("roles", []) if isinstance(r, dict) and r.get("id") == "forge-coordinator"),
        {},
    )
    kernel_id = forge_role.get("kernel_agent_id", "")
    sim_registers_kernel = bool(
        re.search(r"register_agent\(\s*FORGE_COORDINATOR_ID", sim_api)
        and 'FORGE_COORDINATOR_ID = "forge-coordinator"' in read_text(ROOT / "core" / "swarm_join.py")
    )

    role_ids = {r.get("id") for r in registry.get("roles", []) if isinstance(r, dict)}
    lanes = registry.get("execution_lanes", {})
    lane_keys = set(lanes.keys()) if isinstance(lanes, dict) else set()

    return {
        "swarm_class_doc_present": bool(swarm_doc.strip()),
        "work_pack_template_present": bool(wp_template.strip()),
        "lane_doc_refs_swarm_class": "CIVFORGE_SWARM_CLASS_V1" in lane_doc,
        "agents_md_refs_swarm_class": "CIVFORGE_SWARM_CLASS_V1" in agents_md,
        "execution_lanes": sorted(lane_keys),
        "required_lane_keys": ["grok_swarm", "cursor", "openclaw"],
        "role_openclaw_chief_of_staff": "openclaw-chief-of-staff" in role_ids,
        "role_forge_coordinator": "forge-coordinator" in role_ids,
        "role_grok_swarm": "grok-swarm" in role_ids,
        "dawsos_role_map_present": bool(registry.get("dawsos_role_map")),
        "naming_notes_present": bool(registry.get("naming_notes")),
        "wp_template_has_side_effect_class": "side_effect_class" in wp_template,
        "forge_coordinator_kernel_id": kernel_id,
        "sim_api_registers_kernel_id": sim_registers_kernel,
    }


def swarm_alignment_findings(checks: Dict[str, Any]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    if not checks["swarm_class_doc_present"]:
        findings.append({"id": "swarm_doc_missing", "severity": "fail", "detail": "docs/CIVFORGE_SWARM_CLASS_V1.md missing"})
    if not checks["work_pack_template_present"]:
        findings.append({"id": "wp_template_missing", "severity": "fail", "detail": "docs/WORK_PACK_TEMPLATE_V1.md missing"})
    if not checks["lane_doc_refs_swarm_class"]:
        findings.append({"id": "lane_doc_swarm_ref", "severity": "fail", "detail": "EXECUTION_LANE_V2.md must reference CIVFORGE_SWARM_CLASS_V1"})
    if not checks["agents_md_refs_swarm_class"]:
        findings.append({"id": "agents_md_swarm_ref", "severity": "warn", "detail": "AGENTS.md should reference CIVFORGE_SWARM_CLASS_V1"})
    missing_lanes = sorted(set(checks["required_lane_keys"]) - set(checks["execution_lanes"]))
    if missing_lanes:
        findings.append({
            "id": "role_registry_lanes",
            "severity": "fail",
            "detail": f"role_registry missing execution_lanes: {missing_lanes}",
        })
    for key, label in (
        ("role_openclaw_chief_of_staff", "openclaw-chief-of-staff"),
        ("role_forge_coordinator", "forge-coordinator"),
        ("role_grok_swarm", "grok-swarm"),
    ):
        if not checks[key]:
            findings.append({
                "id": f"role_registry_missing:{label}",
                "severity": "fail",
                "detail": f"agents/role_registry.json missing role id {label}",
            })
    if not checks["dawsos_role_map_present"]:
        findings.append({"id": "dawsos_role_map_missing", "severity": "fail", "detail": "role_registry missing dawsos_role_map"})
    if not checks["naming_notes_present"]:
        findings.append({"id": "naming_notes_missing", "severity": "warn", "detail": "role_registry missing naming_notes for grok vs forge-coordinator"})
    if not checks["wp_template_has_side_effect_class"]:
        findings.append({"id": "wp_template_side_effect", "severity": "fail", "detail": "WORK_PACK_TEMPLATE must define side_effect_class taxonomy"})
    if checks.get("forge_coordinator_kernel_id") != "forge-coordinator":
        findings.append({
            "id": "forge_coordinator_kernel_id",
            "severity": "fail",
            "detail": "role_registry forge-coordinator.kernel_agent_id must be forge-coordinator",
        })
    if not checks.get("sim_api_registers_kernel_id"):
        findings.append({
            "id": "sim_api_kernel_registration",
            "severity": "fail",
            "detail": "sim_api.py must register forge-coordinator kernel AgentBrain id",
        })
    return findings


def _findings_from_missing(prefix: str, missing: Iterable[str], severity: str) -> List[Dict[str, str]]:
    return [{"id": f"{prefix}:{item}", "severity": severity, "detail": item} for item in sorted(missing)]


def build_report(write_files: bool = True) -> Dict[str, Any]:
    actual_tools = set(mcp_tool_names())
    guide_tools = set(documented_mcp_tools())
    routes = route_methods()
    bridge = bridge_expectations()
    allowed = allowed_actions_from_boundary()
    poller_text = read_text(ROOT / "tools" / "nexus_command_poller.py")
    swarm_checks = swarm_alignment_checks()

    findings: List[Dict[str, str]] = []
    findings.extend(swarm_alignment_findings(swarm_checks))
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
        "swarm_alignment": swarm_checks,
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
