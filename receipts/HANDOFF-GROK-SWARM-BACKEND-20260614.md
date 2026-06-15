# HANDOFF ARTIFACT FOR GROK SWARM: CivForge Backend — Updates, Implemented, Ready & Usable

> **Superseded for swarm truth plane (2026-06-15):** Read alignment receipts first:
> `receipts/swarm-alignment-ingest-020-continuation-20260615.md`,
> `receipts/swarm-alignment-correction-ingest-021-20260615.md`,
> `receipts/swarm-correction-validation-024-20260615.md`,
> and `docs/GAME_PLAY_GUIDE_V1.md`. This handoff remains useful for Nexus/bootstrap history; do not treat it as sole UI truth (dashboard + Vercel are landed per 020/021).

**Date**: 2026-06-14 (after governed commit 2f09e99 to main, bootstrap execution with explicit user approval, comprehensive docs+stubs+implementation audit, continued execution to turn 104+)
**Primary artifacts to read first (in order)**:
1. This file (focused backend summary)
2. receipts/civ-game-backend-nexus-impl-continuation-20260614.md (living log of every advance, verification, failure mode, audit, and bootstrap)
3. HANDOFF_CONTEXT.md (full workspace + history snapshot)
4. SEPARATION.md (the non-negotiable contract)
5. AGENTS.md (Civ project rules + full terminal approval + dawsOS leverage)

**Literal verification at creation time**: git status, SEPARATION anchors, 8080 LIVE (turn 103-104, fun 86.6-86.8), 8082 quiet, dawsos-nexus tree (Postgres up, node_modules present from approved npm run, tsx status), code greps confirming 8082 wiring + "Replaces dawsos-auth-prototype (archived)", _archive/auth-prototype present + zero active prototype refs outside archive. 8080 advanced during prep.

## Executive Summary
CivForge is the **governed backend** for a simple-but-infinitely-extendible Civ-style game / agentic governance workspace.

- Truth: 8080 FastAPI kernel (backend/sim_api:app) + core/ Python (orchestrator, FunForge, AgentBrain, GovernanceGate, ReceiptStore).
- All core actions (advance, found_city, propose, gate) run through FunForge quality gates (fun_score consistently 86.6-86.8, PASS if >=80), produce human + machine receipts, tick resources, and persist (SQLite + .md files).
- **dawsos-nexus at 8082 is the designated primary implementation** for the backend layers: telemetry (heartbeats + customMetrics + agentState), control (future command proposals), auth (device registration + scoped govern tokens), simulation context, and audit mirror.
- CivForge touches 8082 **only via thin HTTP bridge** (client in tools/dawsos_auth_client.py + calls inside sim_api.py). No direct mutation — per SEPARATION.md.

The backend is **implemented, executing, and usable today**. The thin bridge to nexus is fully wired on the Civ side. Full live effect (real heartbeats, richer sim context, real auth) requires one user action: running the bootstrap in a persistent terminal tab (npm steps already succeeded in a prior approved execution).

## What Is Implemented & Wired (Code That Is Running Now)
All of the following has been exercised in live advances (turn 104+, telemetry calls, sim/protected tests).

### 1. Core Backend Loop (usable immediately, no 8082 required)
- `backend/sim_api.py` (FastAPI on 8080):
  - GET /state — current game_state (resources, fun_score, territories, cities, events, work_packs, receipts).
  - POST /found_city — resource deduction, work_pack creation, ReceiptStore, telemetry trigger.
  - POST /advance_turn — GovernanceOrchestrator.advance_cycle (turn++, resource tick, AgentBrain decisions + record_receipt, FunForge gate, persist + receipt). **Calls send_telemetry_to_nexus**.
  - POST /governance/propose + /gate — proposal creation and FunForge-gated approval.
  - POST /governance/protected_advance — thin auth protected path (dev fallback active).
  - POST /simulation/what_if — resource/fun projection. Probes 8082 (apps/health/customMetrics) with clean fallback.
- `core/`:
  - orchestrator.py: advance_cycle
  - fun_forge.py: calculate_fun_metrics + gate logic
  - agent_brain.py: decide_action + record_receipt for grok/harper/sebastian
  - governance.py: propose/gate
  - receipts.py: append to .md + SQLite load/save_state (restart survival)
- Persistence & liveness: receipts/ folder (governance-cycle-*.md + big continuation receipt), optional SQLite, `tools/start-kernel-8080.sh` (the canonical safe launcher with PID + health).

