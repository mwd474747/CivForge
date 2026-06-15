#!/bin/bash
# Build and smoke-test CivForge kernel container
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== CivForge Docker smoke ==="
docker compose build civforge-kernel
docker compose up -d civforge-kernel

for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1:8080/state >/tmp/civforge-docker-state.json 2>/dev/null; then
    python3 -c "
import json
d=json.load(open('/tmp/civforge-docker-state.json'))
assert len(d.get('map_tiles',[]))==25
print('OK turn', d['current_turn'], 'map', len(d['map_tiles']))
"
    echo "=== Docker smoke PASSED ==="
    exit 0
  fi
  sleep 2
done

echo "=== Docker smoke FAILED (no /state) ==="
docker compose logs civforge-kernel | tail -30
exit 1
