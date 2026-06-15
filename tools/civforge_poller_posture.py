#!/usr/bin/env python3
"""Report CivForge Nexus poller daemon posture."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "receipts"
PID_FILE = Path(os.environ.get("CIVFORGE_POLLER_PID_FILE", "/tmp/civforge-poller.pid"))
LOG_FILE = Path(os.environ.get("CIVFORGE_POLLER_LOG", "/tmp/civforge-poller.log"))
KEY_FILE = Path.home() / ".openclaw" / "runtime" / "nexus-satellite-api-keys.json"
NEXUS_URL = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_pid() -> Optional[int]:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def process_command(pid: Optional[int]) -> str:
    if not pid:
        return ""
    proc = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, check=False)
    return proc.stdout.strip()


def screen_sessions() -> List[str]:
    proc = subprocess.run(["screen", "-ls"], capture_output=True, text=True, check=False)
    return [line.strip() for line in proc.stdout.splitlines() if "civforge-poller" in line]


def key_file_posture() -> Dict[str, Any]:
    if not KEY_FILE.exists():
        return {"exists": False, "mode": None, "has_civforge_kernel": False}
    mode = stat.S_IMODE(KEY_FILE.stat().st_mode)
    has_key = False
    try:
        data = json.loads(KEY_FILE.read_text(encoding="utf-8"))
        has_key = bool(data.get("civforge-kernel", {}).get("apiKey"))
    except Exception:
        has_key = False
    return {"exists": True, "mode": oct(mode), "has_civforge_kernel": has_key}


def nexus_health() -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{NEXUS_URL}/api/health", timeout=4) as resp:
            body = resp.read().decode()
        return {"ok": True, "status_code": 200, "body": body[:240]}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def log_tail(max_lines: int = 8) -> List[str]:
    if not LOG_FILE.exists():
        return []
    try:
        return LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except Exception:
        return []


def build_report(write_files: bool = True) -> Dict[str, Any]:
    pid = read_pid()
    alive = pid_alive(pid) if pid else False
    key = key_file_posture()
    nexus = nexus_health()
    findings: List[Dict[str, str]] = []
    if not alive:
        findings.append({"severity": "warn", "id": "poller_process_not_alive", "detail": str(PID_FILE)})
    if not key["exists"] or not key["has_civforge_kernel"]:
        findings.append({"severity": "fail", "id": "missing_civforge_satellite_key", "detail": str(KEY_FILE)})
    elif key["mode"] != "0o600":
        findings.append({"severity": "warn", "id": "satellite_key_mode_not_0600", "detail": str(KEY_FILE)})
    if not nexus["ok"]:
        findings.append({"severity": "warn", "id": "nexus_health_unreachable", "detail": nexus.get("error", "")})
    fail_count = sum(1 for f in findings if f["severity"] == "fail")
    warn_count = sum(1 for f in findings if f["severity"] == "warn")
    report = {
        "schema": "civforge.poller_posture.v1",
        "generated_at": utc_now(),
        "status": "fail" if fail_count else ("warn" if warn_count else "pass"),
        "summary": {"fail_count": fail_count, "warn_count": warn_count, "finding_count": len(findings)},
        "pid_file": str(PID_FILE),
        "pid": pid,
        "pid_alive": alive,
        "process_command": process_command(pid),
        "screen_sessions": screen_sessions(),
        "log_file": str(LOG_FILE),
        "log_tail": log_tail(),
        "key_file": key,
        "nexus": nexus,
        "findings": findings,
    }
    if write_files:
        write_report(report)
    return report


def write_report(report: Dict[str, Any]) -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    json_path = RECEIPTS / "civforge-poller-posture-latest.json"
    md_path = RECEIPTS / "civforge-poller-posture-latest.md"
    receipt_path = RECEIPTS / "civforge-poller-posture-receipt-latest.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# CivForge Poller Posture",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- status: `{report['status']}`",
        f"- pid: `{report.get('pid')}`",
        f"- pid_alive: `{report.get('pid_alive')}`",
        f"- nexus_ok: `{report.get('nexus', {}).get('ok')}`",
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
        "action": "civforge_poller_posture",
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
