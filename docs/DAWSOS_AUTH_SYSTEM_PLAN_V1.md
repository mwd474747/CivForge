# dawsos-auth system plan v1

**Status:** `current` — CivForge planning + consumer contract  
**Label:** planning evidence — not dawsOS wt promotion truth  
**Sister service:** `~/Documents/GitHub/dawsos-auth-prototype` → branded **dawsos-auth** v1.0  
**CivForge consumer:** Block D (kernel verify) + Block E (dashboard/MCP/bridge)

---

## 1. Problem statement

CivForge mutators on `:8080` need a **separate identity plane** from:

- **dawsOS wt** (`:8000`) — workflow dispatch, promotion truth
- **dawsos-nexus** (`:8082`) — fleet telemetry + Mission Control operator UI

The auth prototype on `:8081` proved JWT issuance + verify. Block D wired kernel-side verify. Block E finishes **clients** (dashboard, MCP, HTTP bridge) and promotes the sister repo from prototype to **dawsos-auth v1**.

---

## 2. Plane separation (non-negotiable)

| Plane | Port | Role | CivForge usage |
|-------|------|------|----------------|
| **dawsos-auth** | 8081 | Identity: register, token, verify, refresh | JWT `govern`/`mutate`/`admin` on mutators |
| **dawsos-nexus** | 8082 | Fleet + operator satellite | Telemetry heartbeat only; not product identity |
| **CivForge kernel** | 8080 | Game/governance execution | Verifies JWT via `GET /verify` or `POST /introspect` |

**Rule:** Never merge auth into Nexus. Never treat Nexus operator token as CivForge player identity in production.

---

## 3. dawsos-auth v1 API surface

### Endpoints (stable)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness; returns `service: dawsos-auth`, `version: 1.0` |
| POST | `/register/device` | Device identity |
| POST | `/register/agent` | Agent identity |
| POST | `/login/user` | Demo/stub user (dev only) |
| POST | `/token` | Issue JWT for identity + scope |
| GET | `/verify` | Verify JWT (query `token` or `Authorization` header) |
| POST | `/introspect` | Verify JWT (JSON body `{ "token": "..." }`) |
| POST | `/refresh` | Refresh non-expired JWT |
| GET | `/identities/{id}` | Identity lookup (requires bearer) |
| GET | `/receipts/recent` | Recent auth mutation receipts |

### JWT claims

| Claim | Required | Example |
|-------|----------|---------|
| `sub` | yes | `civforge-player` |
| `scope` | yes | `govern` |
| `aud` | yes (v1) | `civforge-kernel` |
| `iss` | yes (v1) | `dawsos-auth` |
| `exp` | yes | unix timestamp |

### Scope registry

| Scope | CivForge mutators | Notes |
|-------|-------------------|-------|
| `read` | GET only | Insufficient for POST mutators |
| `govern` | All player/governance mutators | Default dashboard/CLI scope |
| `mutate` | Same as govern | Alias for tooling |
| `admin` | Same as govern | Operator lane |

CivForge kernel accepts `govern`, `mutate`, or `admin` on mutators when `CIVFORGE_REQUIRE_AUTH=1`.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `DAWSOS_AUTH_JWT_SECRET` | dev fallback | HS256 secret; **required** when `DAWSOS_AUTH_REQUIRE_SECRET=1` |
| `DAWSOS_AUTH_DEFAULT_AUD` | `civforge-kernel` | Default audience on issued tokens |
| `DAWSOS_AUTH_ISSUER` | `dawsos-auth` | JWT `iss` claim |
| `DAWSOS_AUTH_REQUIRE_SECRET` | off | Fail startup if secret is default |

---

## 4. CivForge consumer contract

### Kernel (`backend/auth_identity.py`)

- Verify via `{DAWSOS_AUTH_BASE}/verify` (default `http://127.0.0.1:8081`)
- Optional audience check: `CIVFORGE_AUTH_AUDIENCE` (default `civforge-kernel`)
- Enabled when `CIVFORGE_REQUIRE_AUTH=1` or `CIVFORGE_IDENTITY_AUTH=1`
- Static token fallback: `CIVFORGE_API_KEY`, `CIVFORGE_OPERATOR_TOKEN`, `NEXUS_API_KEY`

### Dashboard (`frontend/index.html`)

- `localStorage.civforge_auth_token` → `Authorization: Bearer` on all POST mutators
- Auth panel: paste JWT from CLI; show `/game/auth/status` posture
- Token acquisition (dev):

```bash
python3 tools/dawsos_auth_identity_client.py register-device civforge-player
python3 tools/dawsos_auth_identity_client.py token civforge-player govern
```

### Tooling

| Tool | Auth env | Header |
|------|----------|--------|
| `tools/mcp_server.py` | `CIVFORGE_AUTH_TOKEN` or `CIVFORGE_API_KEY` | `Authorization: Bearer` |
| `bridge/civforge_http_bridge.py` | same | same |
| `tools/dawsos_auth_identity_client.py` | — | talks to `:8081` directly |

### Start helpers

```bash
bash tools/start-auth-8081.sh    # sister repo uvicorn :8081
bash tools/start-kernel-8080.sh
export CIVFORGE_REQUIRE_AUTH=1
export CIVFORGE_AUTH_TOKEN="$(python3 tools/dawsos_auth_identity_client.py token civforge-player govern | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
```

---

## 5. Phased rollout

| Phase | Scope | Status |
|-------|-------|--------|
| **A** | Prototype `:8081` + basic verify | Done (sister repo) |
| **B** | Kernel mutator gate (Block D) | Done |
| **C** | dawsos-auth v1 hardening (aud, iss, receipts, introspect) | This slice |
| **D** | CivForge consumers (dashboard, MCP, bridge) | Block E — this slice |
| **E** | wt integration (device-auth.json bridge, LaunchAgent) | Future — approval-gated |
| **F** | Replace demo login with dawsOS user store | Future |

---

## 6. Validation

- Sister repo: `pytest tests/ -q`
- CivForge: `pytest tests/test_wp_grok_block_d_001.py tests/test_wp_grok_auth_consumer_001.py -q`
- Full: `pytest -q` (147+ tests)
- Live: `bash tools/validate-game.sh --read-only`

---

## 7. Rollback

- Disable auth on kernel: unset `CIVFORGE_REQUIRE_AUTH` / `CIVFORGE_PUBLIC_MODE`
- Dashboard: clear `localStorage.civforge_auth_token`
- Sister service: revert to prior commit; `/verify` remains backward compatible

---

## 8. References

- `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` §4.3
- `backend/auth_identity.py`
- `tools/dawsos_auth_identity_client.py` (not `dawsos_auth_client.py` — Nexus `:8082`)
- Sister: `~/Documents/GitHub/dawsos-auth-prototype/README.md`
