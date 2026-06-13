**CivForge Extension Planning v2 - Autonomous Horizon (realigned to Mac Studio canon)**

This file has been updated to match the current locked reality (WP-PRODUCTION-ACCESS-ASSESSMENT-001 and prior realign).

## Current Foundation (Locked)
- Local governed agentic orchestration backend: FastAPI 8080 + core/ (AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore with SQLite).
- Purpose: receipt-first, safe management of the *separate* gravity-mosaic-knowledge-graph project.
- No active playable 4X game UI (Godot MVP archived).
- "The game" = the governed workflow + optional interactive layers (dashboard, command center, explorer).

## Phase 1 (Immediate — Mac Studio + Initial Production) — All Items REQUIRED
- Persistence hardening + auto-backup (SQLite baseline done; expand as needed). **REQUIRED.**
- Grok Mac Studio bridge + CLI power-up (done).
- Gravity safety advisor + gated deploy.sh integration (abstraction of hard-coded paths REQUIRED).
- Production assessment locked (see planning/production_deployment_assessment.md) — **with all optionals elevated to required + new Civ Game track**.
- Starter deployment artifacts (Dockerfile + docker-compose) + first hosting test (Railway/Render/Fly.io recommended robust path). **Docker + at least one hosting path REQUIRED.**
- Basic auth + secrets handling for any exposed instance. **Full auth integration REQUIRED.**
- FunForge quality scoring remains the gate for all work (target ≥80–88). **REQUIRED.**
- **New REQUIRED: Simple Civ Game core mechanics layer** (pure Python, no legacy Godot): Turn cycles, resource economy (yields from work packs), founding actions, FunForge as core fun/quality/engagement scoring. Designed for infinite extendibility via pluggable modules.
- **New REQUIRED: Expanded agent registry + specialists** (GameMechanicDesigner, PlayerAgent for human/agent play, MechanicsSimulator, UICoordinator, InfraGovernor) per dawsOS-inspired AGENTS.md role registry.
- **New REQUIRED: Initial simulation + governed play loop for mechanics** (as demonstrated in prior simulation: agents decide/propose extensions in advance cycles, FunForge gate, receipt. All future extensions developed this way).

## Phase 2: Production Kernel + Access Layers — All Items REQUIRED
- Full deployment (Docker → chosen host) with the governance kernel live. **REQUIRED.**
- Gamified web dashboard / Command Center (Path A — recommended and now REQUIRED for human play): agent avatars, receipt timeline, workstream map (civ metaphor), propose/gate buttons, quality HUD (FunForge as fun score), real-time state. Supports human play and watching agent play. Re-uses civ metaphor for continuity.
- Public API surface + client SDKs (Path B) + MCP wrapper (auth-gated) **REQUIRED** for agent players to fully participate and build strategies.
- Gravity-mosaic as visible product (hosted explorer with CivForge as invisible governed engine — Path C) — parallel optional track.
- Test exposure (ngrok/Tailscale) with security notes; default remains local/quiet-by-default. **Controlled exposure REQUIRED** for agent play testing.
- **New REQUIRED: Civ Game Mechanics Development**:
  - Core simple mechanics (turns, resources as yields, work packs as actions/foundings, FunForge fun/quality as central scoring and engagement driver).
  - Infinite extendibility design: Clean extension points (MechanicsRegistry, pluggable event/strategy/victory modules). Humans or agents propose extensions as governed work packs. FunForge gates on emergence of interesting new play (high agency + emergence + pacing + juice). If passed, integrated. All development happens *through* the governed play loop (advance as "turns", propose improvements, simulate, gate, receipt).
  - No legacy: New simple Python implementation only. Extensions feed existing orchestrator/receipts/gate.
  - Play modes: Human (dashboard), Agent (full API/MCP/auth/CLI/handoff support — external agents can "play" or "build strategies").
  - End goal locked: A game humans can play directly, or humans/agents can build and run AI players for. Simple base mechanics that are infinitely extendible via the system's own governance.

## Phase 3: Scale & Productization
- Hybrid SaaS option (Path D) or multi-tenant workspaces.
- Multi-project governance (gravity-mosaic + future projects).
- Autonomous scheduling + 24/7 cycles (propose → FunForge gate → receipt → recommend/execute).
- MCP wrapper / observability layer for other agents (auth-gated).
- Stronger production features: logging, monitoring, backups, scaling.
- Full production observability and community / team testing pipeline.

## Quality Gates (Non-Negotiable for All Extensions)
- All work packs / proposals must pass FunForge quality scoring (target ≥80, recommended ≥88 for visible changes).
- Strict separation: CivForge never directly mutates the gravity-mosaic repo. Only the literal deploy.sh does (with full wc/grep/Python model / bad-legacy verification).
- Receipts are first-class and human + machine readable.
- Mac Studio 8080 + core/ (or its deployed equivalent) remains the source of truth for governance state.

**Next Auto-Sprint options** (reply with letter from production assessment or custom):
- A: Dockerfile + docker-compose + starter dashboard + Railway/Render push.
- B: Auth + persistence hardening + first autonomous gravity deploy recommendation cycle.
- C: Full production roadmap + hosting choice + test exposure.
- D: Gravity-mosaic public viewer first (CivForge as backend).
- E: Local-only hardening (launchd, daily summaries, etc.).

See:
- planning/production_deployment_assessment.md (full validated proposal)
- ROADMAP.md
- IMPLEMENTATION_STATUS.md (Mac Studio canon)
- AGENTS.md / ORCHESTRATION_PATTERNS.md (swarm roles updated for production)
