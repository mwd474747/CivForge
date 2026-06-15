# dawsos-nexus reference for CivForge (boundary-aligned)

**Canonical name:** `dawsos-nexus` (Mac Studio `:8082`)  
**Legacy alias:** `nexus_ctrl` — upstream Replit-era repo name only; **do not use in new docs**  
**Sister repo:** `~/Documents/GitHub/dawsos-nexus`

---

## Pattern (all apps)

Every governed app uses the **same dawsos-nexus satellite pattern**:

| Concern | dawsos-nexus role |
|---------|-------------------|
| Telemetry | Push heartbeat → `POST /api/telemetry/heartbeat` |
| Commands | Queue → local poller → **propose only** (FunForge gate) |
| Registration | `app_id` in wt `governed-connectors-registry` + Nexus Postgres |
| Auth | Satellite `x-nexus-api-key` (not product identity) |
| Identity | Separate plane — CivForge uses `dawsos-auth-prototype` `:8081` |

CivForge is `governance_kernel` with `app_id: civforge-kernel`.

---

## CivForge wiring

- **Telemetry:** `send_telemetry_to_nexus()` in `backend/sim_api.py`
- **Commands in:** `tools/nexus_command_poller.py` → `/governance/propose` only
- **Allowed action:** `sync_config` (per wt registry)
- **Probe:** `GET http://127.0.0.1:8080/state`
- **Forbidden:** Nexus control-proxy / `metricsUrl` pull-control on `:8080`; direct `/advance_turn` from poll

---

## wt canon

- Registry: `engine-src/active/config/ops/governed-connectors-registry.v1.json` → `civforge_kernel`
- Mirrors: `reports/ops/nexus-fleet-health-mirror-latest.json`, `nexus-audit-mirror-latest.json`
- Integration probe: `civforge_kernel` in `integration-http-probes-latest.json`

---

## Not dawsos-nexus

| Item | Plane |
|------|-------|
| CivForge execution truth | `:8080` + `receipts/` |
| dawsOS promotion truth | wt `reports/ops/*` |
| Product JWT identity | `:8081` auth-prototype |

See `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`, `SEPARATION.md`.

---

## Historical note

June 2026 receipts used "nexus_ctrl" while reviewing the Replit → local migration. Runtime truth has been **dawsos-nexus on :8082** since WP-001 closure. Auth-absorption into Nexus was **not** executed; identity remains `:8081` per boundary contract.
