#!/bin/bash
# Persistent start helper for the CivForge governance kernel on 8080.
# Run this directly in your own terminal (not through the agent harness background tasks).
# It uses nohup so the server survives agent sessions and background task timeouts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

LOG_FILE="/tmp/civforge-8080.log"
PID_FILE="/tmp/civforge-8080.pid"
SCREEN_SESSION="civforge-kernel-8080"

echo "=== CivForge Kernel Start (8080) ==="

# Stop any previous instance using PID file (safer than broad pkill -f in this context)
if [[ -f "$PID_FILE" ]]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null || true)
  if [[ -n "${OLD_PID}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Stopping previous instance (PID $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

# Fallback: try a narrow kill for uvicorn on this port only (avoid self-match issues)
pkill -f "uvicorn.*8080" 2>/dev/null || true
screen -S "$SCREEN_SESSION" -X quit >/dev/null 2>&1 || true
sleep 1

if command -v screen >/dev/null 2>&1; then
  echo "Starting uvicorn (screen, detached)..."
  screen -dmS "$SCREEN_SESSION" bash -lc "cd '$ROOT_DIR'; python3 -m uvicorn backend.sim_api:app --host 0.0.0.0 --port 8080 > '$LOG_FILE' 2>&1 & echo \$! > '$PID_FILE'; wait \$(cat '$PID_FILE')"
  sleep 1
  SRV_PID="$(cat "$PID_FILE")"
else
  echo "Starting uvicorn (nohup, detached)..."
  nohup python3 -m uvicorn backend.sim_api:app --host 0.0.0.0 --port 8080 > "$LOG_FILE" 2>&1 &
  SRV_PID=$!
  echo "$SRV_PID" > "$PID_FILE"
fi

echo "PID: $SRV_PID (saved to $PID_FILE)"
echo "Log: $LOG_FILE"

sleep 4

echo "=== Health check ==="
if curl -s --max-time 5 http://localhost:8080/state > /tmp/.civforge-state-check.json 2>/dev/null; then
  python3 -c '
import json, sys
try:
  d = json.load(open("/tmp/.civforge-state-check.json"))
  print("✅ LIVE")
  print("  current_turn:", d.get("current_turn") or d.get("turn"))
  print("  fun_score:", d.get("fun_score"))
  print("  status:", d.get("status"))
except Exception as e:
  print("Response received but parse issue:", e)
  print(open("/tmp/.civforge-state-check.json").read()[:300])
'
else
  echo "No response yet. Tail the log for details:"
  echo "  tail -n 30 $LOG_FILE"
fi

echo ""
echo "Useful commands while it is running:"
echo "  python3 tools/civforge_cli.py status"
echo "  python3 tools/civforge_cli.py propose-deploy"
echo "  python3 tools/civforge_cli.py advance"
echo "  curl -s http://localhost:8080/state | python3 -m json.tool | head -30"
echo ""
echo "To stop: kill \$(cat $PID_FILE)   or   pkill -f 'uvicorn.*sim_api'"
echo "The server will keep running in the background until explicitly stopped."
