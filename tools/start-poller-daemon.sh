#!/bin/bash
# Detached Nexus command poller for civforge-kernel (thin bridge)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

KEY_FILE="${HOME}/.openclaw/runtime/nexus-satellite-api-keys.json"
LOG="/tmp/civforge-poller.log"
PID_FILE="/tmp/civforge-poller.pid"
SCREEN_SESSION="civforge-poller"

if [[ ! -f "$KEY_FILE" ]]; then
  echo "Missing $KEY_FILE — provision NEXUS_API_KEY first"
  exit 1
fi

export NEXUS_API_KEY
NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$KEY_FILE'))['civforge-kernel']['apiKey'])")"
export NEXUS_URL="${NEXUS_URL:-http://127.0.0.1:8082}"

if [[ -f "$PID_FILE" ]]; then
  OLD=$(cat "$PID_FILE" 2>/dev/null || true)
  if [[ -n "$OLD" ]] && kill -0 "$OLD" 2>/dev/null; then
    kill "$OLD" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

nohup python3 tools/nexus_command_poller.py --loop --interval 30 >"$LOG" 2>&1 &
echo $! >"$PID_FILE"
sleep 3

if ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  if command -v screen >/dev/null 2>&1; then
    screen -S "$SCREEN_SESSION" -X quit >/dev/null 2>&1 || true
    rm -f "$PID_FILE"
    screen -dmS "$SCREEN_SESSION" bash -lc "cd '$ROOT'; python3 -u tools/nexus_command_poller.py --loop --interval 30 >'$LOG' 2>&1 & echo \$! > '$PID_FILE'; wait \$(cat '$PID_FILE')"
    sleep 3
  fi
fi

if [[ ! -f "$PID_FILE" ]] || ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Poller failed to stay alive; see $LOG"
  tail -n 20 "$LOG" || true
  exit 1
fi

python3 tools/civforge_poller_posture.py >/tmp/civforge-poller-posture-start.json || true
echo "Poller PID $(cat "$PID_FILE") log $LOG"
tail -n 5 "$LOG" || true
