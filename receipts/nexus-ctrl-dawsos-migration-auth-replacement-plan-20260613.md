# Receipt: NEXUS-CTRL-DAWSOS-MIGRATION-AUTH-REPLACEMENT-PLAN-20260613

**Work Pack ID**: WP-NEXUS-CTRL-MIGRATION-001  
**Status**: DRAFT PLAN SAVED — For OpenClaw Main Agent Review (Governed via 8080)  
**Fun/Quality Score**: 94 (high alignment to Replit removal goal, local Mac Studio deployment, dawsOS infrastructure leverage via control plane, and CivForge auth/control needs; extends prior receipts with concrete steps)  
**Date**: 2026-06-13  
**Primary Hat**: CivForge (governance layer, 8080 kernel truth, receipt-first, separation)  
**Secondary Hat**: dawsOS useful infrastructure (RIME patterns, gitnexus, memory tools, control plane for agents/cron)

## Literal Verification Performed (per AGENTS.md Bootstrap + SEPARATION.md + dawsOS patterns)
- Read SEPARATION.md: Confirmed "Gravity-mosaic-knowledge-graph and CivForge are two completely separate projects." + "CivForge never directly mutates" targets except via sacred bridges (deploy.sh for gravity, thin client for auth). nexus_ctrl treated as external private reference (read-only, like civstudy).
- Read AGENTS.md: "Civ Project Configuration" section active (full terminal approval + dawsOS MCP leverage: gitnexus for impact, dawsos-memory-tools for receipts, trivium for governance). Bootstrap: literal verification first (git status, wc/grep anchors, SEPARATION, receipts).
- Read recent receipts: CIVSTUDY-TERMINAL-GIT-REVIEW-20260613-160534.md (nexus patterns from civstudy), civ-project-dawsos-full-approval-config-20260613-211500.md (terminal + dawsOS tools formalization), review-civstudy-proposal-*.md, and swarm proposals (WP-NEXUS-CTRL-DEEP-REVIEW-002, WP-NEXUS-CTRL-AUTH-REVIEW-REPLACE-001).
- Git status + hygiene: Changes tracked (prior meta). No nexus_ctrl source in tree outside receipts (grep confirmed none in .py/.md outside receipts/). 8080 LIVE (via curl /state + CLI status).
- Fresh terminal review of nexus_ctrl (gh clone mwd474747/nexus_ctrl to /tmp, literal ls/cat/grep/wc on replit.md, server/, client/src/lib/nexus-connector-template.ts, schema, then rm -rf): "Nexus Mission Control" — Replit TS app with control plane (Pause/Resume/Emergency Stop, command queue, webhooks, audit_logs), telemetry (heartbeats + custom metrics), agent states (idle/thinking/tool_use), connector template for CivStudy, reference_apps/civstudy, attached Nexus plans. Auth elements: users table, apiKey in connector (lighter than full JWT/device).
- Verification commands: git status --porcelain, grep for anchors ("separate projects", "literal verification", "FunForge >=80"), wc -l on key files, gh repo view + clone, curl 8080/state, python CLI status, grep for nexus outside receipts.
- dawsos-auth-prototype state: Confirmed separate (~/Documents/GitHub/dawsos-auth-prototype, 8081, thin client in tools/dawsos_auth_client.py, PyJWT + device/token/"govern" scopes protecting protected_advance).

**Write It Down discipline**: This receipt is the canonical saved draft plan for openclaw main agent (and cross-workspace handoff via HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md). All future actions on this plan must be 8080-proposed, FunForge-gated, receipted, with literal verification.

## Goal (User Separate Goal)
Remove all Replit deployments. Deploy locally on Mac Studio, **including nexus_ctrl**.

- Factor nexus_ctrl optimally into dawsOS as useful infrastructure (central control plane / "Mission Control" layer for telemetry, commands, audit, agent coordination — pairs with gitnexus, memory tools, trivium, cron).
- Extend it to be usable for CivForge authentication needs (device/agent identity, scoped tokens like "govern", protected governance actions).
- **Specifically**: Remove the recently added dawsos-auth-prototype (separate at 8081) in favour of extending nexus_ctrl to cover full auth functions, while maintaining separation (CivForge uses thin HTTP bridge only; no direct mutation of targets).

