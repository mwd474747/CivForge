# Reference: dawsos-nexus (local implementation of nexus_ctrl)

**Source**: ~/Documents/GitHub/dawsos-nexus (fork/rebirth of mwd474747/nexus_ctrl, local Mac Studio)
**Role in Architecture**: Telemetry + control proposals sister (8082). Not identity, not execution truth.
**Key Conformance to CivForge**:
- Control plane (command queue, audit_logs, alerts) → GovernanceOrchestrator, ReceiptStore, protected_advance.
- Telemetry + agent states (heartbeats, agentState, customMetrics) → FunForge, simulation layer, PlayerAgent.
- Connectors (ts/py with command poll) → lane-agent-player MCP, CivForge telemetry bridge.
- Dashboard UI (commands, stats, fleet) → lane-dashboard gamified Command Center (workstreams as apps).
- Separation: Explicit sister contract, HTTP bridges only, "commands propose not execute".
- Local deploy: Docker + start script, 127.0.0.1:8082 (aligns with Mac Studio goal, no Replit).
- dawsOS infra: RIME aligned (Receipts=audit mirror, Identity=satellite apiKey + future auth sibling, Metadata=apps, Execution=command → dawsOS dispatch). Pairs with gitnexus.

**For Auth Evolution (remove dawsos-auth-prototype)**:
- Current prototype (8081): Device/agent reg, PyJWT, "govern" scope, thin client.
- Nexus has operator token + apiKey, users table.
- Extension path: Add to nexus server: /register/device, /token (with scopes/roles), /verify (JWT compatible). Migrate data. Update CivForge client to 8082. Keep thin bridge.
- Hybrid: Keep prototype during migration; evolve nexus for control + auth.

**Reference Files** (from terminal review):
- replit.md / README: Control plane details.
- shared/schema.ts: apps, heartbeats, commands, audit_logs, agentState.
- packages/connector-*/ : Heartbeat + command poll (use for CivForge agents).
- server/middleware/auth.ts, routes.ts: Auth and command handling.
- SEPARATION.md, AGENTS.md, docs/DAWSOS_SISTER_CONTRACT.md: Explicit CivForge 8080, auth 8081, nexus 8082.

**Governed Integration**:
- Propose on 8080 (this stub).
- Gate with FunForge.
- Update GIT_LANES_POLICY.md (add to lane-required-infra + lane-meta-data-core).
- Extend role_registry (NexusControl role).
- Create thin bridge in CivForge if needed (update dawsos_auth_client or new nexus_client).
- No code copy; reference patterns only.

See receipts/nexus-ctrl-dawsos-migration-auth-replacement-plan-20260613.md for full plan.
