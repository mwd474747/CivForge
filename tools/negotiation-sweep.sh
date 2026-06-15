#!/bin/bash
# Resolve pending negotiations via API (optional backlog cleanup).
# Usage: bash tools/negotiation-sweep.sh [--accept|--decline] [--max N]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="accept"
MAX=10
if [[ "${1:-}" == "--decline" ]]; then MODE="decline"; shift; fi
if [[ "${1:-}" == "--accept" ]]; then MODE="accept"; shift; fi
if [[ "${1:-}" == "--max" ]]; then MAX="${2:-10}"; fi

ACCEPT="true"
[[ "$MODE" == "decline" ]] && ACCEPT="false"

python3 <<PY
import json, urllib.request

KERNEL = "http://127.0.0.1:8080"
accept = $ACCEPT == "true"

def get(path):
    with urllib.request.urlopen(f"{KERNEL}{path}", timeout=15) as r:
        return json.loads(r.read())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{KERNEL}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

state = get("/state")
pending = [n for n in state.get("negotiations", []) if n.get("status") == "pending"]
resolved = 0
for neg in pending[:$MAX]:
    post("/game/negotiate/respond", {"negotiation_id": neg["id"], "accept": accept})
    resolved += 1
print(f"Resolved {resolved} negotiations ({'accept' if accept else 'decline'})")
PY
