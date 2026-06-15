# CivForge ↔ dawsOS boundary contract v1

**Status:** `current` — cross-plane planning contract (both repos)
**Canonical home:** `~/CivForge/docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`
**dawsOS mirror:** `engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` (pointer only)
**wt policy row:** `engine-src/active/config/ops/governed-connectors-registry.v1.json` → `civforge_kernel`
**Label:** planning evidence — not promotion truth; not an execution-authority grant

---

## 1. Purpose

CivForge is a **separate governed plane** that borrows dawsOS *patterns* and dawsos-nexus *visibility*. This contract prevents:

- CivForge execution or receipts becoming dawsOS promotion truth
- dawsOS workflow dispatch absorbing CivForge governance
- dawsos-nexus replacing identity authority (auth-prototype)
- Nexus control-proxy or command paths bypassing CivForge FunForge gates

See also: `SEPARATION.md` (CivForge ↔ gravity-mosaic), dawsOS `STACK_BOUNDARY_CONTRACT_V1.md` (Mission Control stack).

---

## 2. Plane map

| Plane | CivForge owner | dawsOS wt owner | Shared bridge |
|-------|----------------|-----------------|---------------|
| **Execution** | `:8080` `backend/sim_api.py` + `core/` | `:8000` `workflow_dispatch` | None (default) |
| **Receipts** | `receipts/*.md` + SQLite | `reports/ops/*` | None |
| **Identity** | Future: thin client → auth-prototype `:8081` | `dawsos-auth-prototype` canon | HTTP verify only |
| **Fleet telemetry** | Push heartbeats | Mirror builders → `reports/ops/nexus-*` | dawsos-nexus `:8082` |
| **Command intents** | Poll → local `/governance/propose` | `nexus_command_dispatch` (dawsOS satellites only) | Nexus queue only |
| **Metadata policy** | Read-only: app_id + allowed_actions | `governed-connectors-registry.v1` | Canon row `civforge_kernel` |

**Rule:** CivForge is **not** a `dawsos_service` wt satellite. It is a `governance_kernel` Nexus satellite with CivForge-local execution truth.

---

## 3. Ports and probes

| Service | Port | Lock / probe endpoint | Owner |
|---------|------|----------------------|-------|
| CivForge kernel | 8080 | `GET /state` → 200 | CivForge |
| dawsOS API | 8000 | `GET /api/ready` | wt |
| dawsos-nexus | 8082 | `GET /api/health` (public) | sister |
| dawsos-auth-prototype | 8081 | `GET /health` | sister |

wt HTTP probes include CivForge via canon — that is **liveness only**, not governance import.

---

## 4. Allowed bridges (thin HTTP only)

### 4.1 CivForge → dawsos-nexus (telemetry)

- **Tool:** `send_telemetry_to_nexus()` in `backend/sim_api.py`
- **Endpoint:** `POST /api/telemetry/heartbeat`
- **Auth:** `x-nexus-api-key` per registered `civforge-kernel` app (not operator token in production)
- **Payload:** `customMetrics` (turn, funScore, resources, territories, cities, events)
- **Contract:** fire-and-forget; never block `:8080` kernel on Nexus failure

### 4.2 CivForge → dawsos-nexus (commands in)

- **Tool:** `tools/nexus_command_poller.py`
- **Sister contract:** `GET /api/apps/civforge-kernel/commands/pending` → propose locally → `POST /api/commands/{id}/acknowledge` + `complete`
- **Mapping:** Nexus action → `POST /governance/propose` with `action=nexus_<action>` — **never** direct state mutation from poll loop
- **Forbidden:** calling `/found_city`, `/advance_turn`, or service restarts on command receipt without FunForge gate

### 4.3 CivForge → dawsos-auth-prototype (identity — target steady state)

- **Tool:** `tools/dawsos_auth_client.py` (to be realigned to `:8081` for JWT verify)
- **Use:** `govern` scope for `/governance/protected_advance` and sensitive operator paths
- **Not a substitute:** Nexus operator token is for Mission Control operator UI, not CivForge product identity

### 4.4 dawsOS → CivForge (read-only)

- HTTP probe to `:8080/state`
- Nexus fleet mirror visibility when app registered
- **Forbidden:** wt scripts writing CivForge repo, DB, or receipts

