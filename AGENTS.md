# AGENTS.md - CivForge Agentic Architecture

**This folder (CivForge) is home for governed agentic work on separate projects.**

## Execution lanes (canonical — `docs/EXECUTION_LANE_V2.md`)

| Lane | Runtime | Role |
|------|---------|------|
| **Grok swarm** | grok.com | Planning, work packs, PRIME criteria — **no Mac Studio terminal** |
| **Cursor** | Cursor IDE | **All local execution** — code, kernel, tests, CivForge git, vercel |
| **OpenClaw** | wt / escalation | dawsOS promotion, boundary apply, C2 — **only when triggered** |

**Removed (2026-06-15):** Local Grok terminal (`.grok/config.toml`, `grok_macstudio_bridge.py`, ForgeMaster local executor).

---

## Bootstrap (every session)

1. Read `SEPARATION.md`, `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`, and `docs/CIVFORGE_SWARM_CLASS_V1.md`
2. Read `docs/EXECUTION_LANE_V2.md` — know your lane (CivForge ≠ dawsOS `swarm-registry` class)
3. Read `receipts/HANDOFF-GROK-SWARM-20260615.md` for current state
4. Grok swarm: `prompts/grok_swarm_handoff_seed.md`
5. Cursor: run `bash tools/turnkey-cursor-local.sh` after implementation
6. Swarm alignment receipts 020/021/024/025 — truth plane lock
7. Confirm `:8080` kernel, `:8082` Nexus (telemetry), `:8081` auth (optional)

**Write it down:** receipts/ and execution receipts. No mental notes.

---

## Grok swarm (grok.com — planning only)

- Authors `WP-*` work packs and roadmap priority
- PRIME receipts = **planning class**; must link Cursor execution receipt + real `git HEAD`
- Does **not** run terminal, commit, or claim local execution
- In-game personas (Harper, Sebastian, etc.) are simulation roles in `:8080` — not local agents

Handoff: `prompts/grok_swarm_handoff_seed.md`, `docs/GROK_SWARM_PACKET_V1.md`

---

## Cursor (local executor)

- Implements all CivForge source, tests, docs (lane-aligned)
- Runs kernel (`tools/start-kernel-8080.sh`), poller, vercel (when Mike approves)
- CivForge `git commit` / `push` to `main`
- Writes `receipts/cursor-execution-*.md` with probe literals
- Uses `bridge/civforge_http_bridge.py`, `tools/civforge_cli.py`, GitNexus impact before edits
- Does **not** wt commit/C2/storage apply/LaunchAgents (escalate via `docs/OPENCLAW_ESCALATION_PACKET_V1.md`)

---

## OpenClaw (escalation only)

- wt `reports/ops/*` = promotion truth (not CivForge receipts)
- Trigger: boundary menu, C2, projection blockers, scheduled cron
- CivForge bridge closed at WP-001 — no routine CivForge ops

---

## Swarm class (important)

CivForge borrows dawsOS **governance patterns** but is **not** a wt-registered workflow swarm. Grok on grok.com plans; AgentBrains simulate in `:8080`; OpenClaw owns wt truth on escalation only. See `docs/CIVFORGE_SWARM_CLASS_V1.md`.

---

## In-game agent registry (`agents/role_registry.json`)

Simulation personas in `core/` governance cycles (Layer 2 — not grok.com swarm, not wt delegates):

- **harper** — memory, research, verify
- **sebastian** — FunForge gate, separation, literal verify
- **game-mechanic-designer**, **player-agent**, **mechanics-simulator**, **ui-coordinator**, **infra-governor** — lane specialists (Grok plans → Cursor implements)

---

## Orchestration patterns

1. Receipt-first loop — propose, gate, advance → `receipts/*.md` + SQLite
2. FunForge ≥80 gate for gravity/meta work
3. `POST /advance_turn` — AgentBrains → FunForge → gate
4. Gravity **only** via `tools/deploy-gravity-mosaic/deploy.sh`
5. Separation + literal hygiene before every edit

**Kernel truth:** `backend/sim_api.py` + `core/` on `:8080`. Drivers: `civforge_cli.py`, `civforge_http_bridge.py`, MCP server.

---

## Current reality (2026-06-15)

- Dashboard **landed** — `GET /dashboard`, https://civforge.vercel.app — extend, do not rebuild
- CivStudy metadata + mechanics sim bridge live (`civstudy_sim` in `/state`)
- MCP: 8 tools including governance propose/gate
- Verify: `bash tools/validate-game.sh` — never `civforge_cli.py status | grep vercel`
- Git lanes: `docs/GIT_LANES_POLICY.md`
- OpenClaw WP-001 **Done** — Nexus bridge, wt probes pass

Update this file via governed work pack + Cursor execution receipt.
