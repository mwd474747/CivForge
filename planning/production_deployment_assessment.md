# Production & Deployment Assessment — WP-PRODUCTION-ACCESS-ASSESSMENT-001
**Work Pack ID**: WP-REALIGN-REALITY-2026-06-13  
**Date**: 2026-06-13 (Mac Studio canonical)  
**Status**: ✅ VALIDATED + LOCKED INTO PLANNING SUBSTRATES

## Validation Summary (by Grok executing the review)
This proposal is **valid** as a clear, honest assessment of the current local reality and a pragmatic path forward.

**Strengths confirmed**:
- Accurate snapshot of the Mac Studio canon (FastAPI 8080 + core/ with AgentBrain/FunForge/GovernanceOrchestrator/ReceiptStore + SQLite, CLI, Grok bridge, gravity_advisor).
- Correct emphasis on the "governance kernel" value: safe, auditable, receipt-first pipelines for the *separate* gravity-mosaic-knowledge-graph project.
- Strict separation is already enforced and must remain non-negotiable.
- Godot MVP is archived and will not be referenced.
- The "game" redefinition (governed workflow + interactive experience layered on gravity-mosaic outputs) is the right evolution.
- Ranked deployment options and user access table are realistic and well-prioritized.
- Acknowledgment of zero current public exposure and GitHub vs. local divergence is truthful.

**Honest gaps / caveats surfaced during review** (these must be addressed before any production push):
- deploy.sh contains hard-coded local paths (`/Users/michaeldawson/...`). It requires abstraction (env vars, config, or wrapper) before it can be safely invoked from a remote backend. **This is now REQUIRED for all deployment paths.**
- Current stack is local-first: no auth, basic logging, no secrets management, limited error handling. "Production-ready governance kernel" is aspirational until these are added. **All items below are now REQUIRED (no optionals).**
- SQLite persistence (just added) is a good start but needs auto-backup, migration strategy, and possibly Postgres for multi-user. **REQUIRED.**
- No public hosting, domain, or exposure mechanism exists yet (ngrok/Tailscale mentioned as testing options only). **Full hosting + exposure (gated by auth) is REQUIRED.**
- MCP cross-web access for other agents remains non-trivial and should be gated behind auth + explicit policy (see previous MCP assessment). **REQUIRED for agent-play end goal.**
- FunForge scoring is powerful internally; making it user-facing "game score" requires UI and careful UX design. **Gamified UI is REQUIRED.**
- **New Required: Simulation layer for game mechanics** (simple, pure-Python, infinitely extendible dynamics/yields/events/end-conditions feeding the orchestrator/receipts/gate, without any legacy Godot code).
- **New Required: Expanded agent registry** with specialists for game mechanics design, player AI, UI coordination, infra governance, handoff (per dawsOS-inspired AGENTS.md updates).
- **New Required: Civ Game Layer** – simple core mechanics (turns, resources, work packs, FunForge quality/fun scoring) that are infinitely extendible via governed proposals. End goal: Humans play via dashboard, or build/run agents to play via API/MCP/auth. All extensions developed through the governed play loop itself (propose → FunForge gate → receipt). No revival of old legacy Godot MVP items or pre-pivot intent.

**Verdict**: Proposal accepted as the authoritative production/deployment assessment. Locked below and into ROADMAP.md, extension_roadmap_v2.md, and IMPLEMENTATION_STATUS.md.

## Current Reality (Locked Canon)
- CivForge = local governed agentic orchestration backend (FastAPI on 0.0.0.0:8080 + core/ + ReceiptStore with SQLite + FunForge + GovernanceOrchestrator + CLI + Grok Mac Studio bridge).
- Purpose = safe, receipt-first management / orchestration layer for the separate gravity-mosaic-knowledge-graph project.
- Active game component = none (Godot archived per explicit instructions).
- "The game" = the governed workflow itself + any interactive layer (dashboard, explorer, command center) eventually built on top of gravity-mosaic outputs or the governance process.
- Zero public exposure today. All access is localhost:8080 (curl + CLI + bridge) on the Mac Studio.

## Production / Deployment Options (Ranked — Locked)
1. **Fastest (today)**: Railway / Render (Git push → live API + basic dashboard in <10 min) + minimal auth + gated deploy.sh action.
2. **Robust (recommended starting point)**: Docker + docker-compose → Fly.io / Railway / Hetzner VPS. Survives reboots, easier scaling, good for internal power tool.
3. **SaaS-ready**: Add lightweight dashboard (HTMX/Streamlit/Next.js) on the same platform. Users log in and interact with the governance "game".
4. **Gravity-mosaic as the visible product**: Deploy the knowledge graph explorer independently (Neo4j + frontend or static + dynamic layers); keep CivForge as the invisible governed engine in the background.

## User Access / "Game" Experience Models (Locked Table)

