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
    {"name": "civforge_reset_game", "description": "Reset to a fresh game session (turn 1, cleared victory progress)", "inputSchema": {"type": "object", "properties": {}}},
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
    {"name": "civforge_select_district", "description": "Select active CivStudy district (influence cost)", "inputSchema": {
        "type": "object",
        "properties": {"district_id": {"type": "string"}},
        "required": ["district_id"],
    }},
    {"name": "civforge_unlock_policy", "description": "Spend influence to unlock a policy tier", "inputSchema": {
        "type": "object",
        "properties": {"policy_id": {"type": "string"}},
        "required": ["policy_id"],
    }},
    {"name": "civforge_claim_tile", "description": "Claim adjacent neutral/contested map tile", "inputSchema": {
        "type": "object",
        "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
        "required": ["x", "y"],
    }},
    {"name": "civforge_propose_mechanics", "description": "Propose a game mechanic update (Grok swarm proposal lane)", "inputSchema": {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "description": "lane_param|district_yield_override|tick_cadence_override|param_override|policy_definition|fork_definition|tick_module|code_change"},
            "title": {"type": "string"},
            "payload": {"type": "object"},
            "author": {"type": "string", "default": "grok_swarm"},
            "work_pack_id": {"type": "string"},
            "rationale": {"type": "string"},
        },
        "required": ["kind", "title"],
    }},
    {"name": "civforge_gate_mechanics", "description": "FunForge gate on a mechanics proposal", "inputSchema": {
        "type": "object",
        "properties": {
            "proposal_id": {"type": "string"},
            "fun_score_override": {"type": "number"},
        },
        "required": ["proposal_id"],
    }},
    {"name": "civforge_apply_mechanics", "description": "Apply gated-approved runtime mechanics proposal", "inputSchema": {
        "type": "object",
        "properties": {"proposal_id": {"type": "string"}},
        "required": ["proposal_id"],
    }},
    {"name": "civforge_list_mechanics_proposals", "description": "List mechanics proposals and summary", "inputSchema": {
        "type": "object",
        "properties": {"status": {"type": "string"}},
    }},
]


def _http(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{KERNEL}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
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
    elif name == "civforge_reset_game":
        result = _http("POST", "/game/reset")
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
    elif name == "civforge_select_district":
        result = _http("POST", "/game/district/select", {"district_id": arguments["district_id"]})
    elif name == "civforge_unlock_policy":
        result = _http("POST", "/game/policy/unlock", {"policy_id": arguments["policy_id"]})
    elif name == "civforge_claim_tile":
        result = _http("POST", "/game/map/claim", {"x": int(arguments["x"]), "y": int(arguments["y"])})
    elif name == "civforge_propose_mechanics":
        result = _http("POST", "/game/mechanics/propose", {
            "kind": arguments["kind"],
            "title": arguments["title"],
            "payload": arguments.get("payload") or {},
            "author": arguments.get("author", "grok_swarm"),
            "work_pack_id": arguments.get("work_pack_id", ""),
            "rationale": arguments.get("rationale", ""),
        })
    elif name == "civforge_gate_mechanics":
        body: Dict[str, Any] = {"proposal_id": arguments["proposal_id"]}
        if "fun_score_override" in arguments:
            body["fun_score_override"] = float(arguments["fun_score_override"])
        result = _http("POST", "/game/mechanics/gate", body)
    elif name == "civforge_apply_mechanics":
        result = _http("POST", "/game/mechanics/apply", {"proposal_id": arguments["proposal_id"]})
    elif name == "civforge_list_mechanics_proposals":
        status = arguments.get("status")
        path = "/game/mechanics/proposals" + (f"?status={status}" if status else "")
        result = _http("GET", path)
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
