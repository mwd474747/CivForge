#!/bin/bash
# Detached Nexus command poller for civforge-kernel (thin bridge)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

KEY_FILE="${HOME}/.openclaw/runtime/nexus-satellite-api-keys.json"
LOG="/tmp/civforge-poller.log"
PID_FILE="/tmp/civforge-poller.pid"

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
echo "Poller PID $(cat "$PID_FILE") log $LOG"
sleep 2
tail -n 3 "$LOG" || true
