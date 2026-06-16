#!/bin/bash
# Verify truth-plane anchors: git HEAD, pytest count, registry coherence, Block A receipts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== CivForge verify-truth-anchor ==="

HEAD="$(git rev-parse --short HEAD)"
echo "git HEAD: $HEAD"

PYTEST_OUT="$(python3 -m pytest tests/ -q 2>&1)"
echo "$PYTEST_OUT" | tail -3

python3 <<PY
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("$ROOT")
registry_path = ROOT / "config" / "work_pack_registry.yaml"
text = registry_path.read_text(encoding="utf-8")

head_match = re.search(r"^  head:\s*(\S+)\s*$", text, re.M)
pytest_match = re.search(r"^  pytest_total:\s*(\d+)\s*$", text, re.M)
if not head_match or not pytest_match:
    sys.exit("registry missing anchor.head or anchor.pytest_total")

registry_head = head_match.group(1)
expected_pytest = int(pytest_match.group(1))
live_head = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()

errors = []
if registry_head != live_head:
    print(f"NOTE: update config/work_pack_registry.yaml anchor.head to {live_head} after this commit")

pytest_run = subprocess.run(
    ["python3", "-m", "pytest", "tests/", "-q"],
    capture_output=True,
    text=True,
    cwd=ROOT,
)
m = re.search(r"(\d+) passed", pytest_run.stdout)
if not m:
    errors.append("pytest did not report pass count")
else:
    actual = int(m.group(1))
    if actual != expected_pytest:
        errors.append(f"registry pytest_total {expected_pytest} != actual {actual}")

for wp in (
    "WP-GROK-WONDER-PLACE-001",
    "WP-GROK-CULTURAL-VICTORY-001",
    "WP-GROK-POLICY-BRANCH-001",
):
    if f"{wp}:" not in text:
        errors.append(f"missing {wp} in registry")
    elif f"\n    lifecycle: closed" not in text.split(f"{wp}:")[1].split("\n\n", 1)[0]:
        errors.append(f"{wp} not closed in registry")

closure = ROOT / "receipts" / "BLOCK-A-CLOSURE-20260616.md"
exec_receipt = ROOT / "receipts" / "cursor-execution-wp-grok-block-a-20260616.md"
for path in (closure, exec_receipt):
    if not path.is_file():
        errors.append(f"missing {path.relative_to(ROOT)}")

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

print("PASS: registry, docs, Block A closure, pytest count aligned with HEAD", live_head)
PY

echo "=== verify-truth-anchor OK ==="
