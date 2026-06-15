# Receipt: SWARM-ALIGNMENT-INGEST-020 — Continuation & Truth Correction

**Work Pack IDs:** WP-ALIGNMENT-INGEST-AND-VERIFY-020, WP-BACKEND-TRUTH-ALIGN-20260614  
**Date:** 2026-06-15  
**Author:** Cursor partner lane (Mike-approved continuation)  
**Status:** `current` — corrects Grok swarm under-claims; does not grant dawsOS promotion authority  
**Commit anchor:** `0d44eb4` (`main`, pushed to https://github.com/mwd474747/CivForge)

**Supersedes (partial):** Grok swarm receipt narrative that claimed “dashboard = basic stub only” and “Vercel = config stub only.” Those lines are **retracted** below.

---

## 1. Purpose

Ingest the backend alignment brief at `0d44eb4`, validate WP-ALIGNMENT-INGEST-AND-VERIFY-020, and lock **Mac Studio execution truth** for the Grok swarm without narrative drift in either direction:

- **Prior drift (over-claim):** Receipts claiming rich UI without `frontend/index.html` changes.
- **This receipt’s correction (under-claim):** Swarm brief that retired dashboard/Vercel after alignment — **incorrect**; both are landed in tree.

---

## 2. Literal verification (performed 2026-06-15)

```bash
cd ~/CivForge
git rev-parse --short HEAD                    # → 0d44eb4
wc -l frontend/index.html                     # → 426 lines
curl -sf http://127.0.0.1:8080/state          # → active, turn 52, fun 86.6, 25 map_tiles
curl -sf http://127.0.0.1:8080/dashboard | grep -c 'Multi-Agent Command'  # → 1
curl -sf http://127.0.0.1:8082/api/health     # → {"status":"ok",...}
curl -sf -o /dev/null -w '%{http_code}' https://civforge.vercel.app/  # → 200
curl -sf https://civforge.vercel.app/ | grep -o 'Multi-Agent Command' # → match
bash tools/validate-game.sh                   # → PASSED (pytest 4/4 + API + turnkey)
```

| Claim | Swarm receipt (020) | Actual tree (`current`) |
|-------|---------------------|-------------------------|
| Commit anchor | 0d44eb4 | ✅ Match |
| 8080 kernel live | ✅ | ✅ turn 52, status active |
| Multi-agent `/state` | ✅ (API only) | ✅ map, alliances, negotiations, victory, mechanics_lanes |
| 8082 thin bridge | “pending bootstrap” | ✅ `/api/health` ok locally; poller + telemetry wired |
| Dashboard | ❌ “basic stub only” | ✅ **426-line multi-agent SPA** at `GET /dashboard` |
| Vercel | ❌ “config stub only” | ✅ **https://civforge.vercel.app** serves same HTML (200) |
| Rich UI in tree | ❌ “minimal stubs / grep wc -l” | ✅ agent tabs, map, negotiate, alliances, victory, view tabs |
| Receipt file in repo | claimed logged | ❌ original `swarm-alignment-ingest-020-20260614.md` **not in tree** — this file is the correction |

---

## 3. Locked execution truth (Grok swarm must use)

### 3.1 What CivForge is

- **Governed FastAPI kernel** on `:8080` (`backend/sim_api.py` + `core/`).
- **Civ metaphor** for work packs, attention budgets, FunForge quality, multi-agent diplomacy.
- **Separate** from gravity-mosaic (deploy only via `tools/deploy-gravity-mosaic/deploy.sh`) and from dawsOS wt promotion truth.

### 3.2 Core loop (8080-gated)

1. `GET /state` — canonical read (never assume without curl).
2. `POST /advance_turn` — orchestrator + multi-agent tick + mechanics tick + persist + Nexus telemetry.
3. `POST /found_city`, `POST /game/negotiate`, `POST /game/negotiate/respond` — game actions.
4. `POST /governance/propose` + `/governance/gate` — gravity work proposals.
5. Nexus commands via `tools/nexus_command_poller.py` → **propose only**, never direct execute.

### 3.3 Dashboard & Vercel (do not under-claim)

| Surface | Truth |
|---------|-------|
| **Local play** | http://127.0.0.1:8080/dashboard — same-origin, full multi-agent UI |
| **Remote shell** | https://civforge.vercel.app — static `frontend/index.html`; live kernel requires HTTPS tunnel via `?api_base=` or setup panel |
| **Source** | `frontend/index.html` (not a stub); served by `GET /dashboard` in `sim_api.py` |

Swarm must **not** schedule “build rich dashboard from scratch.” Extensions only (mechanics, metadata, juice).

### 3.4 Backend surfaces available today

- **Multi-agent:** `backend/multi_agent_state.py` — map 5×5, alliances, negotiations (sequenced IDs), victory milestones (sync at 100%).
- **Mechanics:** `core/mechanics_registry.py` — military / economic / cultural lanes on advance.
- **MCP:** 6 tools via `tools/mcp_server.py` (`civforge_status`, `advance_turn`, `found_city`, `negotiate`, `negotiate_respond`, `what_if`).
- **CLI:** `tools/civforge_cli.py` — status, advance, found, propose-deploy, gate, mcp-serve, nexus-poll.
- **Validation:** `bash tools/validate-game.sh [--restart]`.
- **Docs:** `docs/GAME_PLAY_GUIDE_V1.md`, `docs/CIVFORGE_COMPLETION_CHECKLIST_V1.md`.

### 3.5 Boundaries (unchanged)

- No CivForge → dawsOS wt promotion claims.
- No direct gravity-mosaic mutation from CivForge code.
- No Nexus command → direct `advance_turn` / `found_city` without FunForge gate.
- `:8081` JWT identity — future; not product auth today.
- Live civstudy corpus — reference panel only (`civstudy_reference` in `/state`).

---

## 4. WP-ALIGNMENT-INGEST-AND-VERIFY-020 disposition

| Section | Verdict |
|---------|---------|
| Backend API alignment | **PASS** |
| Separation / 8080-gated loop | **PASS** |
| UI / Vercel truth | **FAIL** — swarm over-corrected; corrected in §3.3 |
| Receipt hygiene | **PARTIAL** — original 020 file absent from repo; this continuation lands truth |
| “100% aligned • no assumptions” | **REJECTED** — UI/Vercel assumptions were inverted |

**RIME label:** `current` for backend + live probes; `prototype-only` for any future mechanics/CivStudy extensions until re-validated.

---

## 5. Governed next steps (swarm routing)

**Do not repeat:** rebuild dashboard, claim Vercel unimplemented, or conflate with dawsOS wt.

**Approved lanes:**

| Priority | Work | Lane |
|----------|------|------|
| 1 | `bash tools/validate-game.sh --restart` before closure claims | ops |
| 2 | Mechanics registry extension (new tick modules) | mechanics |
| 3 | CivStudy metadata additions (read-only reference; no corpus mutation) | metadata |
| 4 | 8082 poller receipt + `sync_config` proposal flow | thin-bridge |
| 5 | MCP tools for `/governance/propose` + `/gate` (optional) | agent-play |

**Mike ignition mapping (from swarm menu):**

- **A** — Advance kernel/metadata/8082 prep ✅ (skip UI rebuild)
- **B** — 8082 verify ✅ (already `ok`; run poller `--once` for receipt)
- **C** — OpenClaw handoff + Draft PR ✅ if PR states **actual** UI+Vercel+backend
- **D** — Mechanics + CivStudy metadata ✅ **recommended next slice**
- **E** — `validate-game.sh` + N advances + this receipt ✅ **executed via this artifact**

---

## 6. References

- Alignment brief source: Cursor session → commit `0d44eb4`
- `docs/GAME_PLAY_GUIDE_V1.md`
- `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`
- `SEPARATION.md`
- Prior handoff: `receipts/HANDOFF-GROK-SWARM-BACKEND-20260614.md` (partially stale on UI — prefer this receipt)

---

**Fun/quality note:** Backend alignment is high; closure requires honest UI/Vercel claims. No FunForge 100.0 score asserted here — use live `/state` fun_score (~86.6) as observable metric.

**End of receipt.**
