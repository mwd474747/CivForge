#!/usr/bin/env python3
"""
CivForge tool: Client to call the separate dawsos-auth-prototype.

This keeps the auth prototype 100% separate (in ~/Documents/GitHub/dawsos-auth-prototype).
CivForge can use it for governance auth (e.g. token for proposals, device identity for bridges).

Usage:
  python tools/dawsos_auth_client.py register-device my-dev pk123
  python tools/dawsos_auth_client.py token <identity-id> read
  python tools/dawsos_auth_client.py verify <token>

Interoperable with dawsOS (loads seeds if present in ~/.openclaw/identity).
"""

import sys
import requests
import json

AUTH_BASE = "http://localhost:8081"  # the separate prototype

def register_device(device_id: str, public_key: str = None):
    r = requests.post(f"{AUTH_BASE}/register/device", json={"device_id": device_id, "public_key": public_key})
    print(json.dumps(r.json(), indent=2))
    return r.json()

def get_token(identity_id: str, scope: str = "read"):
    r = requests.post(f"{AUTH_BASE}/token", json={"identity_id": identity_id, "scope": scope})
    print(json.dumps(r.json(), indent=2))
    return r.json()

def verify(token: str):
    r = requests.get(f"{AUTH_BASE}/verify", params={"token": token})
    print(json.dumps(r.json(), indent=2))
    return r.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Commands: register-device <id> [pk], token <id> [scope], verify <token>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "register-device":
        register_device(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else None)
    elif cmd == "token":
        get_token(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "read")
    elif cmd == "verify":
        verify(sys.argv[2])
    else:
        print("Unknown command")
