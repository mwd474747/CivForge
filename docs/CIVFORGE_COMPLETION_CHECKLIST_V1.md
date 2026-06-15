# CivForge completion checklist v1

**Status:** `current` — proposal **1351a353** closed 2026-06-15 (`3f4b7af` landed)
**Boundary:** `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`

---

## Done (verified 2026-06-15)

| Item | Evidence |
|------|----------|
| Kernel `:8080` live | `GET /state` → turn 11, fun 86.8 |
| Nexus `:8082` health | `{"status":"ok","service":"dawsos-nexus",...}` |
| `civforge-kernel` registered | `governance_kernel`, healthy, `allowedActions: ["sync_config"]` |
| `what_if` real Nexus context | fun_impact ~91.8; no fallback |
| Poller strict `sync_config` | `blocked_by_canon` on restart; propose on sync_config |
| Satellite key | `~/.openclaw/runtime/nexus-satellite-api-keys.json` (mode 0600) |
| Vercel prod | https://civforge.vercel.app |
| Local dashboard | http://127.0.0.1:8080/dashboard (200) |
| Governed land | commit `3f4b7af` pushed to main |

---

## Closed — proposal 1351a353

- [x] 8082 live + real `what_if` nexus_context
- [x] `NEXUS_API_KEY` provisioned + poller `--once` command handling (2/2)
- [x] Real Vercel prod URL
- [x] Completion patches committed (`3f4b7af`)
- [ ] wt planning pointer (OpenClaw packet — separate repo)

### Poller test (closure round)

```bash
# Key from runtime file (never commit):
export NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$HOME/.openclaw/runtime/nexus-satellite-api-keys.json'))['civforge-kernel']['apiKey'])")"
export NEXUS_URL=http://127.0.0.1:8082
python3 tools/nexus_command_poller.py --once
```

Observed: `polled: 2`, `processed: 2` — restart `blocked_by_canon`; sync_config proposed (`proposal_id=747989fa`).

### Dashboard

- **Local (works now):** http://127.0.0.1:8080/dashboard
- **Vercel (remote shell):** https://civforge.vercel.app — setup panel; tunnel via `?api_base=https://…`

---

## Out of scope / later

- Auth-prototype `:8081` for product identity (Phase D)
- Sister SIS-NEXUS-B: ack/complete API-key auth; control proxy reject for `governance_kernel`
- wt `CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` pointer commit

---

## Quick validation (Mac Studio)

```bash
curl -sf http://127.0.0.1:8080/state | head -c 120
curl -sf http://127.0.0.1:8082/api/health
open http://127.0.0.1:8080/dashboard
curl -sf -X POST http://127.0.0.1:8080/simulation/what_if -H 'Content-Type: application/json' -d '{"investment":5}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('fun_impact_estimate'), 'fallback' not in str(d.get('nexus_context','')))"
```

---

## Multi-Agent UI (WP-UI-MULTI-AGENT-EXTENSION) — `current`

Implemented in code (not receipt-only):

| Layer | Path |
|-------|------|
| State engine | `backend/multi_agent_state.py` |
| API | `backend/sim_api.py` — `/state`, `/game/negotiate`, `/game/negotiate/respond` |
| Dashboard | `frontend/index.html` — tabs, map, negotiation, alliances, victory |

**Open:** http://127.0.0.1:8080/dashboard

