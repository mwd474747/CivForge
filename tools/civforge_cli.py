#!/usr/bin/env python3
"""
CivForge CLI — Terminal driver for the realigned FastAPI governance workspace.

Replaces the old Godot "press End Turn / F5" experience with pure terminal commands
the user loves ("run that in terminal for me").

Commands:
  python tools/civforge_cli.py status
  python tools/civforge_cli.py advance
  python tools/civforge_cli.py found "Gravity formula node"
  python tools/civforge_cli.py recommend
  python tools/civforge_cli.py propose-deploy
  python tools/civforge_cli.py gate <proposal-id>
  python tools/civforge_cli.py run-deploy   # shows the strict command (does not auto-execute)

All real changes to the *separate* gravity-mosaic project still require running
the verified deploy.sh manually after governance receipts.
"""

import argparse
import requests
import json
import subprocess
from pathlib import Path

BASE = "http://localhost:8080"
ROOT = Path(__file__).parent.parent

def _get(path):
    return requests.get(f"{BASE}{path}", timeout=10).json()

def _post(path, json=None):
    return requests.post(f"{BASE}{path}", json=json, timeout=15).json()

def cmd_status():
    s = _get("/state")
    print(json.dumps({
        "turn": s["current_turn"],
        "fun_score": s["fun_score"],
        "player": s["player"],
        "recent_receipts": s.get("receipts", [])[-3:],
        "recent_events": s.get("recent_events", []),
    }, indent=2))

def cmd_advance():
    r = _post("/advance_turn")
    print("Cycle advanced.")
    print(json.dumps(r.get("receipt", {}), indent=2))

def cmd_found(name: str, investment: int = 4):
    r = _post("/found_city", json={"city_name": name, "investment": investment})
    print(json.dumps(r, indent=2))

def cmd_recommend():
    r = _get("/governance/gravity_deploy_recommendation")
    print(json.dumps(r, indent=2))

def cmd_propose(action: str = "gravity_mosaic_update"):
    r = _post("/governance/propose", json={"action": action, "investment": 3, "details": {"via": "cli"}})
    print(json.dumps(r, indent=2))

def cmd_gate(proposal_id: str):
    r = _post("/governance/gate", json={"proposal_id": proposal_id})
    print(json.dumps(r, indent=2))

def cmd_run_deploy():
    print("To perform a governed deploy of changes to the SEPARATE gravity-mosaic project:")
    print("  1. Make changes ONLY in /Users/michaeldawson/gravity-mosaic-knowledge-graph (literal disk)")
    print("  2. cd /Users/michaeldawson/CivForge")
    print("  3. ./tools/deploy-gravity-mosaic/deploy.sh")
    print("\nThe deploy.sh script itself does full literal verification (wc, grep golden anchors, Python model tests, 0 bad legacy, etc.).")
    print("Never bypass it. Receipts from this CLI + backend should be referenced in the commit if relevant.")

def main():
    p = argparse.ArgumentParser(description="CivForge governance CLI (FastAPI workspace)")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show current /state (fun, resources, receipts)")
    sub.add_parser("advance", help="Run one full governance cycle (agents + FunForge + gate + receipt)")
    sub.add_parser("recommend", help="Get current gravity-mosaic recommendation from the brains")
    sub.add_parser("propose-deploy", help="Propose a gravity deploy work pack")

    pf = sub.add_parser("found", help="Initiate a governed work pack (the 'found_city' surface)")
    pf.add_argument("name", help="Work pack / city name")
    pf.add_argument("--investment", type=int, default=4)

    pg = sub.add_parser("gate", help="Gate a proposal by id (FunForge quality check)")
    pg.add_argument("proposal_id")

    sub.add_parser("run-deploy", help="Print the exact safe command to run the strict gravity deploy tool")

    # === New commands added per Mac Studio backend lock-in receipt (swarm execution) ===
    sub.add_parser("mcp-stub", help="MCP compatibility stub — shows how endpoints can be exposed as MCP tools later")
    sub.add_parser("advisor", help="Safe gravity advisor (proposal-only, never auto-executes deploy.sh)")

    args = p.parse_args()

    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "advance":
        cmd_advance()
    elif args.cmd == "recommend":
        cmd_recommend()
    elif args.cmd == "propose-deploy":
        cmd_propose()
    elif args.cmd == "found":
        cmd_found(args.name, args.investment)
    elif args.cmd == "gate":
        cmd_gate(args.proposal_id)
    elif args.cmd == "run-deploy":
        cmd_run_deploy()
    elif args.cmd == "mcp-stub":
        print("MCP stub upgraded → ready to expose /advance_turn, /governance/propose, /governance/gate, /governance/gravity_deploy_recommendation as future MCP tools.")
        print("Current backend already provides the raw HTTP surface at localhost:8080.")
        print("When ready, reply with: “Implement lightweight MCP server wrapper”")
    elif args.cmd == "advisor":
        print("=== Gravity Safety Advisor (Mac Studio canonical) ===")
        print("This layer only advises. It never calls deploy.sh.")
        print("Always:")
        print("  1. Review latest receipts/ (governance-cycle-*.md and work-pack-*.md)")
        print("  2. Run python tools/civforge_cli.py recommend or gate as needed")
        print("  3. Make literal changes ONLY in the separate gravity-mosaic repo")
        print("  4. Then (and only then) run: ./tools/deploy-gravity-mosaic/deploy.sh")
        print("Separation is strictly enforced. CivForge governs; deploy.sh executes under receipts.")
    else:
        p.print_help()

if __name__ == "__main__":
    main()
