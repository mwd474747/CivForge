# CivForge

**Local governed agentic workspace** for safely orchestrating and deploying the *separate* gravity-mosaic-knowledge-graph project (and future projects) on this computer.

Core: receipt-first DawsOS patterns, persistent FastAPI workspace (the earlier backend sandbox), pure-Python AgentBrains + FunForge quality scoring + Governance gates, strict literal-verification deploy tools, and terminal/CLI/headless driver.

**Gravity-mosaic and CivForge are two completely separate projects.**

- Gravity-mosaic-knowledge-graph is the independent project (knowledge graph, models, transcript work) at its own directory and repo.
- CivForge is the local governed agentic workspace/tooling whose only interaction with gravity-mosaic is through the strict `tools/deploy-gravity-mosaic/deploy.sh` (literal verification only, no direct mutation from CivForge code).

All changes to gravity-mosaic are made exclusively on disk at `/Users/michaeldawson/gravity-mosaic-knowledge-graph` and are **only ever deployed** via the deploy helper (which enforces full literal reads, wc/grep golden anchors + new features, Python EQUATIONS tests, zero bad legacy, exact git operations, and post-deploy verification).

The Godot 4X MVP (playable UI, map, end-turn loops, etc.) has been removed in favour of the earlier FastAPI version + Python core so the original intent is fully implemented: CivForge is the intelligent local governance layer, not the game itself.

## Quick Start (exactly as the original pasted Codespaces instructions, now local)

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

See `setup_hybrid.sh --start-backend` for a one-command local activation.

## What CivForge Actually Is (initial intent, now dominant)

- The local on-machine workspace that makes deploying the separate gravity-mosaic project safe, receipted, and agent-augmented.
- FastAPI as the persistent "in-repo Codespace" for state, work packs, agent decisions, FunForge scores, and receipts.
- Python core/ with AgentBrain (receipt memory + goal stack + reflection), FunForge (quality >80 gate), GovernanceOrchestrator, ReceiptStore (disk + memory).
- `tools/deploy-gravity-mosaic/deploy.sh` as the sacred literal enforcer.
- CLI + headless_observer.py for pure terminal / autonomous operation.
- governance/ and receipts/ as first-class artifacts.
- All "simulation" now means governance cycles over real work on the gravity physics knowledge graph (Biefeld-Brown models, precision porting, transcript extensions, etc.).

The 4X/civ metaphor is retained only as an internal model for workstreams, attention budgets ("resources"), quality ("fun_score"), and "founding" work items. The product is governed deployments and agentic process improvement for the separate project.

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