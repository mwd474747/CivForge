#!/usr/bin/env python3
"""
CivForge HTTP bridge — local control of the :8080 governance kernel.

Used by Cursor (local executor) and scripts. Grok swarm on grok.com does not
run on this Mac; it assigns work packs — Cursor executes and receipts prove land.

Usage:
    from bridge.civforge_http_bridge import get_state, advance_cycle
    python3 bridge/civforge_http_bridge.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from typing import Any, Dict, Optional

import requests

from backend.civforge_auth_headers import civforge_auth_headers

BASE = "http://localhost:8080"


def _request(method: str, path: str, json_body: Optional[Dict[str, Any]] = None) -> requests.Response:
    return requests.request(
        method,
        f"{BASE}{path}",
        json=json_body,
        headers=civforge_auth_headers(),
        timeout=15,
    )


def get_state() -> Dict[str, Any]:
    r = _request("GET", "/state")
    r.raise_for_status()
    return r.json()


def send_work_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    r = _request("POST", "/integrate/civforge", pack)
    r.raise_for_status()
    return r.json()


def advance_cycle() -> Dict[str, Any]:
    r = _request("POST", "/advance_turn")
    r.raise_for_status()
    return r.json()


def propose_work(
    action: str = "gravity_mosaic_update",
    details: Optional[Dict[str, Any]] = None,
    investment: int = 3,
) -> Dict[str, Any]:
    payload = {"action": action, "details": details or {}, "investment": investment}
    r = _request("POST", "/governance/propose", payload)
    r.raise_for_status()
    return r.json()


def gate_proposal(proposal_id: str, fun_score_override: Optional[float] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"proposal_id": proposal_id}
    if fun_score_override is not None:
        payload["fun_score_override"] = fun_score_override
    r = _request("POST", "/governance/gate", payload)
    r.raise_for_status()
    return r.json()


def get_gravity_recommendation() -> Dict[str, Any]:
    r = _request("GET", "/governance/gravity_deploy_recommendation")
    r.raise_for_status()
    return r.json()


def test_bridge() -> None:
    print("=== CivForge HTTP Bridge Test ===")
    try:
        state = get_state()
        print("Backend reachable. Turn:", state.get("current_turn"), "Fun:", state.get("fun_score"))
        rec = get_gravity_recommendation()
        print("Recommendation:", rec.get("decision"))
        print("Bridge OK against :8080")
    except Exception as exc:
        print("Bridge test failed:", exc)
        print("Start kernel: bash tools/start-kernel-8080.sh")


if __name__ == "__main__":
    test_bridge()
