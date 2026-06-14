#!/bin/bash
# CivForge Auth Prototype Start Helper
#
# "Enable this function" — brings up the separate dawsos-auth-prototype
# on port 8081 so CivForge can obtain tokens and use protected governance endpoints.
#
# The actual server code lives in the separate repo.
# This script only cds there and launches (or prints the exact command).

set -e

CANONICAL_DIR="/Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype"

echo "=== CivForge — Enable dawsos-auth-prototype (auth function) ==="
echo "Canonical separate location: $CANONICAL_DIR"
echo ""

if [ ! -d "$CANONICAL_DIR" ]; then
    echo "ERROR: No clone found at $CANONICAL_DIR"
    echo "Run first: ./tools/auth-prototype/clone.sh"
    exit 1
fi

cd "$CANONICAL_DIR"

echo "1. Literal verification before starting..."
echo "   pwd: $(pwd)"
ls -1 backend/ core/ tools/ tests/ | cat
wc -l backend/auth_api.py
grep -c "title=\"dawsos-auth-prototype\"\|separate from CivForge" backend/auth_api.py || true

echo ""
echo "2. Ensuring Python dependencies (fastapi, uvicorn, pyjwt, pydantic)..."
python3 -m pip install fastapi uvicorn pyjwt pydantic requests --quiet 2>&1 | tail -2 || true

echo ""
echo "3. Starting the auth prototype on port 8081..."
echo "   (This will block. Use Ctrl-C to stop, or run in background / another terminal.)"
echo ""
echo "   Alternative one-liner you can copy:"
echo "   cd $CANONICAL_DIR && python3 -m uvicorn backend.auth_api:app --reload --host 0.0.0.0 --port 8081"
echo ""

# Prefer the prototype's own runner if it exists and is executable
if [ -x "./run_prototype.sh" ]; then
    echo "Using prototype's run_prototype.sh ..."
    exec ./run_prototype.sh
else
    exec python3 -m uvicorn backend.auth_api:app --reload --host 0.0.0.0 --port 8081
fi
