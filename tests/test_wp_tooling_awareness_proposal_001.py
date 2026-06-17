"""WP-TOOLING-AWARENESS-PROPOSAL-001 — full closure tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.awareness_summary import build_awareness_summary  # noqa: E402
from backend.game_reset import build_initial_game_state  # noqa: E402
from core.mechanics_registry import build_default_registry  # noqa: E402


def test_build_awareness_summary_shape():
    state = build_initial_game_state()
    reg = build_default_registry()
    summary = build_awareness_summary(state, reg, receipt_index={"schema": "test"})
    assert summary["schema"] == "civforge.awareness_summary.v1"
    assert "mechanics_status" in summary
    assert "mechanics_proposals" in summary
    assert "civstudy_anchors" in summary
    assert summary["receipt_index"]["schema"] == "test"


def test_http_awareness_summary_route():
    from fastapi.testclient import TestClient

    import backend.sim_api as api

    api.game_state = build_initial_game_state()
    api.orchestrator.turn = api.game_state["turn"]
    client = TestClient(api.app)
    data = client.get("/game/awareness/summary").json()
    assert data["schema"] == "civforge.awareness_summary.v1"
    assert "mechanics_status" in data
    assert "registry_modules" in data["mechanics_status"]


def test_mcp_state_summary_fetch_live():
    import requests

    try:
        r = requests.get("http://127.0.0.1:8080/game/awareness/summary", timeout=2)
        if r.status_code == 404:
            pytest.skip("kernel :8080 needs restart for /game/awareness/summary")
        r.raise_for_status()
    except requests.RequestException:
        pytest.skip("kernel :8080 not live")
    from tools.mcp_state_summary import fetch_awareness_summary

    data = fetch_awareness_summary()
    assert data["schema"] == "civforge.awareness_summary.v1"


def test_mcp_server_lists_state_summary_tool():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mcp_server.py")],
        input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    tools = json.loads(proc.stdout.strip().splitlines()[0])["result"]["tools"]
    names = {t["name"] for t in tools}
    assert "civforge_state_summary" in names


def test_dashboard_grok_view_markup():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert "grok_view" in html
    assert "grok-awareness-panel" in html
    assert "/game/awareness/summary" in html


def test_cli_snapshot_registered():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "civforge_cli.py"), "-h"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert "snapshot" in proc.stdout
