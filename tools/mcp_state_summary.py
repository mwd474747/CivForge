#!/usr/bin/env python3
"""Fetch or build CivForge awareness summary for MCP / Grok handoff."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.civforge_auth_headers import civforge_auth_headers


def fetch_awareness_summary(
    kernel: Optional[str] = None,
    *,
    include_receipt_index: bool = True,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """HTTP client: GET /game/awareness/summary from live kernel."""
    base = (kernel or os.environ.get("CIVFORGE_KERNEL_URL", "http://127.0.0.1:8080")).rstrip("/")
    params = {}
    if not include_receipt_index:
        params["receipt_index"] = "0"
    resp = requests.get(
        f"{base}/game/awareness/summary",
        headers=civforge_auth_headers(),
        params=params,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    try:
        print(json.dumps(fetch_awareness_summary(), indent=2))
        return 0
    except requests.RequestException as exc:
        print(json.dumps({"error": str(exc), "hint": "bash tools/start-kernel-8080.sh"}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
