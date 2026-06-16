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
Identity plane: sibling repo dawsos-auth-prototype (:8081) via tools/dawsos_auth_client.py.
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


def cmd_snapshot():
    s = _get("/state")
    mech = _get("/game/mechanics/status")
    idx_script = ROOT / "tools" / "civforge_receipt_index.py"
    idx = subprocess.run(
        [sys.executable, str(idx_script)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    receipt_index = {}
    if idx.returncode == 0 and idx.stdout.strip():
        try:
            receipt_index = json.loads(idx.stdout)
        except json.JSONDecodeError:
            receipt_index = {"raw": idx.stdout[:500]}
    print(json.dumps({
        "turn": s.get("current_turn"),
        "session_phase": s.get("session_phase"),
        "fun_score": s.get("fun_score"),
        "victory_hud": s.get("victory_hud"),
        "mechanics_status": mech,
        "receipt_index": receipt_index,
    }, indent=2))


def cmd_status():
    s = _get("/state")
    print(json.dumps({
        "turn": s["current_turn"],
        "fun_score": s["fun_score"],
        "session_phase": s.get("session_phase"),
        "player": s["player"],
        "mechanics_proposals": s.get("mechanics_proposals"),
        "mechanics_overrides": s.get("mechanics_overrides"),
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

    sub.add_parser("snapshot", help="State + mechanics status + receipt index")
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

    if args.cmd == "snapshot":
        cmd_snapshot()
    elif args.cmd == "status":
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
        print("Tools (16): civforge_status, civforge_advance_turn, civforge_reset_game, civforge_found_city,")
        print("  civforge_negotiate, civforge_negotiate_respond, civforge_what_if,")
        print("  civforge_governance_propose, civforge_governance_gate,")
        print("  civforge_select_district, civforge_unlock_policy, civforge_claim_tile,")
        print("  civforge_propose_mechanics, civforge_gate_mechanics, civforge_apply_mechanics, civforge_list_mechanics_proposals")
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
            print("=== Enabling auth (separate dawsos-auth-prototype on :8081) ===")
            print("  cd ~/Documents/GitHub/dawsos-auth-prototype")
            print("  python3 -m uvicorn backend.auth_api:app --reload --host 127.0.0.1 --port 8081")
            print("")
            print("Then: python3 tools/civforge_cli.py auth register-device <id> [pk]")
            print("      python3 tools/civforge_cli.py auth token <identity_id> govern")
        elif args.action == "status":
            print("Auth (separate dawsos-auth-prototype):")
            print("  Repo: https://github.com/mwd474747/dawsos-auth-prototype")
            print("  Path: ~/Documents/GitHub/dawsos-auth-prototype")
            print("  Port: 8081")
            print("  Client: tools/dawsos_auth_client.py")
            print("  See SEPARATION.md and docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md")
        else:
            print("Unknown auth action. Try: status, start, register-device, token, verify")
    else:
        p.print_help()

if __name__ == "__main__":
    main()
