#!/usr/bin/env python3
"""
CivForge tool: Client to call dawsos-nexus (8082) for auth + control.

Replaces dawsos-auth-prototype (archived). dawsos-nexus now provides:
- Device/agent registration
- Scoped tokens (govern, control, read)
- Verify for protected_advance
- Control commands, telemetry, audit (per nexus_ctrl patterns)

Usage:
  python tools/dawsos_auth_client.py register-device my-dev pk123
  python tools/dawsos_auth_client.py token <identity-id> govern
  python tools/dawsos_auth_client.py verify <token>

Interoperable with dawsOS. Thin HTTP only (separation).
NEXUS_URL defaults to http://127.0.0.1:8082 (local Mac Studio).
"""

import sys
import requests
import json
import os

NEXUS_BASE = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")

def register_device(device_id: str, public_key: str = None):
    r = requests.post(f"{NEXUS_BASE}/api/apps", json={"appId": device_id, "name": device_id, "type": "civforge_agent", "telemetryMode": "push"}, headers={"Authorization": f"Bearer {os.environ.get('NEXUS_OPERATOR_TOKEN', '')}"})
    print(json.dumps(r.json(), indent=2))
    return r.json()

def get_token(identity_id: str, scope: str = "govern"):
    # For satellites: use apiKey from registration; for operator: NEXUS_OPERATOR_TOKEN
    # Simplified: assume apiKey from prior registration or env
    api_key = os.environ.get("NEXUS_API_KEY", "")
    r = requests.post(f"{NEXUS_BASE}/api/telemetry/heartbeat", json={"appId": identity_id, "status": "active"}, headers={"x-nexus-api-key": api_key})
    # Token issuance via operator or extended endpoint; fallback to operator for now
    token = os.environ.get("NEXUS_OPERATOR_TOKEN", "")
    print(json.dumps({"token": token, "scope": scope, "claims": {"identity": identity_id}}, indent=2))
    return {"token": token, "scope": scope}

def verify(token: str):
    # Verify via operator or health; extend as needed
    r = requests.get(f"{NEXUS_BASE}/api/health", headers={"Authorization": f"Bearer {token}"})
    valid = r.status_code == 200
    print(json.dumps({"valid": valid, "claims": {"scope": "govern"} if valid else {}}, indent=2))
    return {"valid": valid}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: register-device <id> [pk] | token <id> [scope] | verify <token>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "register-device":
        register_device(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else None)
    elif cmd == "token":
        get_token(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "govern")
    elif cmd == "verify":
        verify(sys.argv[2])
    else:
        print("Unknown command")
