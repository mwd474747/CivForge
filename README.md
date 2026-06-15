# CivForge

**Local governed agentic workspace** for safely orchestrating and deploying the *separate* gravity-mosaic-knowledge-graph project (and future projects) on this computer.

Core: receipt-first DawsOS patterns, persistent FastAPI workspace (the earlier backend sandbox), pure-Python AgentBrains + FunForge quality scoring + Governance gates, strict literal-verification deploy tools, and terminal/CLI/headless driver.

**Gravity-mosaic and CivForge are two completely separate projects.**

- Gravity-mosaic-knowledge-graph is the independent project (knowledge graph, models, transcript work) at its own directory and repo.
- CivForge is the local governed agentic workspace/tooling whose only interaction with gravity-mosaic is through the strict `tools/deploy-gravity-mosaic/deploy.sh` (literal verification only, no direct mutation from CivForge code).

All changes to gravity-mosaic are made exclusively on disk at `/Users/michaeldawson/gravity-mosaic-knowledge-graph` and are **only ever deployed** via the deploy helper (which enforces full literal reads, wc/grep golden anchors + new features, Python EQUATIONS tests, zero bad legacy, exact git operations, and post-deploy verification).

The Godot 4X MVP (playable UI, map, end-turn loops, etc.) has been removed in favour of the earlier FastAPI version + Python core so the original intent is fully implemented: CivForge is the intelligent local governance layer, not the game itself.

## Quick Start (Mac Studio — recommended)

```bash
cd ~/CivForge
bash tools/start-kernel-8080.sh
open http://127.0.0.1:8080/dashboard
bash tools/validate-game.sh          # pytest + API + turnkey
```

**Multi-agent dashboard:** agent tabs, 5×5 map, negotiations, alliances, victory bar, mechanics lanes. See `docs/GAME_PLAY_GUIDE_V1.md`.

**Legacy FastAPI start** (if you prefer manual uvicorn):

```bash
cd /Users/michaeldawson/CivForge/backend
python3 -m pip install fastapi uvicorn pydantic requests
python3 -m uvicorn sim_api:app --reload --host 0.0.0.0 --port 8080
```

Test (verbatim from the earlier version):

- `curl http://localhost:8080/state`
- `curl -X POST http://localhost:8080/found_city -H "Content-Type: application/json" -d '{"city_name":"Gravity research thread","investment":4}'`

Then use the realigned governance:

```bash
python tools/civforge_cli.py status
python tools/civforge_cli.py advance
python tools/civforge_cli.py recommend
python tools/civforge_cli.py propose-deploy
# After a gate + human review of literal changes on the gravity project:
./tools/deploy-gravity-mosaic/deploy.sh
```

See direct FastAPI start in Quick Start above, or `python tools/civforge_cli.py status` once backend is running. (setup_hybrid.sh and other pre-realign artifacts moved to _archive/pre-realign-orphans/ or receipts/_archive/ during governed cleanup; see receipts/orphan-cleanup-*.md and docs/CIV_GAME_MECHANICS_INSPIRATION.md for history and extracted concepts.)

## What CivForge Actually Is (initial intent, now dominant)

- The local on-machine workspace that makes deploying the separate gravity-mosaic project safe, receipted, and agent-augmented.
- FastAPI as the persistent "in-repo Codespace" for state, work packs, agent decisions, FunForge scores, and receipts.
- Python core/ with AgentBrain (receipt memory + goal stack + reflection), FunForge (quality >80 gate), GovernanceOrchestrator, ReceiptStore (disk + memory).
- `tools/deploy-gravity-mosaic/deploy.sh` as the sacred literal enforcer.
- CLI + headless_observer.py for pure terminal / autonomous operation.
- governance/ and receipts/ as first-class artifacts.
- All "simulation" now means governance cycles over real work on the gravity physics knowledge graph (Biefeld-Brown models, precision porting, transcript extensions, etc.).

The 4X/civ metaphor is retained as an internal model for workstreams, attention budgets ("resources"), quality ("fun_score"), and "founding" work items — and as the foundation for the **Civ Game Layer** (see locked planning docs).

**Civ Game Layer (Locked End Goal)**: A playable game with simple core mechanics (turns/cycles, resources/yields from work packs, founding/propose actions, FunForge as central fun/quality/engagement scoring) that is infinitely extendible. Humans play directly via the required gamified Command Center dashboard. Humans or agents can build and run AI players (full support via API, MCP (auth-gated), CLI, handoff). All extensions (new mechanics, simulation layer, strategies, victory conditions) are developed through the governed play loop itself (propose as work packs → FunForge gate → pluggable modules feeding the orchestrator/receipts/gate). No legacy Godot or pre-pivot revival.

See:
- planning/production_deployment_assessment.md and planning/extension_roadmap_v2.md (locked required elements: simulation layer, dashboard, expanded agents, Docker/hosting/MCP, etc.)
- ROADMAP.md (Civ Game track)
- AGENTS.md (role registry including GameMechanicDesigner, PlayerAgent, MechanicsSimulator; bootstrap with HANDOFF + prompts/other_grok_context_update.md)
- docs/GIT_LANES_POLICY.md (parallel lanes for mechanics, simulation, dashboard, agent-play, infra)
- docs/patterns/borrowable-governance-patterns.md (core patterns + Civ Game extensions)
- receipts/LOCKED-CIV-GAME-PLAN-*.md

The delivered value is high-fidelity, low-waste, fully receipted, agent-orchestrated governance — with the Civ game as a first-class, governed, playable layer for human enjoyment and agent co-creation on top of the same kernel used for gravity work.

## Structure (post-aggressive realign)

- `backend/sim_api.py` — The FastAPI workspace (state shape preserved from the earlier version + new /governance/* endpoints).
- `core/` — AgentBrain, FunForge, GovernanceGate, Orchestrator, ReceiptStore (the portable patterns).
- `tools/deploy-gravity-mosaic/` — The only way changes ever reach the live gravity site.
- `tools/civforge_cli.py` + `bridge/headless_observer.py` — Terminal and autonomous drivers.
- `governance/`, `receipts/`, `planning/`, `skills/` — DawsOS-style artifacts.
- `_archive/godot-mvp-deprecated/` — Old playable Godot slice (removed from active use).

Everything else (old Godot scripts, GDScript playtests, Godot-specific orchestration language) has been stripped so the initial intent is implemented cleanly.

## Process Rules (non-negotiable for gravity-mosaic)

- Local disk at the gravity-mosaic path is the single source of truth.
- Before any commit/push to gravity-mosaic: full literal read + wc -l + grep for golden anchors + feature strings + Python model tests + bad-legacy count must be 0.
- Commits contain only exact full-content descriptions (no summaries or meta added by the agent).
- Post-deploy: hard refresh + verification (browser tools or equivalent) logged as receipt.
- CivForge (this repo) proposes, gates, and records — the deploy.sh executes under those receipts.

This keeps the gravity-mosaic artifact pristine while giving CivForge (Grok + sub-agents) a powerful governed workspace to accelerate high-quality work on it.