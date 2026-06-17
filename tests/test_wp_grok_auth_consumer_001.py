"""Block E — CivForge auth consumers (dashboard/MCP/bridge helpers)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.auth_identity import verify_identity_token  # noqa: E402
from backend.civforge_auth_headers import civforge_auth_headers, resolve_auth_token  # noqa: E402


def test_resolve_auth_token_prefers_jwt_env(monkeypatch):
    monkeypatch.setenv("CIVFORGE_AUTH_TOKEN", "jwt-token")
    monkeypatch.setenv("CIVFORGE_API_KEY", "api-key")
    assert resolve_auth_token() == "jwt-token"


def test_civforge_auth_headers_bearer(monkeypatch):
    monkeypatch.setenv("CIVFORGE_AUTH_TOKEN", "abc.def.ghi")
    headers = civforge_auth_headers({"Content-Type": "application/json"})
    assert headers["Authorization"] == "Bearer abc.def.ghi"
    assert headers["Content-Type"] == "application/json"


def test_civforge_auth_headers_empty_without_env(monkeypatch):
    monkeypatch.delenv("CIVFORGE_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("CIVFORGE_API_KEY", raising=False)
    monkeypatch.delenv("CIVFORGE_OPERATOR_TOKEN", raising=False)
    assert civforge_auth_headers() == {}


@patch("backend.auth_identity.requests.get")
def test_verify_identity_token_audience_mismatch(mock_get, monkeypatch):
    monkeypatch.setenv("CIVFORGE_AUTH_AUDIENCE", "civforge-kernel")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "valid": True,
        "claims": {"sub": "x", "scope": "govern", "aud": "wrong-aud"},
    }
    result = verify_identity_token("a.b.c")
    assert result["valid"] is False
    assert result["error"] == "audience_mismatch"


@patch("backend.auth_identity.requests.get")
def test_verify_identity_token_allows_missing_aud(mock_get, monkeypatch):
    monkeypatch.setenv("CIVFORGE_AUTH_AUDIENCE", "civforge-kernel")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "valid": True,
        "claims": {"sub": "legacy", "scope": "govern"},
    }
    result = verify_identity_token("a.b.c")
    assert result["valid"] is True


def test_bridge_imports_auth_headers():
    from bridge.civforge_http_bridge import _request  # noqa: F401


def test_dashboard_sends_auth_storage_key():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert "civforge_auth_token" in html
    assert "function authFetch" in html
    assert "authFetch(apiBase +" in html
