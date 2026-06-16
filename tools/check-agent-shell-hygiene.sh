#!/bin/bash
# Detect stale Cursor agent sandbox wrapper shells (orphaned zsh parents).
#
# Usage:
#   bash tools/check-agent-shell-hygiene.sh           # report only, exit 1 if stale found
#   bash tools/check-agent-shell-hygiene.sh --kill     # terminate stale wrappers
#   MINUTES=60 bash tools/check-agent-shell-hygiene.sh # custom idle threshold (default 30)
set -euo pipefail

KILL=false
MINUTES="${MINUTES:-30}"

for arg in "$@"; do
  case "$arg" in
    --kill) KILL=true ;;
    -h|--help)
      echo "Usage: bash tools/check-agent-shell-hygiene.sh [--kill]"
      echo "  Finds Cursor sandbox zsh wrappers (dump_zsh_state) idle longer than MINUTES."
      exit 0
      ;;
  esac
done

echo "=== CivForge check-agent-shell-hygiene (stale > ${MINUTES}m) ==="

export KILL_ORPHANS=$([[ "$KILL" == true ]] && echo 1 || echo 0)
export MINUTES
python3 <<'PY'
import os
import subprocess
import sys

kill = os.environ.get("KILL_ORPHANS", "0") == "1"
minutes = int(os.environ.get("MINUTES", "30"))
pattern = "dump_zsh_state"

ps = subprocess.run(["ps", "-eo", "pid=,etime=,command="], capture_output=True, text=True, check=True)
stale = []

def etime_minutes(raw: str) -> float:
    raw = raw.strip()
    if "-" in raw:
        days, rest = raw.split("-", 1)
        day_m = int(days) * 24 * 60
    else:
        day_m = 0
        rest = raw
    parts = rest.split(":")
    if len(parts) == 3:
        h, m, s = (int(float(x)) for x in parts)
        return day_m + h * 60 + m + s / 60.0
    if len(parts) == 2:
        m, s = (int(float(x)) for x in parts)
        return day_m + m + s / 60.0
    return day_m + float(parts[0])

for line in ps.stdout.splitlines():
    line = line.strip()
    if not line or pattern not in line:
        continue
    pid_s, etime, cmd = line.split(None, 2)
    pid = int(pid_s)
    mins = etime_minutes(etime)
    if mins < minutes:
        continue
    stale.append((pid, etime.strip(), cmd[:120]))

if not stale:
    print("PASS: no stale Cursor agent wrapper shells")
    sys.exit(0)

print(f"WARN: {len(stale)} stale Cursor agent wrapper shell(s):")
for pid, etime, cmd in stale:
    print(f"  pid={pid} elapsed={etime} cmd={cmd}...")

if kill:
    for pid, _, _ in stale:
        subprocess.run(["kill", str(pid)], check=False)
    print(f"KILLED: {len(stale)} process(es)")
    sys.exit(0)

print("Hint: bash tools/check-agent-shell-hygiene.sh --kill")
sys.exit(1)
PY
