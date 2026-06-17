"""Thin identity plane client — dawsos-auth (:8081) JWT verify."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

AUTH_BASE = os.environ.get("DAWSOS_AUTH_BASE", "http://127.0.0.1:8081").rstrip("/")
AUTH_AUDIENCE = os.environ.get("CIVFORGE_AUTH_AUDIENCE", "civforge-kernel").strip()
MUTATOR_SCOPES = frozenset({"govern", "mutate", "admin"})


def identity_auth_enabled() -> bool:
    raw = os.environ.get("CIVFORGE_IDENTITY_AUTH", "")
    if raw.strip():
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    require = os.environ.get("CIVFORGE_REQUIRE_AUTH", "").strip().lower()
    return require in {"1", "true", "yes", "on"}


def looks_like_jwt(token: str) -> bool:
    parts = token.split(".")
    return len(parts) == 3 and all(parts)


def verify_identity_token(
    token: str,
    *,
    required_scope: str = "govern",
    timeout: float = 4.0,
) -> Dict[str, Any]:
    """Verify JWT via dawsos-auth GET /verify."""
    if not token:
        return {"valid": False, "error": "empty_token"}
    try:
        resp = requests.get(
            f"{AUTH_BASE}/verify",
            params={"token": token},
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )
        if resp.status_code != 200:
            return {"valid": False, "error": f"verify_http_{resp.status_code}"}
        data = resp.json()
        if not data.get("valid"):
            return {"valid": False, "error": "invalid_token"}
        claims = data.get("claims") or {}
        scope = str(claims.get("scope", ""))
        if required_scope == "govern" and scope not in MUTATOR_SCOPES:
            return {"valid": False, "error": "insufficient_scope", "claims": claims}
        aud = claims.get("aud")
        if AUTH_AUDIENCE and aud and str(aud) != AUTH_AUDIENCE:
            return {"valid": False, "error": "audience_mismatch", "claims": claims}
        return {
            "valid": True,
            "claims": claims,
            "identity": claims.get("sub"),
            "scope": scope,
            "audience": aud or AUTH_AUDIENCE,
            "source": "dawsos-auth-8081",
        }
    except requests.RequestException as exc:
        return {"valid": False, "error": f"auth_unreachable:{exc}"}


def auth_status_summary() -> Dict[str, Any]:
    """Machine-readable auth posture for /game/auth/status."""
    enabled = identity_auth_enabled()
    public_mode = os.environ.get("CIVFORGE_PUBLIC_MODE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    require_auth = os.environ.get("CIVFORGE_REQUIRE_AUTH", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    reachable = False
    health: Optional[Dict[str, Any]] = None
    try:
        resp = requests.get(f"{AUTH_BASE}/health", timeout=2.0)
        reachable = resp.status_code == 200
        if reachable:
            health = resp.json()
    except requests.RequestException:
        reachable = False
    return {
        "identity_auth_enabled": enabled,
        "public_mode": public_mode,
        "require_auth": require_auth,
        "auth_base": AUTH_BASE,
        "auth_reachable": reachable,
        "auth_health": health,
        "auth_audience": AUTH_AUDIENCE or None,
        "mutator_scopes": sorted(MUTATOR_SCOPES),
        "static_token_envs": [
            name
            for name in ("CIVFORGE_OPERATOR_TOKEN", "CIVFORGE_API_KEY", "NEXUS_API_KEY")
            if os.environ.get(name)
        ],
    }
