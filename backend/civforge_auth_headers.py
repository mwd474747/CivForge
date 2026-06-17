"""Shared Authorization headers for CivForge HTTP clients (MCP, bridge, CLI)."""

from __future__ import annotations

import os
from typing import Dict, Optional


def resolve_auth_token() -> Optional[str]:
    for name in ("CIVFORGE_AUTH_TOKEN", "CIVFORGE_API_KEY", "CIVFORGE_OPERATOR_TOKEN"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def civforge_auth_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = dict(extra or {})
    token = resolve_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
