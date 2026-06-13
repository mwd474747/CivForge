## CivForge - Local Governed Agentic Deploy Workspace (realigned)

**Phase 0** (Done): Initialized as local tool for the separate gravity-mosaic project. FastAPI backend (earlier Codespaces shape) + strict deploy helper.

**Phase 1** (Current, aggressive realign complete): Remove Godot MVP. Port agent patterns to Python core/. Make backend the primary persistent workspace (SQLite). CLI + headless observer + Grok Mac Studio bridge as terminal/autonomous drivers. Governance + receipt loops + FunForge quality gates active. Deploy tool remains the only path to the live gravity site.

**Phase 2 — Production & Deployment (per WP-PRODUCTION-ACCESS-ASSESSMENT-001, with all optionals elevated to REQUIRED + new Civ Game track)**:
- Docker + docker-compose baseline (robust path) — **REQUIRED** (with path abstraction in bridges).
- Fast production hosting (Railway/Render/Fly.io) with the governance kernel — **REQUIRED**.
- Add auth, persistence hardening, scheduling — **REQUIRED**.
- Starter web dashboard (HTMX/Streamlit or similar) re-using civ/workstream metaphor → gamified Command Center (Path A recommended and REQUIRED for human play): agent avatars, receipt timeline, workstream map, propose/gate/quality HUD (FunForge as fun score).
- Gated integration of deploy.sh (advisory from backend only; literal rules remain in the tool) — **REQUIRED**.
- Test exposure (ngrok/Tailscale) while default remains local-only / quiet-by-default — **controlled exposure REQUIRED** for agent play.
- **New REQUIRED — Civ Game Layer**:
  - Simple core mechanics (pure Python, no legacy Godot revival): Turn-based cycles, resource economy (yields from work packs/"cities"), founding/propose actions, FunForge as central fun/quality/engagement scoring mechanic.
  - Infinite extendibility (core idea): Clean pluggable extension points (MechanicsRegistry, strategy/event/victory modules). Extensions proposed and developed through the governed play loop itself (agents/humans advance cycles as "play turns", propose new mechanics as work packs, FunForge gate on interesting emergence/pacing/juice, receipt as history). End goal: Game humans can play (dashboard) or build/run agents to play (full API/MCP/auth/handoff support).
  - All game development is governed self-improvement using the system. Simple base that compounds infinitely via community/agent contributions under receipts and gates.
  - Expanded agents (required via role registry in AGENTS.md): GameMechanicDesigner, PlayerAgent (AI play/strategy builder), MechanicsSimulator, etc.

**Phase 3 — Broader Access & Productization**:
- Public API surface + SDKs (Path B).
- Gravity-mosaic itself as the visible product (hosted explorer with CivForge governance invisible — Path C).
- Optional hybrid SaaS (Path D).
- Multi-project governance (gravity-mosaic + others) under the same receipt-first patterns.
- Stronger autonomous cycles + MCP wrapper exposure (with auth & policy).
- Full production observability, backups, and scaling.

The "4X" / civ language is retained as **internal metaphor for workstreams, attention budgets ("resources"), quality scoring ("fun/quality score"), and "founding" governed items**, plus the foundation for the playable Civ game layer.

**Core Idea (Locked)**: Game mechanics are simple at base (cycles/turns, resources/yields, actions/foundings, FunForge fun/quality as engagement and strategy scoring) but **infinitely extendible**. Extensions (new resources, events, strategies, victory conditions, AI player modules) are proposed and integrated through the governed play loop itself. All development of the game happens via governed proposals, FunForge gates, and receipts — using the system to build and improve the game.

**End Goal (Locked)**: A game that humans can play directly (via gamified dashboard/Command Center with full civ metaphors and UI for state, proposals, agent visibility, fun score). Or humans can build and run agents to play (full support via API, MCP (auth-gated), CLI, handoff/bootstrap for external agents). Simple base mechanics that compound infinitely through agent/human contributions under the governance rules (no legacy Godot or pre-pivot revival; pure new clean extensions feeding the kernel).

The delivered value remains high-fidelity, low-waste, fully receipted, agent-orchestrated updates to the separate gravity physics knowledge graph — with the Civ game as a first-class, governed, playable layer built on the same kernel for human and agent enjoyment and co-creation.

**Production Assessment locked**: See `planning/production_deployment_assessment.md` (WP-PRODUCTION-ACCESS-ASSESSMENT-001). Mac Studio 8080 + core/ is the single source of truth.
