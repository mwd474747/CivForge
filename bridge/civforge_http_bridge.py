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

from typing import Any, Dict, Optional

import requests

BASE = "http://localhost:8080"


def get_state() -> Dict[str, Any]:
    r = requests.get(f"{BASE}/state", timeout=10)
    r.raise_for_status()
    return r.json()


def send_work_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(f"{BASE}/integrate/civforge", json=pack, timeout=15)
    r.raise_for_status()
    return r.json()


def advance_cycle() -> Dict[str, Any]:
    r = requests.post(f"{BASE}/advance_turn", timeout=15)
    r.raise_for_status()
    return r.json()


def propose_work(
    action: str = "gravity_mosaic_update",
    details: Optional[Dict[str, Any]] = None,
    investment: int = 3,
) -> Dict[str, Any]:
    payload = {"action": action, "details": details or {}, "investment": investment}
    r = requests.post(f"{BASE}/governance/propose", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def gate_proposal(proposal_id: str, fun_score_override: Optional[float] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"proposal_id": proposal_id}
    if fun_score_override is not None:
        payload["fun_score_override"] = fun_score_override
    r = requests.post(f"{BASE}/governance/gate", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def get_gravity_recommendation() -> Dict[str, Any]:
    r = requests.get(f"{BASE}/governance/gravity_deploy_recommendation", timeout=10)
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
