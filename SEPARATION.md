# CivForge and Gravity-Mosaic Separation

**Gravity-mosaic-knowledge-graph and CivForge are two completely separate projects.**

## Project Boundaries (Strict)

### Gravity-Mosaic-Knowledge-Graph
- **Location**: `/Users/michaeldawson/gravity-mosaic-knowledge-graph`
- **Repo**: https://github.com/mwd474747/gravity-mosaic-knowledge-graph
- **Purpose**: Independent static knowledge graph site + Python physics models (Biefeld-Brown thrust, precision porting, EQUATIONS) + declassified document transcript research.
- **Content rules**: All source (index.html, models/*.py, README, ROADMAP, transcript data) lives only here.
- **Changes**: Made directly in this directory using full literal disk reads. Deployed **only** via its own verified process.

### CivForge
- **Location**: `/Users/michaeldawson/CivForge`
- **Repo**: https://github.com/mwd474747/CivForge
- **Purpose**: Local governed agentic workspace and tooling on this Mac.
  - FastAPI governance backend (backend/sim_api.py + core/)
  - Agent patterns (AgentBrain, FunForge quality scoring, GovernanceOrchestrator, ReceiptStore)
  - CLI, Grok bridge, headless observer
  - Planning, receipts, governance artifacts
- **Role with gravity-mosaic**: Provides receipt-first proposals, quality gates, and orchestration advice. **Never** directly edits gravity-mosaic files.

## The Only Allowed Bridge
`tools/deploy-gravity-mosaic/deploy.sh` (inside CivForge)

This script:
- Is the **sole** mechanism for moving work from CivForge governance into the gravity-mosaic project.
- Always `cd`s to the separate gravity-mosaic directory.
- Performs exhaustive literal verification (wc -l, golden anchor greps, Python model tests, zero bad legacy, etc.).
- Executes the exact git add/commit/push there.
- CivForge code may only invoke or advise this script. It must never `open()`, `write()`, or copy source from/to the gravity directory.

## What "Clean and Separate" Means
- No gravity-mosaic source files (index.html, models/biefeld_brown_thrust.py, etc.) may exist in CivForge outside the deploy bridge directory.
- No CivForge source (core/, backend/, bridge/grok_macstudio_bridge.py, planning/, etc.) may exist inside the gravity-mosaic directory.
- Git histories and remotes are independent.
- Documentation in both projects must clearly state the separation.
- Any future dashboard, explorer, or "game-like" UI for governance stays in CivForge. Any public viewer for the knowledge graph itself should live in (or alongside) the gravity-mosaic project.

## Current State (Verified)
- Both directories are independent git repositories with different remotes.
- Audits (find + grep) confirm no source leakage.
- The only references are:
  - Historical commit messages in gravity-mosaic .git (from using the deploy tool – expected and correct).
  - Intentional governance references in CivForge planning/receipts/deploy helper (with explicit "separate project" language).
- Caches and temporary files cleaned in CivForge.

This SEPARATION.md is the canonical declaration. All planning, code, and future work must respect it.

**Mac Studio local truth**: CivForge (this workspace) is the governance layer. Gravity-mosaic is the independent artifact being governed.


## Updated sister: dawsos-nexus (8082)

- **Telemetry + command queue only** for CivForge (thin HTTP bridge).
- **Identity** remains `dawsos-auth-prototype` (`:8081`) per `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` — Nexus operator token is not CivForge product identity.
- Full cross-plane rules: `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`.

## Swarm alignment note (2026-06-15)

Execution truth for Grok swarm: `:8080` kernel + alignment receipts 020/021/024. Dashboard and Vercel are **landed** in tree; next extensions are mechanics/CivStudy metadata/8082 thin bridge only. CivForge receipts do not confer dawsOS wt promotion authority.
