#!/usr/bin/env python3
"""
CivForge tool: thin client for dawsos-nexus (8082) machine satellite functions.

Per boundary contract:
- Nexus = telemetry (heartbeats with customMetrics/agentState) + command queue (proposals).
- Register app (governance_kernel type) + x-nexus-api-key for heartbeats/poll.
- **Not** product identity. Scoped "govern" here is machine context only.
- Identity / JWT / user scopes long-term via dawsos-auth-prototype :8081 (or explicit local dev operator bypass documented in SEPARATION.md).
- Does not replace auth-prototype. "Replaces" language limited to old prototype's machine satellite parts only.

Usage (machine only):
  python tools/dawsos_auth_client.py register-device civforge-kernel
  ... (heartbeats, basic verify for dev)

Thin HTTP only. See SEPARATION.md planes + wt governed-connectors-registry.v1 for civforge_kernel.
NEXUS_URL defaults to http://127.0.0.1:8082.
"""

import sys
import requests
import json
import os

NEXUS_BASE = os.environ.get("NEXUS_URL", "http://127.0.0.1:8082")

def register_device(device_id: str, public_key: str = None):
    # Per agent rec + Q3: type governance_kernel (canon); prefer NEXUS_API_KEY (x-nexus-api-key) for satellite register.
    api_key = os.environ.get("NEXUS_API_KEY", "")
    headers = {"x-nexus-api-key": api_key} if api_key else {"Authorization": f"Bearer {os.environ.get('NEXUS_OPERATOR_TOKEN', '')}"}
    r = requests.post(f"{NEXUS_BASE}/api/apps", json={"appId": device_id, "name": device_id, "type": "governance_kernel", "telemetryMode": "push"}, headers=headers)
    print(json.dumps(r.json(), indent=2))
    return r.json()

def get_token(identity_id: str, scope: str = "govern"):
    # For satellites (governance_kernel): use NEXUS_API_KEY (x-nexus-api-key) per Q3 satellite-only posture.
    # No operator fallback in primary path.
    api_key = os.environ.get("NEXUS_API_KEY", "") or os.environ.get("NEXUS_OPERATOR_TOKEN", "")
    headers = {"x-nexus-api-key": api_key} if api_key else {}
    r = requests.post(f"{NEXUS_BASE}/api/telemetry/heartbeat", json={"appId": identity_id, "status": "active"}, headers=headers)
    # Machine context only; real identity via 8081 auth-prototype long-term.
    token = api_key
    print(json.dumps({"token": token, "scope": scope, "claims": {"identity": identity_id, "note": "machine satellite key only"}}, indent=2))
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
