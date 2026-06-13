# CivForge Autonomous Agent Orchestration (dawsOS-inspired, realigned)

## Core Patterns (implemented in pure Python core/ + FastAPI 8080)
- **Master Work Pack Executor**: `python tools/civforge_cli.py advance` or POST /advance_turn (orchestrator + brains + FunForge + gate + receipt).
- **Agent Brain Pattern** (Python): `core/agent_brain.py` — receipt_memory, goal_stack, decide_action(state), record_receipt + reflection on low fun/quality. Used for gravity/auth/handoff/meta decisions (research vs. verify vs. propose vs. govern).
- **Swarm Coordination**: Grok main + registered sub-agents (Harper, Sebastian per role registry in AGENTS.md) in the orchestrator. Decisions logged as receipts. Cross-workspace swarm uses HANDOFF_CONTEXT + context prompts.
- **Continuous Governance Loop**: Advance cycle → FunForge quality score (agency/emergence/pacing/juice) → gate (min 80) → rich receipt to disk + backend state → update workstream "resources" / fun_score. Mirrors the Codespaces /advance_turn surface + governance extensions.
- **Autonomous / Headless Operation**: `bridge/headless_observer.py` + `tools/civforge_cli.py` + `grok_macstudio_bridge.py` drive the backend from terminal or other agents (including external Grok via handoff). No Godot required.
- **Gravity Deploy Governance**: Proposals/gates here. Real execution **always** via the strict `tools/deploy-gravity-mosaic/deploy.sh` (literal verification on the separate project).
- **Auth Layer Governance** (new): Enable via `tools/auth-prototype/` bridge. Use client or CLI `auth` subcommands for tokens. Protected actions (e.g. /governance/protected_advance) require valid "govern" scope from separate :8081 prototype.
- **Governed Meta-Actions** (dawsOS REPO_OPS + self-gov): Repo syncs, agent config updates (these docs), bridge additions, handoff artifacts — propose first (via CLI or /governance), impact check (grep/wc or GitNexus-style), gate, receipt. Before editing: git status/branch/remotes, confirm canonical root, literal verify.
- **Cross-Workspace Handoff & Swarm Etiquette** (dawsOS bootstrap/handoff): New workspace or other Grok: bootstrap with HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md + AGENTS bootstrap section. Run literal checks first. Write-it-down (receipts). Follow same proposal-first + auth + separation rules. "Text > brain".

**Agent Role Registry Reference** (see AGENTS.md for full; keep aligned with `backend/sim_api.py` + core/orchestrator.py):
- grok, harper (memory/systems), sebastian (governance/safety). Capabilities: govern, auth, handoff, deploy-advisor, literal-verify.

**Current Priorities** (post realign + auth/handoff + locked Civ Game):
1. Core Python patterns (AgentBrain, FunForge, Governance, Orchestrator, ReceiptStore with SQLite — done and live).
2. FastAPI workspace (state shape + /state /found_city /advance_turn + /governance/* + protected auth demo — done).
3. CLI + bridges + auth-prototype/ as drivers (auth subcommands, clone/start for :8081, gravity advisor, deploy.sh).
4. Handoff / cross-agent support (HANDOFF_CONTEXT.md, context update prompt, bootstrap in AGENTS — done + pushed).
5. Governed meta + self-gov (literal process on CivForge itself, receipts for syncs/configs, role registry).
6. All work on separate targets (gravity-mosaic, auth-prototype) remains under literal disk + verification contract + bridges only. Receipts mandatory.
7. **Civ Game Layer (REQUIRED, locked)**: Implement simple core mechanics + simulation layer + pluggable extensions (MechanicsRegistry) as governed work. Use lanes (docs/GIT_LANES_POLICY.md) for parallel development of mechanics, simulation, dashboard (human play), agent player support. All via the existing loop (agents decide/propose in cycles → FunForge gate → receipt → integrate). See planning/ docs and receipts/LOCKED-CIV-GAME-PLAN-*.md. Kernel is ready; actual layer is the next governed extension target.

**Borrowed from dawsOS sister patterns**: Receipt-first evidence (reconstructable), proposal/dispatch-only for mutations, GitNexus-style impact before config changes, registries for role alignment, write-it-down discipline, specialized bootstrap for handoff contexts, three-roots separation hygiene. See docs/patterns/borrowable-governance-patterns.md for reuse.
