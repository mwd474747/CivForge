#!/bin/bash
# Start dawsos-auth identity service on :8081 (sister repo).
# CivForge kernel verifies JWTs via DAWSOS_AUTH_BASE (default http://127.0.0.1:8081).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
AUTH_REPO="${DAWSOS_AUTH_REPO:-$HOME/Documents/GitHub/dawsos-auth}"

LOG_FILE="/tmp/dawsos-auth-8081.log"
PID_FILE="/tmp/dawsos-auth-8081.pid"

if [[ ! -d "$AUTH_REPO/backend" ]]; then
  echo "Auth repo not found at: $AUTH_REPO"
  echo "Set DAWSOS_AUTH_REPO to the dawsos-auth checkout."
  exit 1
fi

echo "=== dawsos-auth Start (8081) ==="
echo "Repo: $AUTH_REPO"

if [[ -f "$PID_FILE" ]]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null || true)
  if [[ -n "${OLD_PID}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Stopping previous instance (PID $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

pkill -f "uvicorn.*auth_api:app.*8081" 2>/dev/null || true
sleep 1

cd "$AUTH_REPO"
nohup python3 -m uvicorn backend.auth_api:app --host 127.0.0.1 --port 8081 > "$LOG_FILE" 2>&1 &
SRV_PID=$!
echo "$SRV_PID" > "$PID_FILE"

echo "PID: $SRV_PID (saved to $PID_FILE)"
echo "Log: $LOG_FILE"
sleep 3

if curl -s --max-time 5 http://127.0.0.1:8081/health | python3 -c 'import json,sys; d=json.load(sys.stdin); print("✅ LIVE", d.get("service"), d.get("version"))'; then
  :
else
  echo "No response yet. Tail: tail -n 30 $LOG_FILE"
fi

echo ""
echo "Issue a govern token for CivForge:"
echo "  cd '$ROOT_DIR'"
echo "  python3 tools/dawsos_auth_identity_client.py register-device civforge-player"
echo "  python3 tools/dawsos_auth_identity_client.py token civforge-player govern"
echo ""
echo "Enable kernel auth:"
echo "  export CIVFORGE_REQUIRE_AUTH=1"
echo "  export CIVFORGE_AUTH_TOKEN=\"<jwt from token command>\""
