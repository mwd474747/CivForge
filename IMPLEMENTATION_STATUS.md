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
- bridge/grok_macstudio_bridge.py — direct Grok / swarm control of the 8080 backend
- tools/civforge_cli.py + tools/gravity_advisor.py — terminal-first drivers and safety layer
- receipts/ — growing set of real governance-cycle and work-pack markdown artifacts (including auth-prototype-push receipts)
- Gravity deploy tool untouched and canonical for the separate project
- dawsos-auth-prototype (separate repo https://github.com/mwd474747/dawsos-auth-prototype) — pushed after literal verification; only thin client integration in CivForge/tools/dawsos_auth_client.py + optional protected_advance demo

**Persistence**: Enabled (ReceiptStore now supports db_path). State snapshots + receipts load on startup.
**MCP readiness**: Stub upgraded in CLI + bridge (ready for full MCP server wrapper when requested).
**Grok Bridge**: Live — main orchestration can call get_state(), advance_cycle(), propose_work(), gate_proposal(), get_gravity_recommendation() directly.

**Verification**:
- Backend responds on http://localhost:8080/state
- python3 tools/civforge_cli.py status / advance / advisor / mcp-stub all functional
- python3 bridge/grok_macstudio_bridge.py succeeds against the real backend
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