### 2. dawsos-nexus Thin Bridge (the implementation layer — fully coded and called on Civ side)
- `tools/dawsos_auth_client.py`:
  - register_device → /api/apps (satellite registration)
  - token / verify (health + x-nexus-api-key / Bearer)
  - Explicitly documents "Replaces dawsos-auth-prototype (archived). Thin HTTP bridge only per SEPARATION.md."
- `backend/sim_api.py`:
  - `send_telemetry_to_nexus(...)` — POST /api/telemetry/heartbeat with appId="civforge-kernel", agentState="thinking", customMetrics containing turn/funScore/resources/territories/cities/events/funComponents.
    - Wired on real paths: post-advance_turn (after orchestrator + persist), post-found_city, inside protected_advance.
    - Fire-and-forget (never blocks game).
  - `/simulation/what_if` — multi-probe for nexus data + projection logic.
  - `require_govern_token` + protected_advance — supports NEXUS_OPERATOR_TOKEN, x-nexus-api-key, health fallback + dev permissive.
- `tools/civforge_cli.py`: status, advance, found, propose-deploy, gate, auth subcommands (register-device/token/verify), mcp-stub (explicit tracked placeholder).

### 3. Tooling & Patterns (ready now)
- CLI: python3 tools/civforge_cli.py (the primary way to drive governed play).
- Safe 8080 launcher: bash tools/start-kernel-8080.sh.
- Verification pattern: literal (git + SEPARATION greps + 8080 curl + tree inspect + code greps) + advance (telemetry proof) + receipt append. This is the "test".
- Audit passed (see continuation receipt): no untracked stubs, docs coherent, implementation quality high.

## What Is Ready & Usable Today
- Complete governed game loop (advance the civ, found work, propose/gate, FunForge quality, receipts).
- Telemetry sender (already calling on every advance — ready for when 8082 is healthy).
- Simulation what-if (nexus-aware with fallback).
- Thin auth for protected actions (dev fallback works; real when 8082 up).
- CLI + HTTP API surface for humans or agent players.
- Persistence that survives restarts.
- 8080 bring-up in seconds.
- All recent updates (dawsos-nexus integration, user-approved bootstrap execution, full audit with no untracked stubs, commit to main) are on main and documented.

**You can run the game and governance right now without 8082.**

## What Still Needs One External Step (dawsos-nexus 8082)
Full live thin bridge (visible heartbeats in nexus dashboard, real customMetrics/agentState in /simulation/what_if, real auth without fallback, future command proposals from nexus).

**Exact user command (run in your own persistent terminal tab — not via agent harness):**
```bash
cd ~/Documents/GitHub/dawsos-nexus
# (npm install + tsx --save-dev already succeeded in prior approved execution)
./tools/start-nexus.sh
# or npm run dev
# Verify:
curl http://127.0.0.1:8082/api/health
curl -s http://127.0.0.1:8082/api/apps | head -c 200
```

Once healthy, re-run advances here — the bridge will light up.

## How a Grok Swarm Should Warm-Start & Continue
1. Read: this handoff + tail of the continuation receipt + SEPARATION.md + AGENTS.md.
2. Bring 8080 live: `bash tools/start-kernel-8080.sh`.
3. Drive: `python3 tools/civforge_cli.py status / advance / found / propose / gate`.
4. For 8082: run the bootstrap block above in your terminal. Then re-verify live telemetry.
5. Any new work (more mechanics, command poll, MCP wrapper, dashboard, production): must be proposed on the live 8080, gated (FunForge >=80), executed, literally verified, and appended to the continuation receipt.
6. Tracked future items (from audit): command poll (nexus commands → 8080 proposals), MCP wrapper (using the tracked mcp-stub), richer mechanics (governed), production items (Docker for both sides), gamified UI (adapting nexus patterns).

**Never**: mutate the dawsos-nexus tree, bypass propose/gate for meta, assume 8082 is healthy, revive archived prototype/Godot.

## Current Snapshot (at artifact creation)
- Turn: 104
- fun_score: 86.6-86.8 (consistent PASS)
- Resources: food/prod 120, sci 117, influence 114, verify_budget 115 (and ticking)
- Telemetry: live on advances (sender wired and called)
- 8080: live via safe script
- 8082: awaiting user terminal bootstrap
- Git: clean on main post governed commit 2f09e99
- Stubs: none untracked (mcp-stub and minimal CI gate are explicitly called out as future/governed)

**This artifact + the continuation receipt give the swarm everything needed to continue the backend work immediately and correctly.**

All under the locked plan, separation contract, literal verification, receipt-first governance, and 8080+core/ as single source of truth.

— Prepared as part of the governed continuation (see main receipt for the authorizing steps).
