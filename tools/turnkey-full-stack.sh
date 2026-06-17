#!/bin/bash
# CivForge + dawsos-auth turnkey — one command for local/OpenClaw operator lanes.
#
# Starts :8081 identity + :8080 kernel, runs read-only validation + OpenClaw ops probe.
# Optional: export CIVFORGE_REQUIRE_AUTH=1 after sourcing a govern JWT (see auth bootstrap).
#
# Usage:
#   bash tools/turnkey-full-stack.sh              # start services + validate
#   bash tools/turnkey-full-stack.sh --auth-on    # also issue JWT + enable require_auth on kernel restart
#   bash tools/turnkey-full-stack.sh --no-start   # validate only (services must already be live)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

AUTH_ON=false
NO_START=false
for arg in "$@"; do
  case "$arg" in
    --auth-on) AUTH_ON=true ;;
    --no-start) NO_START=true ;;
  esac
done

echo "=== CivForge Full Stack Turnkey ==="

if ! $NO_START; then
  echo "1. dawsos-auth :8081..."
  bash tools/start-auth-8081.sh

  echo "2. CivForge kernel :8080..."
  bash tools/start-kernel-8080.sh

  if $AUTH_ON; then
    echo "3. Bootstrap govern JWT..."
    python3 tools/dawsos_auth_identity_client.py register-device civforge-player pk-turnkey >/dev/null 2>&1 || true
    TOKEN="$(python3 tools/dawsos_auth_identity_client.py token civforge-player govern | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
    export CIVFORGE_AUTH_TOKEN="$TOKEN"
    export CIVFORGE_REQUIRE_AUTH=1
    echo "   CIVFORGE_AUTH_TOKEN set (15 min TTL)"
    echo "   Re-export before CLI/MCP if shell exits:"
    echo "     export CIVFORGE_AUTH_TOKEN=\"$TOKEN\""
    echo "     export CIVFORGE_REQUIRE_AUTH=1"
    echo "   Dashboard: paste same JWT in Auth panel at http://127.0.0.1:8080/dashboard"
  fi
else
  echo "1–2. Skipping service start (--no-start)"
fi

echo "4. validate-game (read-only)..."
bash tools/validate-game.sh --read-only

echo "5. OpenClaw ops probe..."
bash tools/turnkey-openclaw-ops.sh --once

echo "=== Full stack turnkey PASSED ==="
echo "Dashboard: http://127.0.0.1:8080/dashboard"
echo "Auth health: curl -s http://127.0.0.1:8081/health | python3 -m json.tool"
echo "OpenClaw wt: docs/OPENCLAW_OPS_PACKET_V1.md (escalation when promotion needed)"
