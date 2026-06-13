**CivForge Extension Planning v2 - Autonomous Horizon (realigned to Mac Studio canon)**

This file has been updated to match the current locked reality (WP-PRODUCTION-ACCESS-ASSESSMENT-001 and prior realign).

## Current Foundation (Locked)
- Local governed agentic orchestration backend: FastAPI 8080 + core/ (AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore with SQLite).
- Purpose: receipt-first, safe management of the *separate* gravity-mosaic-knowledge-graph project.
- No active playable 4X game UI (Godot MVP archived).
- "The game" = the governed workflow + optional interactive layers (dashboard, command center, explorer).

## Phase 1 (Immediate — Mac Studio + Initial Production)
- Persistence hardening + auto-backup (SQLite baseline done; expand as needed).
- Grok Mac Studio bridge + CLI power-up (done).
- Gravity safety advisor + gated deploy.sh integration.
- Production assessment locked (see planning/production_deployment_assessment.md).
- Starter deployment artifacts (Dockerfile + docker-compose) + first hosting test (Railway/Render/Fly.io recommended robust path).
- Basic auth + secrets handling for any exposed instance.
- FunForge quality scoring remains the gate for all work (target ≥80–88).

## Phase 2: Production Kernel + Access Layers
- Full deployment (Docker → chosen host) with the governance kernel live.
- Gamified web dashboard / Command Center (Path A — recommended): agent avatars, receipt timeline, workstream map, propose/gate/quality HUD. Re-uses civ metaphor for continuity.
- Public API surface + client SDKs (Path B).
- Gravity-mosaic as visible product (hosted explorer with CivForge as invisible governed engine — Path C).
- Test exposure (ngrok/Tailscale) with security notes; default remains local/quiet-by-default.

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
