#!/bin/bash
set -e
echo '🚀 CivForge Governance Workspace Setup (realigned — FastAPI + core Python, no Godot MVP)'

echo "This sets up the local agentic governance layer for safely driving work on the"
echo "SEPARATE project: /Users/michaeldawson/gravity-mosaic-knowledge-graph"
echo "All real changes to gravity-mosaic MUST go through tools/deploy-gravity-mosaic/deploy.sh"
echo "(strict literal full-disk verification, no meta, receipts, etc.)."
echo ""

# Python env
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 required."
    exit 1
fi

echo "=== Installing backend deps (FastAPI workspace) ==="
cd backend
python3 -m pip install --quiet fastapi uvicorn pydantic requests
echo "Deps ready."

echo ""
echo "=== Starting the governance backend (uvicorn) ==="
echo "Run this in a separate terminal (or background it):"
echo "  cd /Users/michaeldawson/CivForge/backend"
echo "  python3 -m uvicorn sim_api:app --reload --host 0.0.0.0 --port 8080"
echo ""
echo "Then test exactly as in the original Codespaces paste:"
echo "  curl http://localhost:8080/state"
echo "  curl -X POST http://localhost:8080/found_city -H 'Content-Type: application/json' -d '{\"city_name\":\"Gravity research thread\",\"investment\":4}'"
echo ""

# Optional: start in background for this session (user can kill later)
if [ "$1" = "--start-backend" ]; then
    echo "Starting backend in background on port 8080..."
    nohup python3 -m uvicorn sim_api:app --host 0.0.0.0 --port 8080 > /tmp/civforge_backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID (log: /tmp/civforge_backend.log)"
    sleep 2
    curl -s http://localhost:8080/state | head -c 400 || echo "Backend may still be starting..."
    echo ""
fi

cd ..

echo "=== CLI + Headless Observer ready ==="
python3 -m pip install --quiet requests >/dev/null || true
chmod +x tools/civforge_cli.py bridge/headless_observer.py 2>/dev/null || true

echo ""
echo "Key active components (Godot MVP archived in _archive/):"
ls -d backend/ bridge/ core/ governance/ planning/ receipts/ skills/ tools/ tools/deploy-gravity-mosaic/ 2>/dev/null

echo ""
echo "✅ CivForge realigned and ready."
echo "Next typical flow (terminal-driven):"
echo "  python tools/civforge_cli.py status"
echo "  python tools/civforge_cli.py advance"
echo "  python tools/civforge_cli.py recommend"
echo "  ./tools/deploy-gravity-mosaic/deploy.sh   # (only after literal changes + gate on the separate gravity project)"
echo ""
echo "See README.md for the full realigned intent."