### 4.5 CivForge → dawsOS (none by default)

- No `workflow_dispatch` calls
- No `reports/ops` writes
- No wt source edits

Integration requires a future **`CUR-CIVFORGE-BRIDGE`** approval packet — not implied by this contract.

---

## 5. Nexus registration canon (from wt)

From `governed-connectors-registry.v1.json`:

```json
{
  "id": "civforge_kernel",
  "nexus": {
    "app_id": "civforge-kernel",
    "type": "governance_kernel",
    "allowed_actions": ["sync_config"]
  }
}
```

**CivForge implementation must:**

- Register as `civforge-kernel` with `type: governance_kernel`
- Treat `pause`, `resume`, `restart`, `run_task`, etc. as **local proposals** surfaced through FunForge — not auto-executed
- **Not** set `metricsUrl` to CivStudy `/api/automation/metrics` unless CivForge implements an explicit governed `/api/control/*` handler (not present today)

**dawsOS sister hardening (SIS-NEXUS-B):** control proxy disabled for `governance_kernel` and `dawsos_service`; ack/complete require API key.

---

## 6. Anti-patterns (explicit block list)

| ID | Anti-pattern | Owner fix |
|----|--------------|-----------|
| CF-AP-01 | CivForge receipts promoted as `reports/ops` truth | Never — separate planes |
| CF-AP-02 | Nexus operator token as CivForge production identity | Use auth-prototype or local dev exception |
| CF-AP-03 | Command poll mutates game state without propose/gate | Poller → propose only |
| CF-AP-04 | wt `nexus_command_dispatch` handles CivForge commands | CivForge-local dispatch only |
| CF-AP-05 | Nexus control proxy hits `:8080` without governed handler | No `metricsUrl` control path until designed |
| CF-AP-06 | CivForge code vendored into wt `engine-src/` | Thin clients in CivForge `tools/` only |
| CF-AP-07 | OpenClaw lands CivForge mechanics in wt | Separate commit families / repos |

---

## 7. Minimal OpenClaw responsibilities

OpenClaw **does not** run CivForge governance loops. Minimal cross-stack duties:

1. Keep `civforge_kernel` row accurate in `governed-connectors-registry.v1.json`
2. Maintain Nexus `:8082` when fleet visibility is desired (operator lane)
3. Register `civforge-kernel` in Nexus Postgres; issue satellite API key to CivForge env only
4. Keep HTTP probe green for `:8080/state`
5. Apply SIS-NEXUS-B before expanding dashboard control over CivForge

OpenClaw **must not** treat CivForge `receipts/` as C2/promotion evidence.

---

## 8. Code alignment backlog (CivForge repo)

| Item | Status | Notes |
|------|--------|-------|
| Swarm class documentation | **Done** | `docs/CIVFORGE_SWARM_CLASS_V1.md` |
| dawsos-nexus naming | **Done** | `docs/dawsos_nexus_reference.md` (retired `nexus_ctrl_*` active docs) |
| Governance posture builders | **Done** | `civforge_governance_posture.py`, poller/receipt-index/contract-parity |
| Proposal/gate persistence | **Done** | SQLite-backed in `sim_api.py` / `governance.py` |
| Auth story | **Open** | Identity → auth-prototype `:8081`; Nexus machine key only |
| Poller side effects | **Done** | Propose-only path |
| App type strings | **Done** | `governance_kernel` + `civforge-kernel` |

---

## 9. Validation hooks

**CivForge local:**

```bash
curl -sf http://127.0.0.1:8080/state
python3 tools/civforge_cli.py status
grep -l "separate projects" SEPARATION.md docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md
```

**dawsOS wt (read-only):**

```bash
curl -sf http://127.0.0.1:8080/state   # probe target from canon
python3 engine-src/active/scripts/ops/integration_http_probes_build.py
```

**When Nexus live:**

- `civforge-kernel` appears in fleet mirror `live_apps_reported >= 1`
- Heartbeats visible; commands surface as proposals in CivForge receipts

---

## 10. Versioning

- **v1** (2026-06-15): Initial cross-plane contract after Mission Control Phase A lock (`999d476`).
- Updates require receipt in CivForge `receipts/` and wt planning-inputs disposition note (no wt execution claims).
