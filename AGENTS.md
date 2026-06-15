# AGENTS.md - CivForge Agentic Architecture (dawsOS-inspired, realigned)

**This folder (CivForge) is home for governed agentic work on separate projects. Treat it that way.**

## Bootstrap (Every Session / New Workspace - Mandatory, dawsOS-style)
Before doing anything else (no mental notes, text > brain):

1. Read `SEPARATION.md` — the canonical three-project contract (CivForge governance root, gravity-mosaic as independent target artifact, dawsos-auth-prototype as sister identity root). Do not conflate.
2. Read `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` — cross-plane rules with dawsOS wt and dawsos-nexus (execution, receipts, identity, telemetry).
2. If this is a fresh or other-workspace context: Read `HANDOFF_CONTEXT.md` (the portable bootstrap artifact) + `prompts/other_grok_context_update.md` (context sync for less-context agents).
3. Read `PROJECT_MANIFESTO.md` (or equivalent SOUL) — who CivForge is and its intention.
4. Read latest in `receipts/` (or `receipts/github-sync-*.md`, governance-cycle-*.md) for continuity.
5. Run literal verification: `git status --short`, `wc -l` on key files (SEPARATION, HANDOFF, core/*.py, tools/auth-prototype/*), `grep` for golden anchors ("separate projects", "literal verification", "FunForge >=80", "auth-prototype", "handoff").
6. Confirm working targets: localhost:8080 (CivForge backend + /state probe). Nexus :8082 for machine telemetry heartbeats + command proposals (governance_kernel per wt canon, strict allowed_actions=["sync_config"]). Auth prototype :8081 for identity/JWT (machine satellite key only for Nexus paths; no dev bypass per boundary contract). Do not conflate. See docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md.

**Write It Down discipline**: Capture decisions, context, lessons in receipts/ or daily notes. No mental notes. When you learn or mistake — document so future-you (or other Grok) doesn't repeat it.

## Primary Agent: Grok (Main Orchestrator / ForgeMaster-Grok)
**Role**: Lead local operator for the governed workspace. Proposes/gates work for *separate* targets (gravity-mosaic first), drives 8080 + core/ cycles, enforces literal verification + receipts, uses auth bridge for protected actions, only triggers real changes via strict bridges.

**Authority**: High for proposals, orchestrator calls, gates, receipts, CLI/bridge use. Mutations on targets only after gate + human or governed approval. For meta (this repo's docs, bridges, syncs): treat as governed work packs (propose via CLI or /governance/propose, impact check like GitNexus, receipt).

**Agent Role Registry** (runtime alignment, inspired by dawsOS LOCAL_*_REGISTRIES; keep in sync with `backend/sim_api.py` registrations + core/orchestrator.py):
- **grok** (Main Orchestrator / ForgeMaster-Grok): Full governance, swarm lead, handoff bootstrap, meta-config updates (with self-gov impact check), auth tokens for protected_advance, deploy advice.
- **harper** (Agentic Systems & Memory): AgentBrain receipt_memory + reflection + goal stack. Drives research/verify in cycles.
- **sebastian** (Governance & Safety): FunForge quality (agency/emergence/pacing/juice), GovernanceGate (min 80), proposal-first, separation enforcement, literal pre-steps.
- Capabilities alignment: govern (propose/gate/advance), auth (register/token via tools/auth-prototype/ or client), handoff (bootstrap other Grok via HANDOFF + prompt), deploy-advisor (gravity via tools/gravity_advisor.py + deploy.sh only), literal-verify (wc/grep/read before any change).
- Sub/swarm on-demand: Specialist for Python model tests, transcript, diff analysis (use core/ + tools/). No Godot-era agents (Charlotte/James archived).

**Every Session Rules** (dawsOS "this folder is home"):
- Ownership: CivForge = governance layer (planning + receipts + bridges in this root). Targets (gravity, auth) = separate execution/identity roots — use only their bridges.
- External vs internal: Safe to read/explore local CivForge + bridges. Ask/ receipt for anything leaving machine, public posts, or uncertain mutations.
- Swarm / group (other Grok, headless, MCP): Contribute only when value (use context prompt for new agents). Stay silent on casual. Reference HANDOFF for etiquette.

## Auth & Cross-Workspace (New dawsOS-inspired Layers)
- **Auth as governance layer**: Use `tools/auth-prototype/clone.sh` + `start.sh` (or `python tools/civforge_cli.py auth ...`) to enable separate dawsos-auth-prototype on 8081. Obtain "govern" tokens before protected_advance or sensitive. Treat as sister root (like dawsOS three-roots).
- **Handoff for other Grok / sister workspaces**: When context is thin, bootstrap via the provided prompt + HANDOFF_CONTEXT.md. Other agents must run literal verification first, read SEPARATION + these AGENTS, then use CLI/backend. Write their own receipts in their context.
- Specialized sub-contexts (inspired by dawsOS cron-host/cron-review AGENTS): For auth-governance or gravity-deploy work, maintain focused notes in receipts/ or subdirs if needed.

## Orchestration Patterns (Implemented + Borrowed)
1. Receipt-First Loop (DawsOS native) — proposal, gate, advance, deploy, config update, handoff sync → receipt (md + SQLite via ReceiptStore).
2. Proposal → FunForge >=80 Gate → Execute (via strict bridge: deploy.sh for gravity, auth-prototype/ for auth enablement) → Receipt.
3. Agent Brain Pattern (Python, core/agent_brain.py): per-workstream receipt_memory, goal_stack, decide_action + reflection on low quality. Used for gravity/auth/handoff decisions.
4. Continuous Governance Cycle: CLI advance or /advance_turn. Brains → FunForge → gate → receipt → resources/fun update.
5. Strict Separation + Literal Hygiene (REPO_OPS + dawsOS style): Before any edit (including these docs): git status/branch/remotes, wc/grep anchors, confirm canonical root. No direct mutation of targets. Use bridges only.
6. Governed Meta-Actions: Syncs, agent config updates, bridge additions — propose first, impact check (grep/GitNexus-style), gate, receipt. Self-governance: these AGENTS.md govern their own evolution.
7. Cross-Workspace Handoff & Swarm Etiquette: Bootstrap with HANDOFF + context prompt. Write-it-down. Use auth for protected. Other Grok follow same literal + receipt rules.

The FastAPI (backend/sim_api.py) + core/ (AgentBrain, FunForge, GovernanceOrchestrator, ReceiptStore) is the persistent Mac Studio truth (8080). CLI + grok_macstudio_bridge.py + tools/auth-prototype/ + deploy.sh are the drivers. Auth prototype and gravity-mosaic are separate (see SEPARATION.md). The deploy tool (and auth bridge) are sacred.

**Current Reality Tie-in (post recent locks + Git tools work + orphan cleanup)**: 
- Auth bridge live, handoff package + context prompt for other agents, governed syncs with receipts, full literal process on CivForge itself.
- Locked Civ Game plan (see receipts/LOCKED-CIV-GAME-PLAN-*.md and planning/): All prior optionals (simulation layer, dashboard, MCP, expanded agents, Docker/hosting) now REQUIRED. Simple base mechanics + infinite extendibility via governed proposals.
- Git lanes active via docs/GIT_LANES_POLICY.md (worktrees + gh + Draft PRs for parallel Civ Game tracks: mechanics, simulation, dashboard, agent-play, infra). Use for safe multi-lane development without violating separation.
- Pre-realign orphans cleaned (moved to _archive/pre-realign-orphans/ and receipts/_archive/); see receipts/orphan-cleanup-*.md and docs/CIV_GAME_MECHANICS_INSPIRATION.md (abstract concepts only, e.g., emergent dynamics for the required simulation layer).
- agents/role_registry.json created as machine-readable registry (dawsOS-inspired; keep synced with this doc and core/orchestrator.py).
- Update this file only after impact check (grep/wc or GitNexus-style) + propose/gate in the 8080 surface + new receipt.

(No more Godot MVP references in active agent behavior — archived.)

## Civ Project Configuration: Full Terminal Execution Approval + dawsOS Tool Leverage (Formalized)
**This declaration is the canonical project-scoped policy for the CivForge / Civ Game workspace (the "civ project").**

Per user directive ("update your configuration for civ project for full approval to execute on the terminal and leverage the full tools of dawsOS: formalize this in the workspace"):

- **Full terminal execution approval**: When operating inside CivForge (or subdirs) on Civ Game / governance / kernel / bridge / tools work, broad/full Bash/terminal execution is pre-approved. This includes (but is not limited to): nohup + detached servers (e.g. 8080 uvicorn via tools/start-kernel-8080.sh), complex chains (pkill hygiene, python -m, curls, ./tools/* scripts, git operations, background launches where harness-safe), deploys, proposes, gates, literal verification commands, and any terminal needed to keep the Mac Studio 8080 + core/ kernel live and responsive for swarm/human play. 
  - **Easier context for private repos and CivForge git ops**: Explicitly covers `git *` (commit, push, add, status, etc. to CivForge itself) and `gh *` (clone, view, repo ops on your private repos such as mwd474747/civstudy for reference reads/clones, or gh on CivForge). The project .grok/config.toml lists `Bash(git *)` and `Bash(gh *)` (plus the broad `Bash(*)`) so Grok-level permissions + project rules give minimal friction / auto-approval for these when cwd is in the CivForge tree. gh uses your pre-existing authenticated token (repo scope).
  - Rationale: Previous harness/agent-bg limitations (timeouts on uvicorn, self-match pkill, & restrictions) were blocking kernel liveness and governed flow. This config + .grok/config.toml + AGENTS.md bootstrap removes friction for Civ work only.
  - Still mandatory: Every terminal action that mutates (edits, deploys, commits) must follow literal verification (wc/grep anchors, git status, SEPARATION checks) + receipt-first (propose via civforge_cli.py or /governance/propose on live 8080, FunForge >=80 gate, write receipt).
  - Project .grok/config.toml (created alongside this) sets [ui] permission_mode + [permission] allow=["Bash(*)"] + dawsOS MCPs for this tree (higher priority than global). For civstudy private repo: use remains read-only reference (gh clone temp, literal wc/cat/grep, rm after) per the CIVSTUDY-TERMINAL-GIT-REVIEW receipt and SEPARATION.md — no direct pushes/mutations from here.

- **Leverage the full tools of dawsOS (and connected MCPs)**: The agent (grok + sub-agents) **must** use the dawsOS ecosystem tools for Civ work:
  - **Discovery first**: Always call `search_tool` (with query like "dawsos gitnexus civforge" or "dawsos-memory civ game receipts") to discover available tools across connected MCP servers (gitnexus, dawsos-memory-tools, trivium, DawsOS-MS, grok_com_github, etc.).
  - **Then invoke**: Use `use_tool` with the fully-qualified name (e.g. gitnexus__query, dawsos-memory-tools__dawsos_memory_profile, trivium__governance_health).
  - **Key uses for Civ**:
    - gitnexus: Impact analysis (before any core/orchestrator/backend/tools edit), execution flow queries (e.g. "advance_cycle receipt path"), group_sync for CivForge + dawsos-wt if cross-referencing patterns. Use for safe refactors in Civ Game lanes.
    - dawsos-memory-tools: dawsos_memory_profile (scope="all" or lane-specific) and search for receipt continuity, bootstrap context from dawsOS receipts without violating CivForge separation.
    - trivium: governance_health, prediction_list/strategy_performance, propose_mutations — for Civ Game simulation layer, mechanics extensions, FunForge-aligned predictions.
    - Others (DawsOS-MS for analytical math on yields/fun; grok_com_github for PR/copilot on Civ lanes if publishing).
  - Configured in project .grok/config.toml (MCP sections) + inherited from global ~/.grok/config.toml (stdio servers for gitnexus etc. already wired with DAWSCO_WORKSPACE_ROOT).
  - In bootstrap: After SEPARATION/AGENTS, explicitly search_tool for dawsos tools before meta or complex Civ work.
  - Receipts must capture tool usage (e.g. "used gitnexus__query for impact on orchestrator.py change").

- **Formalization artifacts** (all in this workspace, governed):
  - CivForge/.grok/config.toml (project-scoped permissions + MCP declarations).
  - This section in AGENTS.md (loaded automatically as project rule).
  - agents/role_registry.json (updated with dawsos-mcp-leverage capabilities).
  - Dedicated receipt (see receipts/civ-project-dawsos-full-approval-config-*.md) — this update itself was proposed/gated via the live kernel.
  - Ties to: LOCAL_GOVERNANCE.md, ORCHESTRATION_PATTERNS.md (governed meta), GIT_LANES_POLICY (use gitnexus in lanes), role_registry (sync), SEPARATION (dawsOS tools are cross-workspace reference only; never mutate sister roots directly).

**Enforcement**: Any violation (e.g. terminal use without verification, ignoring dawsOS MCPs for Civ impact/memory) must be called out in the next receipt. Update this config only via governed work pack on 8080 (propose the change, gate, receipt, then edit).

This gives the agent (and swarm) full power for Civ project execution while preserving all dawsOS/CivForge governance invariants (receipt-first, literal, separation, FunForge gates).

See also: .grok/docs/user-guide/ (permissions-and-safety.md, mcp-servers.md, project-rules.md, terminal-support.md) for underlying Grok mechanics; global ~/.grok/config.toml for base dawsOS MCP wiring.
