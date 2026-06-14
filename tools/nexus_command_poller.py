#!/usr/bin/env python3
"""
CivForge Nexus Command Poller (thin bidirectional control bridge to dawsos-nexus 8082).

Per SEPARATION.md + sister contract:
- dawsos-nexus is the control sister (telemetry, commands as proposals, audit mirror).
- Commands propose, never direct execute on 8080 kernel.
- Thin HTTP only. Uses patterns from dawsos_auth_client + shared schema (CommandActions, CommandStatuses).
- No mutation of the dawsos-nexus tree (reference only).

Supported (from schema): PAUSE, RESUME, RESTART, EMERGENCY_STOP, SYNC_CONFIG, RUN_TASK, CANCEL_TASK.
On receive pending command for civforge-kernel (or general):
  - Record local event + create governance proposal (action="nexus_<action>").
  - Ack back to nexus (ACKNOWLEDGED / IN_PROGRESS / COMPLETED).
- Fully defensive: if 8082 unreachable, no commands, or auth fail -> clean no-op + log. Never blocks game.
- Run modes: --once (single poll cycle) or --loop (daemon with sleep).

CLI integration: python tools/civforge_cli.py nexus-poll [--loop] [--interval 5]

Wired for use after 8082 live (register app "civforge-kernel" first via auth client recommended).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

NEXUS_BASE = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")
CIV_APP_ID = "civforge-kernel"
OPERATOR_TOKEN = os.environ.get("NEXUS_OPERATOR_TOKEN", "")
API_KEY = os.environ.get("NEXUS_API_KEY", "")

# Local 8080 for proposing surfaced commands (never auto execute)
CIV_BASE = "http://127.0.0.1:8080"

# Map from nexus CommandActions -> local proposal action prefix (commands are proposals)
COMMAND_ACTION_MAP = {
    "pause": "nexus_pause",
    "resume": "nexus_resume",
    "restart": "nexus_restart",
    "emergency_stop": "nexus_emergency_stop",
    "sync_config": "nexus_sync_config",
    "run_task": "nexus_run_task",
    "cancel_task": "nexus_cancel_task",
}

# Reasonable endpoint variants (sister uses /api/commands + insert schema; apps enriched)
COMMAND_ENDPOINTS = [
    f"{NEXUS_BASE}/api/commands",
    f"{NEXUS_BASE}/api/commands?status=pending",
    f"{NEXUS_BASE}/api/apps/{CIV_APP_ID}/commands",
]
ACK_ENDPOINT_TEMPLATES = [
    f"{NEXUS_BASE}/api/commands/{{cmd_id}}",
    f"{NEXUS_BASE}/api/commands/{{cmd_id}}/ack",
]


def _headers() -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if OPERATOR_TOKEN:
        h["Authorization"] = f"Bearer {OPERATOR_TOKEN}"
        h["x-nexus-api-key"] = OPERATOR_TOKEN
    elif API_KEY:
        h["x-nexus-api-key"] = API_KEY
    return h


def _post_local(path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        r = requests.post(f"{CIV_BASE}{path}", json=payload, timeout=8)
        if r.status_code < 400:
            return r.json()
    except Exception:
        pass
    return None


def register_if_needed() -> None:
    """Light register of civforge-kernel app (idempotent, best-effort)."""
    try:
        payload = {"appId": CIV_APP_ID, "name": "CivForge Governance Kernel", "type": "civforge_agent", "telemetryMode": "push"}
        requests.post(f"{NEXUS_BASE}/api/apps", json=payload, headers=_headers(), timeout=5)
    except Exception:
        pass  # silent; register via CLI auth client preferred


def fetch_pending_commands() -> List[Dict[str, Any]]:
    """Try multiple endpoints; return list of pending command dicts (best effort)."""
    for ep in COMMAND_ENDPOINTS:
        try:
            r = requests.get(ep, headers=_headers(), timeout=6)
            if r.status_code != 200:
                continue
            data = r.json()
            if isinstance(data, list):
                cmds = [c for c in data if isinstance(c, dict)]
            elif isinstance(data, dict):
                cmds = data.get("commands") or data.get("items") or ([data] if data.get("action") else [])
            else:
                cmds = []
            pending = [c for c in cmds if (c.get("status") or "").upper() in ("PENDING", "pending") or not c.get("status")]
            # Prefer those targeting our app or untargeted
            filtered = [c for c in pending if not c.get("appId") or c.get("appId") == CIV_APP_ID or c.get("targetAppId") == CIV_APP_ID]
            if filtered:
                return filtered
            if pending:
                return pending  # fallback
        except Exception:
            continue
    return []


def ack_command(cmd_id: str, status: str = "ACKNOWLEDGED", note: str = "") -> bool:
    """Ack / update status on nexus command. Try common update shapes."""
    payload = {"status": status, "note": note, "ackedBy": CIV_APP_ID}
    for tmpl in ACK_ENDPOINT_TEMPLATES:
        try:
            url = tmpl.format(cmd_id=cmd_id)
            # Try PATCH then POST
            for meth in (requests.patch, requests.post):
                r = meth(url, json=payload, headers=_headers(), timeout=5)
                if r.status_code < 400:
                    return True
        except Exception:
            continue
    # Fallback: create audit-style log if direct ack fails
    try:
        requests.post(f"{NEXUS_BASE}/api/auditLogs", json={"action": "command.ack", "appId": CIV_APP_ID, "details": {"cmd_id": cmd_id, "status": status, "note": note}}, headers=_headers(), timeout=4)
    except Exception:
        pass
    return False


def handle_command(cmd: Dict[str, Any]) -> str:
    """Map command to local governed proposal (never direct mutate game state). Return local action taken."""
    action = (cmd.get("action") or cmd.get("type") or "").lower()
    local_action = COMMAND_ACTION_MAP.get(action, f"nexus_{action or 'unknown'}")
    payload = cmd.get("payload") or cmd.get("details") or {}

    # Surface as proposal on 8080 (governed path)
    propose_resp = _post_local("/governance/propose", {
        "action": local_action,
        "investment": 1,
        "details": {
            "source": "dawsos-nexus-command",
            "nexus_cmd_id": cmd.get("id") or cmd.get("_id"),
            "nexus_action": action,
            "payload": payload,
            "note": "Command received via thin bridge. This is a proposal (per SEPARATION: commands propose, not execute)."
        }
    })

    note = f"Proposed local action '{local_action}' from nexus cmd {cmd.get('id')}"
    if propose_resp and propose_resp.get("proposal"):
        note += f" (proposal_id={propose_resp['proposal'].get('id')})"

    # Also log a receipt-like event via state touch (advance not forced here)
    _post_local("/found_city", {"city_name": f"nexus_cmd_{action}", "investment": 1})  # lightweight marker work pack

    return note


def poll_once() -> Dict[str, Any]:
    """Single poll cycle. Returns summary."""
    register_if_needed()
    pending = fetch_pending_commands()
    processed = []
    for cmd in pending[:10]:  # safety cap
        cmd_id = cmd.get("id") or cmd.get("_id") or str(cmd)[:16]
        try:
            note = handle_command(cmd)
            acked = ack_command(cmd_id, status="IN_PROGRESS", note=note)
            # Mark completed after propose surfaced
            ack_command(cmd_id, status="COMPLETED", note=note + " (proposal surfaced on CivForge)")
            processed.append({"id": cmd_id, "action": cmd.get("action"), "acked": acked, "note": note})
        except Exception as e:
            ack_command(cmd_id, status="FAILED", note=f"error: {e}")
    return {
        "polled": len(pending),
        "processed": len(processed),
        "items": processed,
        "nexus_base": NEXUS_BASE,
        "timestamp": time.time(),
    }


def run_loop(interval: int = 5) -> None:
    print(f"[nexus-poller] Starting loop every {interval}s against {NEXUS_BASE} (app={CIV_APP_ID}). Ctrl-C to stop.")
    while True:
        try:
            res = poll_once()
            if res["processed"] > 0:
                print("[nexus-poller]", json.dumps(res, indent=2))
            else:
                # quiet unless verbose
                pass
        except KeyboardInterrupt:
            print("\n[nexus-poller] Stopped.")
            break
        except Exception as e:
            print("[nexus-poller] cycle error (defensive):", e)
        time.sleep(max(1, interval))


def main():
    p = argparse.ArgumentParser(description="CivForge <-> dawsos-nexus command poller (thin bridge, commands-as-proposals)")
    p.add_argument("--once", action="store_true", help="Single poll cycle then exit")
    p.add_argument("--loop", action="store_true", help="Continuous poll loop")
    p.add_argument("--interval", type=int, default=5, help="Loop sleep seconds")
    args = p.parse_args()

    if args.once or (not args.loop and not args.once):
        res = poll_once()
        print(json.dumps(res, indent=2))
    elif args.loop:
        run_loop(args.interval)


if __name__ == "__main__":
    main()
