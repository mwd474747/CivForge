#!/usr/bin/env python3
"""
Headless Observer + Bridge for CivForge (Python-first, post Godot MVP removal).

This is the primary way the agent (Grok) interacts with the running FastAPI governance
workspace in autonomous / terminal-driven mode.

- Queries /state
- Requests agent decisions via /governance/gravity_deploy_recommendation or core brains
- Can trigger /advance_turn or /governance/advance_and_log cycles
- Logs receipts and can invoke the gravity deploy tool under governance

The actual gravity-mosaic project remains 100% separate. All real changes to it
must go through tools/deploy-gravity-mosaic/deploy.sh (literal full-disk verification enforced).
"""

import requests
import subprocess
from pathlib import Path
import json
from datetime import datetime

BASE = "http://localhost:8080"
DEPLOY_TOOL = Path(__file__).parent.parent / "tools" / "deploy-gravity-mosaic" / "deploy.sh"

def get_state():
    r = requests.get(f"{BASE}/state", timeout=10)
    r.raise_for_status()
    return r.json()

def advance_cycle():
    r = requests.post(f"{BASE}/advance_turn", timeout=15)
    r.raise_for_status()
    return r.json()

def propose_gravity_work(action: str = "gravity_mosaic_update", details: dict = None):
    payload = {"action": action, "details": details or {"source": "headless_observer"}, "investment": 3}
    r = requests.post(f"{BASE}/governance/propose", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_gravity_recommendation():
    r = requests.get(f"{BASE}/governance/gravity_deploy_recommendation", timeout=10)
    r.raise_for_status()
    return r.json()

def run_governed_gravity_deploy(dry_run: bool = True):
    """
    Example of governed execution.
    In real use the human (or a very trusted sub-process) runs the deploy.sh.
    Here we at least get the recommendation + current gate status first.
    """
    rec = get_gravity_recommendation()
    print("[Headless] Gravity recommendation from brains + FunForge:")
    print(json.dumps(rec, indent=2))

    if dry_run:
        print("\n[Headless] DRY RUN — not actually invoking deploy.sh.")
        print("To execute for real (after human gate):")
        print(f"  cd /Users/michaeldawson/CivForge && ./tools/deploy-gravity-mosaic/deploy.sh")
        return {"dry_run": True, "recommendation": rec}

    # Real invocation would be done by the user or a gated wrapper.
    # We refuse to auto-run the deploy tool from here to respect the strict literal rules.
    print("[Headless] Refusing automatic execution of deploy.sh. Run it manually after reviewing the receipt and state.")
    return {"executed": False, "reason": "human gate required for literal gravity deploy"}

def main():
    print("CivForge Headless Observer (Python bridge) — realigned, no Godot MVP")
    print("=" * 60)
    try:
        state = get_state()
        print("Current workspace state (fun/quality, work items, recent receipts):")
        print(f"  Turn: {state.get('current_turn')}")
        print(f"  Fun/Quality: {state.get('fun_score')}")
        print(f"  Player territories (active items): {state['player'].get('territories')}")
        print(f"  Recent receipts: {len(state.get('receipts', []))}")
    except Exception as e:
        print(f"Could not reach backend at {BASE}: {e}")
        print("Start it with: cd backend && python3 -m uvicorn sim_api:app --reload --host 0.0.0.0 --port 8080")

    print("\n--- Agent decision for gravity work ---")
    try:
        rec = get_gravity_recommendation()
        print(rec.get("decision"))
        print(rec.get("comment"))
    except Exception as e:
        print("Recommendation unavailable:", e)

    print("\nHeadless observer ready. Use /state, /advance_turn, /governance/* from terminal or other agents.")

if __name__ == "__main__":
    main()
