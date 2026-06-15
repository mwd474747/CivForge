# HANDOFF — Grok Swarm (CivForge complete state)

**Date:** 2026-06-15 (lane v2 aligned)
**Lane model:** `docs/EXECUTION_LANE_V2.md` — **you plan on grok.com; Cursor executes; OpenClaw escalates only**
**Local Grok terminal:** **removed** — no `.grok/config.toml`, no Mac Studio Grok CLI
**Handoff seed:** `prompts/grok_swarm_handoff_seed.md`
**CivForge HEAD:** `201169f`+ (Cursor commits)
**OpenClaw WP-001:** **Done**

---

## 1. Executive verdict

CivForge is **playable and cross-plane integrated** on this Mac Studio:

| Plane | Status |
|-------|--------|
| Kernel `:8080` | Live — multi-agent dashboard, mechanics, CivStudy sim |
| Nexus `:8082` | Healthy — `civforge-kernel` registered, telemetry push |
| wt probes | `pass` @ `2026-06-15T17:49:12Z` (`7/7` integration, fleet `100`) |
| Vercel shell | `https://civforge.vercel.app` — redeploy approved (see §6) |
| Poller daemon | **Cursor** (or Mike) — `bash tools/start-poller-daemon.sh` |

**Do not rebuild the dashboard.** Extensions only.

---

## 2. What landed (commit chain)

| Commit | Content |
|--------|---------|
| `227da70` | Multi-agent UI, mechanics registry, MCP, docker-compose |
| `0d44eb4` | Review hardening: DB volume, negotiation IDs, victory sync, pytest |
| `f5031ba`–`025` | Honest swarm correction receipts (020/021/024/025) |
| `cc80db3` | CivStudy metadata D+E (districts, policy_tree, forks, chains) |
| `58246de` | Turnkey Grok/OpenClaw packets + CivStudy mechanics sim bridge |

---

## 3. Live surfaces (verify before any PRIME receipt)

```bash
cd ~/CivForge
git pull origin main
bash tools/start-kernel-8080.sh
bash tools/turnkey-cursor-local.sh --advances 3
```

| Surface | URL / command |
|---------|----------------|
| Local play | http://127.0.0.1:8080/dashboard |
| Remote play | https://civforge.vercel.app?api_base=<HTTPS_TUNNEL_TO_8080> |
| State API | `GET /state` — map, alliances, negotiations, `civstudy_sim`, `victory_progress` |
| MCP | 8 tools via `python3 tools/mcp_server.py` (incl. governance propose/gate) |

**Forbidden verify:** `python3 tools/civforge_cli.py status | grep vercel` (always 0 matches).

---

## 4. CivStudy ↔ mechanics (simulation hooks)

Read-only metadata in `civstudy_reference`; **live sim** in `civstudy_sim`:

- **District pulse** — `Governance Quarter` yield every 3 turns
- **Discovery forks** — unlock when prereqs met (`legacy-doctrine`, `sci-trade-route`, etc.)
- **Cultural chains** — stage progress every 6 turns

Code: `backend/civstudy_mechanics_bridge.py` → registered in `core/mechanics_registry.py`.

Tests: `tests/test_civstudy_mechanics_bridge.py`.

---

## 5. OpenClaw closure (WP-OPENCLAW-CIVFORGE-OPS-001)

| Step | Status |
|------|--------|
| Kernel verify | Done |
| Nexus + key | Done |
| Poller `--once` | Done (`polled=0`) |
| Poller **daemon** | OpenClaw executing |
| wt registry | Done — `engine-src/active/config/ops/governed-connectors-registry.v1.json` |
| wt boundary | Done — pointer-only mirror (correct; no overwrite) |
| wt receipts | Done @ `2026-06-15T17:49:12Z` |

Receipt: `receipts/openclaw-ops-run-20260615-134711.md`
wt memory: `~/.openclaw/dawsos-workspace-wt/memory/2026-06-15.md` §13:42–13:52 EDT

**CivForge receipts ≠ dawsOS promotion truth.**

---

## 6. Vercel redeploy (approved)

After pull, from CivForge root:

```bash
cd ~/CivForge && vercel --prod
```

Ships win overlay + latest `frontend/index.html` from `58246de`.

**Deployed 2026-06-15:** Production alias https://civforge.vercel.app
Deployment: `dpl_DMAdbh4vUNwGLZQ8WqEBMYSEW2CE` (Vercel CLI `npx vercel --prod --yes`)

---

## 7. Grok default next lane (only these)

Work pack: `receipts/work-pack-grok-mechanics-sim-001.md`

| Priority | Item | Lane |
|----------|------|------|
| 1 | Policy-tree tier effects on district pulse | `lane/civ-game-mechanics` |
| 2 | Negotiation backlog sweep | `tools/negotiation-sweep.sh` or MCP respond loop |
| 3 | Git worktrees per `docs/GIT_LANES_POLICY.md` | parallel tracks |
| 4 | `:8081` JWT for `protected_advance` | `lane/infra-required` |

**Not Grok default:** UI rebuild, fake commit hashes, FunForge 100 without live `/state`.

---

## 8. MCP tool catalog

| Tool | Endpoint |
|------|----------|
| `civforge_status` | `GET /state` |
| `civforge_advance_turn` | `POST /advance_turn` |
| `civforge_found_city` | `POST /found_city` |
| `civforge_negotiate` | `POST /game/negotiate` |
| `civforge_negotiate_respond` | `POST /game/negotiate/respond` |
| `civforge_what_if` | `POST /simulation/what_if` |
| `civforge_governance_propose` | `POST /governance/propose` |
| `civforge_governance_gate` | `POST /governance/gate` |

---

## 9. Swarm receipt rules (locked)

1. Cite real `git rev-parse --short HEAD` on `main`
2. Cite probe output — `bash tools/validate-game.sh`, not narrative
3. Tag stale over-claims explicitly
4. `fun_score` from live `/state` only (currently ~86.6, not 100)
5. UI claims: dashboard curl or `GET /dashboard`, never grep vercel on CLI status

---

## 10. Canonical docs

| Doc | Purpose |
|-----|---------|
| `docs/GROK_SWARM_PACKET_V1.md` | Grok verify + forbidden patterns |
| `docs/OPENCLAW_OPS_PACKET_V1.md` | OpenClaw ops checklist |
| `docs/OPENCLAW_WT_APPLY_PACKET_V1.md` | wt mirror (pointer-first; `config/ops/` registry) |
| `docs/GAME_PLAY_GUIDE_V1.md` | Human play guide |
| `AGENTS.md` | Swarm truth plane lock |

---

## 11. Prompt seed for other Grok

> CivForge lane v2: Grok swarm on grok.com plans work packs; Cursor executes on Mac Studio; OpenClaw only for wt escalation. No local Grok terminal. Read `docs/EXECUTION_LANE_V2.md` + this handoff. Require Cursor execution receipt before closing PRIME. Default lane: policy-tree mechanics — no UI rebuild.

---

_Generated after OpenClaw WP-001 closure review. Cursor partner lane — patches not dawsOS promotion truth._
