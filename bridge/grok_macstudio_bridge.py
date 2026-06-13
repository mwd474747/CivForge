#!/usr/bin/env python3
"""
Grok Mac Studio Bridge — Direct control of the canonical CivForge backend
running on this Mac Studio (localhost:8080 + core/).

This is the native bridge the main orchestration swarm (ForgeMaster-Grok + sub-agents)
uses to drive the realigned FastAPI governance workspace.

It talks to the exact stack that was locked in:
- FastAPI sim_api:app on 8080
- core/ (AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore with SQLite option)

Usage from main agent / other swarm members:
    from bridge.grok_macstudio_bridge import send_work_pack, get_state, advance_cycle

All activity remains advisory for the separate gravity-mosaic project.
Real mutations only happen via tools/deploy-gravity-mosaic/deploy.sh after receipts + gate.
"""

import requests
import json
from typing import Dict, Any

BASE = "http://localhost:8080"

def get_state() -> Dict[str, Any]:
    """Return current governance workspace state (matches the earlier FastAPI shape)."""
    r = requests.get(f"{BASE}/state", timeout=10)
    r.raise_for_status()
    return r.json()

def send_work_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a work pack / proposal into the system.
    Posts to /integrate/civforge (existing hook) and returns the full response + receipt.
    """
    r = requests.post(f"{BASE}/integrate/civforge", json=pack, timeout=15)
    r.raise_for_status()
    return r.json()

def advance_cycle() -> Dict[str, Any]:
    """Trigger one full governance cycle (agents decide + FunForge + gate + receipt)."""
    r = requests.post(f"{BASE}/advance_turn", timeout=15)
    r.raise_for_status()
    return r.json()

def propose_work(action: str = "gravity_mosaic_update", details: Dict[str, Any] = None, investment: int = 3) -> Dict[str, Any]:
    """Create a proposal for gravity-mosaic work (or other)."""
    payload = {"action": action, "details": details or {}, "investment": investment}
    r = requests.post(f"{BASE}/governance/propose", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def gate_proposal(proposal_id: str, fun_score_override: float = None) -> Dict[str, Any]:
    """Run FunForge gate on a proposal."""
    payload = {"proposal_id": proposal_id}
    if fun_score_override is not None:
        payload["fun_score_override"] = fun_score_override
    r = requests.post(f"{BASE}/governance/gate", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_gravity_recommendation() -> Dict[str, Any]:
    """Ask the registered AgentBrains + FunForge for current gravity-mosaic advice."""
    r = requests.get(f"{BASE}/governance/gravity_deploy_recommendation", timeout=10)
    r.raise_for_status()
    return r.json()

def test_bridge():
    print("=== Grok Mac Studio Bridge Test ===")
    try:
        state = get_state()
        print("Backend reachable. Turn:", state.get("current_turn"), "Fun/Quality:", state.get("fun_score"))
        rec = get_gravity_recommendation()
        print("Recommendation:", rec.get("decision"))
        print("Comment:", rec.get("comment"))
        print("✅ Bridge fully functional against the Mac Studio canonical backend (8080 + core/)")
    except Exception as e:
        print("Bridge test failed:", e)
        print("Is the backend running? (python3 -m uvicorn sim_api:app --reload --host 0.0.0.0 --port 8080)")

if __name__ == "__main__":
    test_bridge()