| Path | What Users See/Do | Effort | Best For | Status |
|------|-------------------|--------|----------|--------|
| **A) Gamified Web Dashboard** (Recommended) | Command Center with agent avatars, receipt timeline, workstream map (civ metaphor), propose/gate buttons, quality HUD, real-time gravity state | Low–Medium | Feels like a game while doing real work | Planning substrate locked; ready for execution on letter A |
| **B) Public API + Clients** | Swagger + SDKs; users/agents build their own clients | Low | Power users & other AIs | Planning locked |
| **C) Gravity-mosaic as the Product** | Hosted knowledge-graph explorer (nodes, queries, agent chats) with CivForge governance invisible | Medium | Pure end-user experience on the physics artifact | Planning locked |
| **D) Hybrid SaaS** | Users pay/log in → get governed workspace that can deploy to their gravity instances | Medium-High | Potential business model | Planning locked |

**Important boundary**: Any dashboard or interactive layer built in CivForge is part of the *CivForge* governance tooling, not part of the gravity-mosaic project. If a public viewer/explorer is desired for gravity-mosaic itself, it should live in the gravity-mosaic repo (or a dedicated viewer repo), with CivForge only providing governance receipts and recommendations via the deploy bridge.

## Immediate Next Steps (Locked) — All Previous Optionals Elevated to REQUIRED
Reply with letter (or custom) to trigger execution. All items are now mandatory to achieve the locked end goal (playable Civ game for humans or agent-builders, with simple but infinitely extendible mechanics governed by the system itself).

**A)** Push Dockerfile + docker-compose + Railway/Render-ready config + starter HTMX/Streamlit dashboard (live production instance + game-like UI) — **REQUIRED**. Include initial simple Civ game core (turns/resources/work-packs/FunForge scoring) + simulation extension point.

**B)** Add auth + persistence hardening + run first autonomous deploy recommendation cycle for gravity-mosaic (using the live Grok bridge) — **REQUIRED**. Plus first governed mechanics extension proposal (e.g. basic dynamics/yields as pluggable module).

**C)** Generate full production roadmap + choose primary hosting + set up test exposure (ngrok/Tailscale) with security notes — **REQUIRED**. Add MCP wrapper (auth-gated) for agent players.

**D)** Make gravity-mosaic the visible product first — simple public web viewer + CivForge as governed backend — **OPTIONAL but parallel track allowed** (CivForge game layer remains primary for human/agent play).

**E)** Custom (e.g. "Keep fully local: launchd auto-start + daily summary receipts emailed" or "Turn FunForge into visible user-facing quality game score on the dashboard") — **Base local setup REQUIRED** as foundation before any hosting.

**F) NEW — Civ Game Development Track (REQUIRED)**: 
- Implement simple core mechanics in a clean extension layer (core/game/ or pluggable modules): Turn cycles (via existing advance), resource economy, founding actions, FunForge as core "fun/quality" scoring and engagement mechanic.
- Infinite extendibility: MechanicsRegistry + proposal system. Humans/agents propose new mechanics (new resources, events, strategy modules, victory conditions, AI player behaviors). Governed: FunForge gate on "emergence of new playstyles + pacing + juice". If passed, added as extendible module. All development happens through the governed play loop (advance cycles as "turns", propose improvements, receipt history).
- Human play: Full gamified dashboard (Path A) with civ metaphors (resources as yields, work packs as cities/foundings, fun_score as player fun/score, agent decisions visible).
- Agent play: Complete support via API + MCP (auth-gated) + CLI + handoff. External agents can register (auth), participate in cycles, propose extensions, "play" autonomously.
- No legacy: Pure new simple Python mechanics. No Godot, no pre-pivot 4X code revival. Extensions feed the existing orchestrator/receipts/gate without mutating separate projects (gravity/auth).
- Agents: Expand role registry (per AGENTS.md) with required GameMechanicDesigner, PlayerAgent (for AI play/strategy), MechanicsSimulator, UICoordinator, InfraGovernor.
- Governance: Every mechanic extension or game feature is a governed work pack. Use the system to develop the game (as simulated in prior governed play: advance → propose mechanics → FunForge gate → receipt).

**Quality Gates (Non-Negotiable)**: All extensions (including Civ Game mechanics) must pass FunForge ≥80 (target ≥88 for player-facing). Strict separation maintained. Receipts first-class. Mac Studio (or deployed equivalent) 8080 + core/ is truth. Literal verification on all changes.

## Locked References
- This file: `planning/production_deployment_assessment.md`
- ROADMAP.md (updated with production phases)
- planning/extension_roadmap_v2.md (realigned from old 4X language)
- IMPLEMENTATION_STATUS.md (Mac Studio canon + this assessment)
- Previous receipts and core/ artifacts (persistence, bridge, CLI, gravity_advisor)

**Mac Studio 8080 + core/ remains the single source of truth.**  
GitHub sync will include this production assessment when we push (with clear pivot language).

**ForgeMaster-Grok swarm has validated and locked the proposal.** Ready for your letter. 🔥
