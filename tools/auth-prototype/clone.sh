#!/bin/bash
# CivForge Auth Prototype Clone Helper
#
# Ensures a local clone of the SEPARATE dawsos-auth-prototype exists
# at the canonical location.
#
# This is the "create the local clone" command.
#
# Rules followed:
# - Strict separation (auth prototype is never mixed into CivForge)
# - Literal verification before / during operations (ls, wc, grep)
# - Only clones or pulls; never mutates source inside the prototype beyond git pull
# - Receipts should be logged in CivForge for governance actions around this

set -e

CANONICAL_DIR="/Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype"
REPO_URL="https://github.com/mwd474747/dawsos-auth-prototype.git"

echo "=== CivForge Auth Prototype Clone / Update ==="
echo "Target (separate project): $CANONICAL_DIR"
echo ""

# Literal pre-check
echo "1. Pre-verification (literal disk reads)..."
echo "   Current CivForge dir: $(pwd)"
ls -ld "$CANONICAL_DIR" 2>/dev/null || echo "   (target dir does not exist yet — will clone)"

echo ""
echo "2. Checking for existing clone..."

if [ -d "$CANONICAL_DIR/.git" ]; then
    echo "   Existing clone found. Updating + verifying..."
    cd "$CANONICAL_DIR"
    git status --short
    git pull --ff-only || echo "   (pull may have been a no-op or had conflicts — review manually)"

    echo ""
    echo "   Literal verification of clone:"
    wc -l backend/auth_api.py core/identity_patterns.py tools/auth_cli.py tests/test_auth_flows.py docs/INTEROPERABILITY.md README.md AGENTS.md 2>/dev/null || true

    echo ""
    echo "   Golden feature anchors (must be present):"
    grep -c "dawsos-auth-prototype\|Isolated, testable auth\|register/device\|/verify\|separate from CivForge" backend/auth_api.py docs/INTEROPERABILITY.md README.md 2>/dev/null || true

    echo ""
    echo "   Cross-contamination check (should be near zero for critical terms):"
    grep -E "CivForge|gravity-mosaic|godot-mvp" . --include="*.py" --include="*.md" | grep -v "INTEROPERABILITY\|dawsos_auth_client\|patterns" | wc -l || echo "0"

    echo ""
    echo "✅ Local clone already present and updated at: $CANONICAL_DIR"
else
    echo "   No clone at canonical location. Performing git clone..."
    PARENT_DIR=$(dirname "$CANONICAL_DIR")
    mkdir -p "$PARENT_DIR"
    cd "$PARENT_DIR"

    git clone "$REPO_URL" "$(basename "$CANONICAL_DIR")"

    echo ""
    echo "   Post-clone literal verification:"
    cd "$CANONICAL_DIR"
    ls -la
    wc -l backend/auth_api.py core/identity_patterns.py tools/auth_cli.py
    git log --oneline -3

    echo ""
    echo "✅ Fresh clone created at: $CANONICAL_DIR"
fi

echo ""
echo "=== Next steps to ENABLE the auth function ==="
echo "   cd /Users/michaeldawson/CivForge"
echo "   ./tools/auth-prototype/start.sh"
echo ""
echo "   Or manually:"
echo "   cd $CANONICAL_DIR"
echo "   python3 -m pip install fastapi uvicorn pyjwt pydantic --quiet"
echo "   python3 -m uvicorn backend.auth_api:app --reload --host 0.0.0.0 --port 8081"
echo ""
echo "After the server is running on 8081, use:"
echo "   python tools/dawsos_auth_client.py register-device ..."
echo "   python tools/dawsos_auth_client.py token <id> govern"
echo "   Then call CivForge /governance/protected_advance with the Bearer token."
echo ""
echo "See ./README.md in this directory and the main HANDOFF_CONTEXT.md for full details."