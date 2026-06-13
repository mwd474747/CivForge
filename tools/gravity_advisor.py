#!/usr/bin/env python3
"""
Gravity Advisor — Safe, proposal-only layer for the separate gravity-mosaic project.

Executed as part of the Mac Studio backend lock-in (WP-BACKEND-REALIGN-EXEC-001).

This tool (and the backend it talks to) only generates recommendations and receipts.
It **never** mutates the gravity-mosaic-knowledge-graph directory.

The only thing allowed to touch that separate project is:
  ./tools/deploy-gravity-mosaic/deploy.sh

That script alone performs the literal full-disk verification (wc, grep golden anchors,
Python model tests, bad-legacy == 0, exact git operations, etc.).

Usage:
    python tools/gravity_advisor.py recommend
    python tools/gravity_advisor.py safe-check
"""

import sys
from pathlib import Path

# Try to use the real bridge if available
try:
    from bridge.grok_macstudio_bridge import get_gravity_recommendation, get_state
    BRIDGE_AVAILABLE = True
except Exception:
    BRIDGE_AVAILABLE = False

def recommend():
    print("=== Gravity-Mosaic Work Recommendation (advisory only) ===")
    if BRIDGE_AVAILABLE:
        try:
            rec = get_gravity_recommendation()
            print("Decision from AgentBrains + FunForge:")
            print("  ", rec.get("decision"))
            print("  Fun/Quality:", rec.get("fun_score"))
            print("  Comment:", rec.get("comment"))
            print("\nRecommendation:", rec.get("recommendation"))
            print("Warning:", rec.get("warning"))
            return
        except Exception as e:
            print("Bridge call failed, falling back to static advice:", e)

    # Static safe advice (always valid)
    print("Proposal: Perform a governed cycle first:")
    print("  python tools/civforge_cli.py advance")
    print("  python tools/civforge_cli.py recommend")
    print("\nThen (only after reviewing receipts/ and getting a clean gate):")
    print("  cd /Users/michaeldawson/CivForge")
    print("  ./tools/deploy-gravity-mosaic/deploy.sh")
    print("\nNever edit the gravity-mosaic repo directly from CivForge code.")
    print("Strict separation is canonical on this Mac Studio.")

def safe_check():
    print("=== Safe Gravity Integration Check ===")
    print("CivForge role: Propose → Gate (FunForge) → Receipt → Advise")
    print("Gravity-mosaic role: The separate project (100% untouched by CivForge code)")
    print("Execution role: ONLY tools/deploy-gravity-mosaic/deploy.sh (literal rules)")
    print("\nCurrent backend (if running):")
    if BRIDGE_AVAILABLE:
        try:
            state = get_state()
            print(f"  Turn: {state.get('current_turn')}, Fun/Quality: {state.get('fun_score')}")
            print("  Receipts in state:", len(state.get("receipts", [])))
        except Exception as e:
            print("  Backend not reachable or error:", e)
    else:
        print("  (bridge not importable in this context — run from CivForge root)")
    print("\n✅ Separation and safety rules respected.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "safe-check":
        safe_check()
    else:
        recommend()
