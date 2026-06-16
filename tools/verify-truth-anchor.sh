#!/bin/bash
# Verify truth-plane anchors: git HEAD, pytest count, registry coherence, block closures.
#
# Default: read-only verify (fails if anchor.head != git HEAD — no silent registry writes).
# After a land commit, update registry explicitly: bash tools/verify-truth-anchor.sh --sync
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SYNC_ANCHOR=0
for arg in "$@"; do
  case "$arg" in
    --sync) SYNC_ANCHOR=1 ;;
    -h|--help)
      echo "Usage: bash tools/verify-truth-anchor.sh [--sync]"
      echo "  default  Fail if registry anchor.head != git HEAD (no file mutation)"
      echo "  --sync   Write anchor.head to current git HEAD after checks pass"
      exit 0
      ;;
  esac
done

echo "=== CivForge verify-truth-anchor ==="
echo "git HEAD: $(git rev-parse --short HEAD)"
if [[ "$SYNC_ANCHOR" == "1" ]]; then
  echo "mode: --sync (will update config/work_pack_registry.yaml anchor.head on success)"
else
  echo "mode: verify-only (use --sync after land commit to update registry)"
fi

export SYNC_ANCHOR
export ROOT_OVERRIDE="$ROOT"
python3 <<'PY'
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("ROOT_OVERRIDE", ".")).resolve()
registry_path = ROOT / "config" / "work_pack_registry.yaml"
text = registry_path.read_text(encoding="utf-8")

head_match = re.search(r"^  head:\s*(\S+)\s*$", text, re.M)
pytest_match = re.search(r"^  pytest_total:\s*(\d+)\s*$", text, re.M)
if not head_match or not pytest_match:
    sys.exit("registry missing anchor.head or anchor.pytest_total")

registry_head = head_match.group(1)
expected_pytest = int(pytest_match.group(1))
live_head = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, cwd=ROOT).strip()
sync_anchor = os.environ.get("SYNC_ANCHOR", "0") == "1"


def parent_short_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD~1"],
            text=True,
            cwd=ROOT,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def anchor_head_ok() -> bool:
    if registry_head == live_head:
        return True
    parent = parent_short_head()
    # Allow anchor sync follow-up: registry points at land commit (HEAD~1).
    return bool(parent) and registry_head == parent


errors = []

if not anchor_head_ok():
    msg = f"registry anchor.head {registry_head} != git HEAD {live_head}"
    if sync_anchor:
        text = text.replace(f"  head: {registry_head}", f"  head: {live_head}", 1)
        registry_path.write_text(text)
        print(f"SYNC: updated registry anchor.head → {live_head}")
        registry_head = live_head
    else:
        parent = parent_short_head()
        hint = f" (run: bash tools/verify-truth-anchor.sh --sync)"
        if parent:
            hint += f"; or land commit + anchor sync (HEAD~1={parent})"
        errors.append(msg + hint)

pytest_run = subprocess.run(
    ["python3", "-m", "pytest", "tests/", "-q"],
    capture_output=True,
    text=True,
    cwd=ROOT,
)
print(pytest_run.stdout.strip().splitlines()[-1] if pytest_run.stdout.strip() else pytest_run.stdout)
if pytest_run.returncode != 0:
    errors.append("pytest failed")
    if pytest_run.stdout:
        for line in pytest_run.stdout.strip().splitlines()[-5:]:
            print(line)

m = re.search(r"(\d+) passed", pytest_run.stdout)
if not m:
    errors.append("pytest did not report pass count")
else:
    actual = int(m.group(1))
    if actual != expected_pytest:
        errors.append(f"registry pytest_total {expected_pytest} != actual {actual}")

CLOSED_WPS = (
    "WP-GROK-WONDER-PLACE-001",
    "WP-GROK-CULTURAL-VICTORY-001",
    "WP-GROK-POLICY-BRANCH-001",
    "WP-GROK-COMPETITION-DEPTH-001",
    "WP-GROK-PLAYER-AGENT-001",
)
for wp in CLOSED_WPS:
    if f"{wp}:" not in text:
        errors.append(f"missing {wp} in registry")
    elif f"\n    lifecycle: closed" not in text.split(f"{wp}:")[1].split("\n\n", 1)[0]:
        errors.append(f"{wp} not closed in registry")

for block_id in ("block_a", "block_b", "block_c", "block_d"):
    marker = f"  {block_id}:"
    if marker not in text:
        errors.append(f"missing blocks.{block_id} in registry")
    elif f"\n    status: closed" not in text.split(marker)[1].split("\n\n", 1)[0]:
        errors.append(f"blocks.{block_id} not closed in registry")

closure_docs = (
    "receipts/BLOCK-A-CLOSURE-20260616.md",
    "receipts/BLOCK-B-CLOSURE-20260616.md",
    "receipts/BLOCK-C-CLOSURE-20260616.md",
    "receipts/BLOCK-D-CLOSURE-20260616.md",
    "receipts/cursor-execution-wp-grok-block-a-20260616.md",
    "receipts/cursor-execution-wp-grok-block-c-20260616.md",
    "receipts/cursor-execution-wp-grok-block-d-20260616.md",
    "receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md",
)
for rel in closure_docs:
    if not (ROOT / rel).is_file():
        errors.append(f"missing {rel}")

for doc in (
    "docs/TRUTH_ORDER.md",
    "docs/WORK_PACK_LIFECYCLE.md",
    "docs/AGENT_CLAIMS_POLICY.md",
):
    if not (ROOT / doc).is_file():
        errors.append(f"missing {doc}")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print(f"PASS: registry, docs, block closures, pytest count aligned with HEAD {live_head}")
PY

echo "=== verify-truth-anchor OK ==="
