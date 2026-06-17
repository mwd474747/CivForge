#!/usr/bin/env python3
"""CivForge thin client for dawsos-auth identity plane (:8081).

Separate from tools/dawsos_auth_client.py (Nexus :8082 machine satellite).

Usage:
  python3 tools/dawsos_auth_identity_client.py health
  python3 tools/dawsos_auth_identity_client.py register-device civforge-player pk-demo
  python3 tools/dawsos_auth_identity_client.py token civforge-player govern
  python3 tools/dawsos_auth_identity_client.py verify <jwt>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional

import requests

BASE = os.environ.get("DAWSOS_AUTH_BASE", "http://127.0.0.1:8081").rstrip("/")


def _post(path: str, payload: dict) -> dict:
    resp = requests.post(f"{BASE}{path}", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get(path: str, **kwargs) -> dict:
    resp = requests.get(f"{BASE}{path}", timeout=10, **kwargs)
    resp.raise_for_status()
    return resp.json()


def cmd_health() -> None:
    print(json.dumps(_get("/health"), indent=2))


def cmd_register_device(device_id: str, public_key: Optional[str]) -> None:
    print(json.dumps(_post("/register/device", {"device_id": device_id, "public_key": public_key}), indent=2))


def cmd_register_agent(agent_id: str, capabilities: List[str]) -> None:
    print(json.dumps(_post("/register/agent", {"agent_id": agent_id, "capabilities": capabilities}), indent=2))


def cmd_token(identity_id: str, scope: str) -> None:
    print(json.dumps(_post("/token", {"identity_id": identity_id, "scope": scope}), indent=2))


def cmd_verify(token: str) -> None:
    print(json.dumps(_get("/verify", params={"token": token}), indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="dawsos-auth client (:8081)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    reg = sub.add_parser("register-device")
    reg.add_argument("device_id")
    reg.add_argument("public_key", nargs="?", default=None)
    agent = sub.add_parser("register-agent")
    agent.add_argument("agent_id")
    agent.add_argument("capabilities", nargs="*", default=["read", "govern"])
    tok = sub.add_parser("token")
    tok.add_argument("identity_id")
    tok.add_argument("scope", nargs="?", default="govern")
    ver = sub.add_parser("verify")
    ver.add_argument("token")
    args = parser.parse_args()

    try:
        if args.cmd == "health":
            cmd_health()
        elif args.cmd == "register-device":
            cmd_register_device(args.device_id, args.public_key)
        elif args.cmd == "register-agent":
            cmd_register_agent(args.agent_id, list(args.capabilities))
        elif args.cmd == "token":
            cmd_token(args.identity_id, args.scope)
        elif args.cmd == "verify":
            cmd_verify(args.token)
        return 0
    except requests.RequestException as exc:
        print(json.dumps({"error": str(exc), "auth_base": BASE}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
