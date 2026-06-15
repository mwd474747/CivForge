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
  python tools/civforge_cli.py auth status
  python tools/civforge_cli.py auth start
  python tools/civforge_cli.py auth register-device my-device pk123
  python tools/civforge_cli.py auth token <id> govern

All real changes to the *separate* gravity-mosaic project still require running
the verified deploy.sh manually after governance receipts.
Auth prototype (separate) is enabled via tools/auth-prototype/{clone.sh,start.sh} and the thin client.
"""

import argparse
import os
import sys
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
    sub.add_parser("mcp-serve", help="Start stdio MCP tool server (forwards to kernel :8080)")
    sub.add_parser("advisor", help="Safe gravity advisor (proposal-only, never auto-executes deploy.sh)")
    sub.add_parser("nexus-poll", help="Poll dawsos-nexus (8082) for pending commands and surface as governed proposals (thin bridge, commands propose not execute). Supports --once/--loop.")

    # Auth/control: Nexus 8082 machine satellite (telemetry + proposals, governance_kernel). Identity long-term auth-prototype 8081. No "replaces" per boundary contract.
    auth_p = sub.add_parser("auth", help="Auth prototype commands (separate identity plane :8081). Nexus 8082 is machine satellite only (telemetry + proposals). See SEPARATION planes.")
    auth_p.add_argument("action", nargs="?", default="status", choices=["status", "start", "register-device", "token", "verify"])
    auth_p.add_argument("arg1", nargs="?", default=None)
    auth_p.add_argument("arg2", nargs="?", default=None)
    auth_p.add_argument("arg3", nargs="?", default=None)

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
    elif args.cmd == "mcp-serve":
        import subprocess
        mcp = Path(__file__).parent / "mcp_server.py"
        print(f"Starting CivForge MCP server (stdio) → {os.environ.get('CIVFORGE_KERNEL_URL', 'http://127.0.0.1:8080')}")
        os.execv(sys.executable, [sys.executable, str(mcp)])
    elif args.cmd == "mcp-stub":
        print("MCP is implemented: use `python3 tools/civforge_cli.py mcp-serve` (stdio JSON-RPC).")
        print("Tools: civforge_status, civforge_advance_turn, civforge_found_city, civforge_negotiate, civforge_negotiate_respond, civforge_what_if, civforge_governance_propose, civforge_governance_gate")
    elif args.cmd == "advisor":
        print("=== Gravity Safety Advisor (Mac Studio canonical) ===")
        print("This layer only advises. It never calls deploy.sh.")
        print("Always:")
        print("  1. Review latest receipts/ (governance-cycle-*.md and work-pack-*.md)")
        print("  2. Run python tools/civforge_cli.py recommend or gate as needed")
        print("  3. Make literal changes ONLY in the separate gravity-mosaic repo")
        print("  4. Then (and only then) run: ./tools/deploy-gravity-mosaic/deploy.sh")
        print("Separation is strictly enforced. CivForge governs; deploy.sh executes under receipts.")

    elif args.cmd == "nexus-poll":
        poller_script = str(ROOT / "tools" / "nexus_command_poller.py")
        print("=== dawsos-nexus Command Poller (thin bridge) ===")
        print("Commands from nexus are surfaced as 8080 proposals (never auto-executed).")
        print("Run directly with --loop for continuous: python tools/nexus_command_poller.py --loop")
        subprocess.run(["python3", poller_script, "--once"])

    elif args.cmd == "auth":
        # Delegate to the thin client for the separate dawsos-auth-prototype (enables protected governance)
        auth_script = str(ROOT / "tools" / "dawsos_auth_client.py")
        if args.action in ("register-device", "token", "verify"):
            cmd = ["python3", auth_script, args.action]
            if args.arg1:
                cmd.append(args.arg1)
            if args.arg2:
                cmd.append(args.arg2)
            if args.arg3:
                cmd.append(args.arg3)
            subprocess.run(cmd)
        elif args.action == "start":
            print("=== Enabling auth function (separate prototype on :8081) ===")
            print("Recommended: run the dedicated bridge script for literal verification + clone safety")
            print("  ./tools/auth-prototype/start.sh")
            print("")
            print("Direct (if you already have the clone):")
            print("  cd /Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype")
            print("  python3 -m uvicorn backend.auth_api:app --reload --host 0.0.0.0 --port 8081")
            print("")
            print("After it is running, use this CLI or the client directly to get tokens.")
            print("Example protected CivForge call requires a 'govern' scope token from the prototype.")
        elif args.action == "status":
            print("Auth prototype (separate dawsos-auth-prototype) status:")
            print("  Canonical location: /Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype")
            print("  Expected port: 8081")
            print("  GitHub: https://github.com/mwd474747/dawsos-auth-prototype")
            print("")
            print("To enable:")
            print("  ./tools/auth-prototype/clone.sh")
            print("  ./tools/auth-prototype/start.sh   # (in another terminal or background)")
            print("")
            print("Then obtain tokens and call CivForge /governance/protected_advance with Authorization: Bearer ...")
            print("Use: python tools/civforge_cli.py auth register-device <id> [pk]")
            print("     python tools/civforge_cli.py auth token <identity_id> govern")
            print("See tools/auth-prototype/README.md and HANDOFF_CONTEXT.md for full steps.")
        else:
            print("Unknown auth action. Try: status, start, register-device, token, verify")
    else:
        p.print_help()

if __name__ == "__main__":
    main()