This is governed meta-work: Propose on live 8080, FunForge gate (>=80), receipt, literal verify before/after edits. Respect SEPARATION.md (nexus_ctrl as external reference; auth-prototype as sister root until migrated).

## Current State (Verified)
- **nexus_ctrl** (https://github.com/mwd474747/nexus_ctrl.git, private reference): Replit TS app "Nexus Mission Control". Centralized dashboard + control plane for satellite apps.
  - Control Plane: Pause/Resume/Emergency Stop, command queue (Nexus→apps with status), webhooks, persistent alerts (ack/resolve), full audit_logs for governance.
  - Telemetry: Heartbeats (push) + polling (pull /api/automation/metrics). Agent states (idle/thinking/tool_use). Custom metrics (e.g. corpusCardCount, automationTasksCompleted, apiCostToday).
  - UI: React/TS + Tailwind (Nexus dark) + shadcn/ui + Recharts + Framer Motion. Real-time polling, control toasts.
  - Backend: Express/TS + Drizzle + Postgres. Schema (shared/schema.ts): users (auth), apps, heartbeats, logs, alerts, commands, webhooks, audit_logs, app_operational_modes.
  - Standout: client/src/lib/nexus-connector-template.ts (explicit "NEXUS CONNECTOR FOR CIVSTUDY" — heartbeat, states, metrics; drop-in for satellites).
  - reference_apps/civstudy/ + attached_assets (Nexus integration plans from prior civstudy review).
  - Auth in it: users table + apiKey in connector (basic; extensible for roles/permissions).
  - Current: Replit-deployed ( .replit, vite+tsx, docker-compose in family).
- **dawsos-auth-prototype** (recently added, separate): PyJWT + SQLite at 8081 (~/Documents/GitHub/dawsos-auth-prototype). Device/agent registration, /token with scopes ("govern"), /verify. Thin client in CivForge/tools/dawsos_auth_client.py + tools/auth-prototype/ bridge + CLI auth subcommands. Protects /governance/protected_advance. Working, minimal, separated (sister root per SEPARATION).
- **CivForge** (governance layer): 8080 kernel (GovernanceOrchestrator.advance_cycle, FunForge, AgentBrain, ReceiptStore, protected_advance with Depends on token). Full terminal approval + dawsOS MCP leverage (gitnexus, memory, trivium) formalized. Receipts, AGENTS.md, role_registry (with dawsos-mcp-leverage), Git lanes, etc. Current auth bridge to 8081 prototype.
- **dawsOS workspace** (.openclaw/dawsos-workspace-wt): Engine, cron-host/review, gitnexus (graph + impact + audits), memory tools, trivium, nexus-graph symlink, LOCAL_*_REGISTRIES, receipts. No direct nexus_ctrl source (only gitnexus tooling + references). Strong RIME (Receipts/Identity/Metadata/Execution) patterns.
- **Separation & Hygiene**: Three projects + external references (gravity, civstudy, nexus_ctrl). CivForge touches via bridges (deploy.sh, thin auth client) or read-only reference. No cross-contamination. Prior reviews (civstudy, nexus_ctrl) receipted and 8080-gated.

**8080 + CLI Health**: LIVE (turn 1, fun 87, active). CLI status/auth commands responsive.

## Draft Plan: Remove Replit, Deploy Locally on Mac Studio (Including nexus_ctrl)

### 1. Local Deploy of nexus_ctrl (Mac Studio, Remove Replit)
- Clone/reference locally (already accessible via gh; keep in ~/Documents/GitHub/nexus_ctrl or dawsOS workspace as separate project).
- Database: Use local Postgres (or Docker Compose service with postgres:15 + volume). Run `npx drizzle-kit push` (adapt from existing docker-compose.yml).
- Environment: .env for secrets (NEXUS_URL, API keys, DB). Mirror patterns from auth-prototype + CivForge kernel.
- Run locally:
  - Backend: `tsx server/index.ts` (or `npm run start` post-build).
  - Frontend: `vite dev --port 5000` (or production).
  - Or Docker: Adapt docker-compose.yml for local (node service + postgres). Expose ports (e.g. 3000 API, 5000 UI). Use nohup + PID like tools/start-kernel-8080.sh.
- Create `tools/start-nexus-ctrl.sh` (or centralize in dawsOS): DB push, start backend/frontend, health check (e.g. curl /health or equivalent).
- Process management: nohup + PID file + log. Add to Mac Studio startup if desired (launchd or similar).
- Remove Replit artifacts: Delete .replit, update scripts/vite for local-only (commit as governed change).
- Verification: Literal reads (wc -l replit.md/server files), test connector against satellite (e.g. local CivForge agent or civstudy ref), 8080 propose if impacting CivForge.

**Timeline**: 1-2 days for core local run. Use existing terminal approval.

### 2. Factor nexus_ctrl into dawsOS as Useful Infrastructure
- **Positioning**: Central "Nexus Mission Control" control plane / observability layer on top of dawsOS stack.
  - Base: gitnexus (graph + impact + audits), dawsos-memory-tools (receipts/profiles), trivium (governance_health, predictions), cron-host/review, engine-src, memory/.
  - nexus_ctrl on top: Ingest telemetry from all "satellites" (cron, agents, workspaces, CivForge 8080 via connector). Unified command plane (dispatch to components), dashboard for health/states/control, audit as governance layer.
- **RIME Alignment** (Receipts/Identity/Metadata/Execution): 
  - Receipts: audit_logs + command status feed directly into ReceiptStore / dawsOS receipts.
  - Identity: Extend users/apps with roles/permissions (map to CivEntityMetadata + governor roles).
  - Metadata: apps table + operational modes for entity sync (workstreams/civs as "apps").
  - Execution: Command queue + webhooks for governed actions (propose/gate/execute across systems).
- **Integration**:
  - Adapt nexus-connector-template.ts as standard for dawsOS satellites (heartbeats + custom metrics like receipt volume, agent states, FunForge scores).
  - Wire to gitnexus (index nexus_ctrl code + provide impact views in dashboard).
  - Expose UI via local networking (Tailscale like 8080/8081).
  - Governance: Its commands/audit become first-class in LOCAL_GOVERNANCE.md, receipts, AGENTS.md.
  - Use dawsOS tools: gitnexus__impact before edits, dawsos_memory_profile for receipts, trivium__governance_health.
- **Steps**:
  1. Add as satellite in dawsOS config (LOCAL_RUNTIME_TOPOLOGY.json, etc.).
  2. Bridge scripts in dawsOS workspace (e.g. scripts/nexus-ctrl-bridge.sh for telemetry).
  3. Update dawsOS AGENTS.md / LOCAL_*_REGISTRIES (governed).
  4. Test with cron + agents.
  5. Propose/gate on CivForge 8080 for any cross (e.g. shared patterns).

**Value**: Accelerates dawsOS control without reinvention. Pairs with existing (gitnexus for graph, memory for continuity).

### 3. Extend nexus_ctrl for CivForge Auth Needs + Remove dawsos-auth-prototype
**Rationale**: Prototype is solid for identity (device/agent reg, PyJWT, scopes like "govern", /verify, protected_advance). But nexus_ctrl's control/audit/telemetry/dashboard + explicit CivStudy connector make it ideal to extend for unified auth+control. Removal reduces duplication, centralizes in dawsOS infra. Hybrid during migration.

**Extension in nexus_ctrl (separate project, reference for CivForge)**:
- Enhance auth (build on existing users table + connector):
  - Add /register/device (device_id, public_key, metadata) — mirror prototype.
  - /token (identity_id, scope e.g. "govern" | "control" | "read") — extend with roles/permissions (map to CivEntityMetadata.governance).
  - /verify?token=... — return claims + roles (PyJWT compatible for interoperability).
  - /revoke, audit every issuance/verify/command (to audit_logs — feed to dawsOS receipts).
- Add "govern" scope support + protected command dispatch (e.g. tokens allow issuing governance commands that CivForge validates).
- Enhance connector template: Support token auth for CivForge agents (heartbeat with resources/fun/proposals, receive commands like "advance" or "propose").
- Dashboard: Expose auth admin (devices, tokens, roles) + existing control UI.
- DB: Extend schema for roles/permissions/scopes (align with CivEntityMetadata).
- Local deploy: Same as Phase 1 (port e.g. 8082 or consolidate; use nohup).

**Migration + Removal Steps (Governed)**:
1. Analysis: Literal review of both schemas/code (use gitnexus__impact on dawsos-auth-prototype + nexus_ctrl + CivForge client). Identify gaps (prototype has stronger device reg; nexus_ctrl has better audit/control).
2. Extend nexus_ctrl as above (in its repo; propose/gate any dawsOS/Civ cross).
3. Data migration: Script to export from prototype SQLite (devices, identities, tokens) → import to nexus_ctrl Postgres (preserve history in audit_logs). Test roundtrip.
4. Update CivForge bridges (governed propose on 8080 first):
   - tools/dawsos_auth_client.py + civforge_cli.py auth subcommands: Change AUTH_BASE to new nexus_ctrl URL. Keep API identical (register-device, token, verify) for zero-downtime.
   - backend/sim_api.py (protected_advance Depends): No change if token format/scopes preserved (interoperable).
   - tools/auth-prototype/* (clone.sh, start.sh, README): Mark deprecated; remove after migration. Update SEPARATION.md (nexus_ctrl becomes new sister "auth+control" root).
5. Update CivForge docs (AGENTS.md, HANDOFF_CONTEXT.md, prompts/other_grok_context_update.md, role_registry.json — add "NexusControl" role or extend InfraGovernor).
6. Test end-to-end: Register via CLI, get "govern" token, call protected_advance, verify audit in receipts + nexus_ctrl logs. Test with agent simulation.
7. Deprecate/Remove prototype: After gate + verification receipt, stop 8081, archive prototype repo (or keep as reference), remove from dawsOS topology. Update 8080 health checks.
8. Receipts: New receipt for each phase (migration, extension, removal). Use 8080 propose-deploy or /governance/propose for changes.

**CivForge Auth Usability Post-Extension**:
- Tokens with "govern" scope still protect protected_advance.
- Richer control: Nexus commands can trigger proposals (e.g. "pause city X" becomes governed propose).
- Telemetry: Agent heartbeats feed FunForge + simulation layer.
- Dashboard: Reuse nexus_ctrl UI patterns for required gamified Command Center (workstreams as "apps", commands as unit orders).
- MCP: Connector enables agent-player lane (external agents authenticate via nexus_ctrl, play via API).
- No violation of separation: CivForge still thin client only; nexus_ctrl is external (like prototype was).

**Risks & Mitigations**:
- Breakage of protected actions: Parallel run (prototype + nexus_ctrl) + rollback receipt. Test with CLI + e2e.
- Scope creep: All via 8080 propose/gate. Literal verify (wc/grep on schemas) before edits.
- Separation: Nexus_ctrl remains separate project; CivForge uses HTTP bridge (update thin client).
- Data loss: Migration script with verification + backup.
- Replit removal: Phase 1 first; local test before cutover.

**Governed Execution**:
- This receipt = saved draft plan (for openclaw main agent review + handoff).
- Before terminal work: Propose on 8080 (e.g. `python tools/civforge_cli.py propose-deploy "NEXUS-CTRL-DAWSOS-MIGRATION-AUTH-REPLACEMENT-PLAN-20260613" ` or rich /governance/propose).
- Gate (target high FunForge on control-plane emergence).
- Literal verification + new receipt after each phase.
- Use dawsOS tools (gitnexus for impact, memory for receipts) in process.

## Ignition Options (for OpenClaw Main Agent + Swarm)
A) Review this receipt + local nexus_ctrl clone. Run verification command + propose full migration plan on 8080.
B) Start Phase 1 (local deploy of nexus_ctrl + start script).
C) Extend nexus_ctrl auth (add device reg/token/verify mirroring prototype + "govern" scope) + draft migration script.
D) Update CivForge bridges/docs for new auth surface (after gate).
E) Custom (e.g. "Focus dawsOS integration first; defer Civ auth to hybrid" or "Add nexus_ctrl as reference in GIT_LANES_POLICY.md").

**References**:
- receipts/CIVSTUDY-TERMINAL-GIT-REVIEW-20260613-160534.md (nexus patterns).
- receipts/civ-project-dawsos-full-approval-config-20260613-211500.md (terminal/dawsOS config).
- AGENTS.md, SEPARATION.md, role_registry.json.
- nexus_ctrl replit.md + connector (from terminal review).
- dawsos-auth-prototype current state (CLI + client).
- Prior swarm proposals (WP-NEXUS-CTRL-*).

This receipt is now saved in CivForge/receipts/ for openclaw main agent review. Plan is governed, receipt-first, separation-respecting. Local 8080 kernel remains the truth.

Ready for your governed work pack or next terminal step, Mike. 🔥🚀

_Generated in CivForge at 2026-06-13. Draft for openclaw main agent._
