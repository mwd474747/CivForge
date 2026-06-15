#!/usr/bin/env python3
"""
CivForge MCP tool server (stdio JSON-RPC).

Exposes kernel HTTP endpoints as MCP tools for agent-player lane.
Requires live kernel at CIVFORGE_KERNEL_URL (default http://127.0.0.1:8080).

Run: python3 tools/mcp_server.py
Or:  python3 tools/civforge_cli.py mcp-serve
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

KERNEL = os.environ.get("CIVFORGE_KERNEL_URL", "http://127.0.0.1:8080").rstrip("/")

TOOLS = [
    {"name": "civforge_status", "description": "Get live governance + multi-agent state", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "civforge_advance_turn", "description": "Advance one governance cycle", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "civforge_found_city", "description": "Found a work pack / city", "inputSchema": {
        "type": "object",
        "properties": {
            "city_name": {"type": "string"},
            "investment": {"type": "integer", "default": 4},
        },
    }},
    {"name": "civforge_negotiate", "description": "Send negotiation offer to an agent", "inputSchema": {
        "type": "object",
        "properties": {"to": {"type": "string"}, "offer": {"type": "string"}},
        "required": ["to", "offer"],
    }},
    {"name": "civforge_negotiate_respond", "description": "Accept or decline a pending negotiation", "inputSchema": {
        "type": "object",
        "properties": {
            "negotiation_id": {"type": "string"},
            "accept": {"type": "boolean", "default": True},
        },
        "required": ["negotiation_id"],
    }},
    {"name": "civforge_what_if", "description": "Simulation what-if with investment", "inputSchema": {
        "type": "object",
        "properties": {"investment": {"type": "integer", "default": 5}},
    }},
    {"name": "civforge_governance_propose", "description": "Create a governed proposal (gravity/meta work)", "inputSchema": {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "investment": {"type": "integer", "default": 3},
            "details": {"type": "object"},
        },
        "required": ["action"],
    }},
    {"name": "civforge_governance_gate", "description": "Run FunForge gate on a proposal", "inputSchema": {
        "type": "object",
        "properties": {"proposal_id": {"type": "string"}},
        "required": ["proposal_id"],
    }},
]


def _http(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    api_key = os.environ.get("CIVFORGE_API_KEY") or os.environ.get("NEXUS_API_KEY")
    if api_key:
        headers["X-CivForge-Token"] = api_key
    req = urllib.request.Request(
        f"{KERNEL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode(), "status": e.code}


def _call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "civforge_status":
        result = _http("GET", "/state")
    elif name == "civforge_advance_turn":
        result = _http("POST", "/advance_turn")
    elif name == "civforge_found_city":
        result = _http("POST", "/found_city", {
            "city_name": arguments.get("city_name", "New Work Pack"),
            "investment": int(arguments.get("investment", 4)),
        })
    elif name == "civforge_negotiate":
        result = _http("POST", "/game/negotiate", {
            "to": arguments["to"],
            "offer": arguments["offer"],
        })
    elif name == "civforge_negotiate_respond":
        result = _http("POST", "/game/negotiate/respond", {
            "negotiation_id": arguments["negotiation_id"],
            "accept": bool(arguments.get("accept", True)),
        })
    elif name == "civforge_what_if":
        result = _http("POST", "/simulation/what_if", {"investment": int(arguments.get("investment", 5))})
    elif name == "civforge_governance_propose":
        result = _http("POST", "/governance/propose", {
            "action": arguments["action"],
            "investment": int(arguments.get("investment", 3)),
            "details": arguments.get("details") or {"via": "mcp"},
        })
    elif name == "civforge_governance_gate":
        result = _http("POST", "/governance/gate", {"proposal_id": arguments["proposal_id"]})
    else:
        result = {"error": f"unknown tool: {name}"}
    text = json.dumps(result, indent=2)
    return {"content": [{"type": "text", "text": text}]}


def _respond(msg_id: Any, result: Any) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()


def _respond_err(msg_id: Any, code: int, message: str) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


def handle(msg: Dict[str, Any]) -> None:
    msg_id = msg.get("id")
    method = msg.get("method", "")

    if method == "initialize":
        _respond(msg_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "civforge-mcp", "version": "1.0.0"},
        })
    elif method == "notifications/initialized":
        return
    elif method == "tools/list":
        _respond(msg_id, {"tools": TOOLS})
    elif method == "tools/call":
        params = msg.get("params") or {}
        _respond(msg_id, _call_tool(params.get("name", ""), params.get("arguments") or {}))
    elif method == "ping":
        _respond(msg_id, {})
    else:
        if msg_id is not None:
            _respond_err(msg_id, -32601, f"Method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle(json.loads(line))
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
