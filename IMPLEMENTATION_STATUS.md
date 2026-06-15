# IMPLEMENTATION_STATUS.md
**CURRENT STATE (Mac Studio canonical — Jun 13 2026)**

CivForge = **local Python FastAPI governance backend** running on `0.0.0.0:8080` (uvicorn sim_api:app --reload) + `core/` package (AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore with SQLite) on this Mac Studio.

**Locked Canon**:
- Purpose: governed, receipt-first orchestration layer that proposes/gates/receipts work for the *separate* `gravity-mosaic-knowledge-graph` project.
- Strict rules: CivForge never mutates gravity-mosaic directly; only advises + receipts. Only `tools/deploy-gravity-mosaic/deploy.sh` (literal wc/grep/git rules) ever touches it.
- Godot MVP fully archived in `_archive/godot-mvp-deprecated` and never referenced in active flow.
- All future swarm activity, pushes, CLI, bridges, and enhancements target this exact running stack.

**Active Components**:
- backend/sim_api.py (earlier FastAPI shape preserved: /state, /found_city with detailed receipt, /advance_turn, /integrate + new /governance/*)
- core/ fully wired with persistence (SQLite gravity_backend.db for state + receipts that survive restarts)
- bridge/civforge_http_bridge.py — HTTP control of :8080 (Cursor local executor)
- tools/civforge_cli.py + tools/gravity_advisor.py + tools/dawsos_auth_client.py — terminal-first drivers, safety layer, and auth client bridge
- receipts/ — growing set of real governance-cycle and work-pack markdown artifacts (including auth-prototype-push, git-tools, LOCKED-CIV-GAME-PLAN, mechanics-extension-sim receipts)
- Gravity deploy tool untouched and canonical for the separate project
- dawsos-auth-prototype (separate repo https://github.com/mwd474747/dawsos-auth-prototype) — pushed after literal verification; only thin client integration in CivForge/tools/dawsos_auth_client.py + optional protected_advance demo
- **Civ Game Layer (Locked, Required)**: Planning for simple core mechanics + simulation layer + gamified Command Center (Path A) + expanded agents (GameMechanicDesigner, PlayerAgent, etc.) + required infra (Docker, hosting, MCP, auth). All extensions governed via the kernel. See planning/production_deployment_assessment.md, ROADMAP.md, AGENTS.md (role registry + agents/role_registry.json), docs/GIT_LANES_POLICY.md, docs/CIV_GAME_MECHANICS_INSPIRATION.md, receipts/LOCKED-CIV-GAME-PLAN-*.md and orphan-cleanup-*.md. Pre-realign orphans consolidated to _archive/pre-realign-orphans/ and receipts/_archive/. No implementation yet; kernel ready for governed development.

**Persistence**: Enabled (ReceiptStore now supports db_path). State snapshots + receipts load on startup.
**MCP readiness**: Stub upgraded in CLI + bridge (ready for full MCP server wrapper when requested).
**Execution lanes (v2):** Grok swarm (grok.com) plans; Cursor executes; OpenClaw escalates for wt. See `docs/EXECUTION_LANE_V2.md`.
**Bridge**: `bridge/civforge_http_bridge.py` — Cursor/scripts call get_state(), advance_cycle(), etc.

**Verification**:
- Backend responds on http://localhost:8080/state
- python3 tools/civforge_cli.py status / advance / advisor
- python3 bridge/civforge_http_bridge.py
- bash tools/turnkey-cursor-local.sh
- ls receipts/ shows multiple .md files
- gravity_backend.db exists once a cycle with persistence has run

See README.md, AGENTS.md, ORCHESTRATION_PATTERNS.md, ROADMAP.md, and `planning/production_deployment_assessment.md` for the full realigned picture (zero Godot, zero duplication, Mac Studio locked).

**Production/Deployment Assessment locked** (WP-PRODUCTION-ACCESS-ASSESSMENT-001):
- Honest gap map complete: zero public exposure today.
- High-leverage governance kernel already in place.
- Ranked deployment paths and user access models (A–D) accepted.
- Recommended first step: gamified Command Center dashboard (Path A) on top of the existing kernel.
- Mac Studio 8080 + core/ remains the single source of truth. GitHub will be synced with clear pivot language when requested.

**Mac Studio FastAPI 8080 + core/ is the locked, strengthened, fully governed canonical CivForge.**
