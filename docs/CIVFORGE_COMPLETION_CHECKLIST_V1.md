# CivForge completion checklist v1

**Status:** `current` — Vercel prod **https://civforge.vercel.app** deployed 2026-06-15
**Boundary:** `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`

---

## Done (verified 2026-06-15)

| Item | Evidence |
|------|----------|
| Kernel `:8080` live | `GET /state` → turn 11, fun 86.6 |
| Nexus `:8082` health | `{"status":"ok","service":"dawsos-nexus",...}` |
| `civforge-kernel` registered | Nexus apps: `governance_kernel`, heartbeats, `allowedActions: ["sync_config"]` |
| `what_if` real Nexus context | `nexus_context` has service/version/bind/port (not fallback note) |
| Poller strict `sync_config` | `tools/nexus_command_poller.py` |
| Satellite key posture | `_headers()` API_KEY only; register requires `NEXUS_API_KEY` |
| Boundary contract committed | `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` (in repo history via prior commits) |
| wt pointer | `engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` (wt — commit separately) |

---

## Remaining (operator / Claw)

### 1. `NEXUS_API_KEY` in CivForge shell

Nexus masks keys in operator API (`nxs_07f0…60ea`). Export the **full** satellite key from provisioning receipt or Postgres into CivForge env (never commit):

```bash
export NEXUS_API_KEY='nxs_...'   # from OpenClaw Phase B provisioning
export NEXUS_URL=http://127.0.0.1:8082
python3 tools/nexus_command_poller.py --once
```

### 2. Real Vercel production URL

```bash
cd ~/CivForge
npx vercel login    # once, in persistent terminal
npx vercel link     # if not linked
npx vercel --prod
```

Paste the `https://*.vercel.app` URL into receipt + handoff.

**Important:** Default dashboard uses `?api_base=http://127.0.0.1:8080` — works only when opened **on the Mac Studio host** and may still fail (HTTPS page → HTTP localhost). For remote viewing, use an **HTTPS tunnel** to `:8080` and open:

`https://<your-vercel-app>.vercel.app/?api_base=https://<your-tunnel-host>`

### 3. Optional: auth-prototype `:8081` for identity

`require_machine_satellite_key` still verifies via Nexus `/api/health` — not JWT. Wire `:8081` verify when ready (Phase D / CivForge hygiene).

### 4. Sister: SIS-NEXUS-B

Ack/complete API-key auth; control proxy reject for `governance_kernel`.

---

## Quick validation script (Mac Studio)

```bash
curl -sf http://127.0.0.1:8080/state | head -c 120
curl -sf http://127.0.0.1:8082/api/health
curl -sf -X POST http://127.0.0.1:8080/simulation/what_if -H 'Content-Type: application/json' -d '{"investment":5}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('fun_impact_estimate'), 'fallback' not in str(d.get('nexus_context','')))"
```

---

## Completion definition

- [x] 8082 live + civforge-kernel registered + real `what_if` context
- [ ] `NEXUS_API_KEY` exported + poller `--once` with pending command test (optional)
- [x] Real Vercel `--prod` URL: **https://civforge.vercel.app**
- [ ] wt planning pointer committed (OpenClaw packet, separate repo)
