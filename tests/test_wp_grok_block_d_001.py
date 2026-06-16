"""Block D — :8081 JWT identity on mutators (WP-GROK-JWT-IDENTITY-001)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.auth_identity import (  # noqa: E402
    auth_status_summary,
    identity_auth_enabled,
    looks_like_jwt,
    verify_identity_token,
)
from backend.game_reset import build_initial_game_state  # noqa: E402


def test_looks_like_jwt():
    assert looks_like_jwt("aaa.bbb.ccc") is True
    assert looks_like_jwt("not-a-jwt") is False


def test_identity_auth_enabled_follows_require_auth(monkeypatch):
    monkeypatch.delenv("CIVFORGE_IDENTITY_AUTH", raising=False)
    monkeypatch.delenv("CIVFORGE_REQUIRE_AUTH", raising=False)
    assert identity_auth_enabled() is False
    monkeypatch.setenv("CIVFORGE_REQUIRE_AUTH", "1")
    assert identity_auth_enabled() is True


@patch("backend.auth_identity.requests.get")
def test_verify_identity_token_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "valid": True,
        "claims": {"sub": "civforge-player", "scope": "govern"},
    }
    result = verify_identity_token("header.payload.sig")
    assert result["valid"] is True
    assert result["identity"] == "civforge-player"


@patch("backend.auth_identity.requests.get")
def test_verify_identity_token_rejects_read_scope_on_mutator(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "valid": True,
        "claims": {"sub": "reader", "scope": "read"},
    }
    result = verify_identity_token("a.b.c", required_scope="govern")
    assert result["valid"] is False
    assert result["error"] == "insufficient_scope"


def test_auth_status_summary_shape(monkeypatch):
    monkeypatch.setenv("CIVFORGE_REQUIRE_AUTH", "0")
    summary = auth_status_summary()
    assert "auth_base" in summary
    assert "identity_auth_enabled" in summary
    assert "mutator_scopes" in summary


def test_mutator_blocked_without_token_when_require_auth(monkeypatch):
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    monkeypatch.setenv("CIVFORGE_REQUIRE_AUTH", "1")
    monkeypatch.delenv("CIVFORGE_API_KEY", raising=False)
    monkeypatch.delenv("CIVFORGE_OPERATOR_TOKEN", raising=False)
    monkeypatch.delenv("NEXUS_API_KEY", raising=False)
    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    blocked = client.post("/advance_turn")
    assert blocked.status_code == 401


def test_mutator_accepts_static_api_key_when_require_auth(monkeypatch):
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    monkeypatch.setenv("CIVFORGE_REQUIRE_AUTH", "1")
    monkeypatch.setenv("CIVFORGE_API_KEY", "test-static-key")
    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    ok = client.post("/advance_turn", headers={"Authorization": "Bearer test-static-key"})
    assert ok.status_code == 200


@patch("backend.sim_api.verify_identity_token")
def test_mutator_accepts_jwt_when_verified(mock_verify, monkeypatch):
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    monkeypatch.setenv("CIVFORGE_REQUIRE_AUTH", "1")
    mock_verify.return_value = {
        "valid": True,
        "scope": "govern",
        "identity": "civforge-player",
        "source": "auth-prototype-8081",
    }
    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]

    client = TestClient(api.app)
    ok = client.post(
        "/advance_turn",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJwIn0.sig"},
    )
    assert ok.status_code == 200
    mock_verify.assert_called_once()


def test_http_auth_status_route():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    client = TestClient(api.app)
    status = client.get("/game/auth/status").json()
    assert status["auth_base"].endswith("8081")
    assert "identity_auth_enabled" in status
