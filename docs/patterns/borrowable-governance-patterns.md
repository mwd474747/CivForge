# Borrowable Governance Patterns from CivForge

These patterns are designed to be repeatable and borrowable for governing other independent projects (like gravity-mosaic or future ones). They live in CivForge as the workspace, but can be adapted.

## 1. Strict Project Separation (SEPARATION.md template)
- Declare two projects clearly.
- Only narrow, verified bridge (literal checks, no direct mutation).
- See SEPARATION.md in root for template.

## 2. Receipt-First Governance Loop
- Proposal → FunForge quality gate (target >=80) → Execute (via bridge) → Detailed Receipt (markdown + SQLite).
- Core: core/governance.py, core/orchestrator.py, core/receipts.py (with optional SQLite for persistence).

## 3. Agent Brain Pattern (core/agent_brain.py)
- Per-"workstream" receipt memory + goal stack.
- decide_action based on state + history + reflection on low quality.
- Used for autonomous decisions (research/verify/deploy/govern).

## 4. FunForge Quality Scoring (core/fun_forge.py)
- Calculate "fun/quality" from agency, emergence, pacing, juice (adaptable metrics).
- Auto-reject below threshold, trigger refactor.
- Reusable for any work output: code, docs, deploys, research.

## 5. Strict Literal Deploy Bridge (tools/deploy-*/ )
- The deploy script lives in the governance workspace.
- Always operates on the target project's directory.
- Enforces: full literal disk reads, wc/grep for anchors/features, model tests, zero bad legacy, exact git ops, post-deploy verification.
- Never bypass.

## 6. Local FastAPI Governance Backend (backend/sim_api.py + core/)
- Persistent workspace state (player/ai_civs reframed as workstreams).
- Endpoints: /state, /found_city (init work pack), /advance_turn (governance cycle), /governance/propose/gate.
- Wire in core/ for brains, scoring, gates.
- Use for terminal/CLI/headless or future dashboard.

## 7. Terminal-First Drivers
- CLI (tools/civforge_cli.py): status, advance, propose, gate, recommend, advisor.
- Headless observer / Grok bridge for autonomous or swarm control.
- All drive the backend without UI.

## 8. Local Persistence + .gitignore Hygiene
- SQLite for state/receipts that survive restarts (core/receipts.py).
- .gitignore: db, logs, pyc, _archive (optional), ephemeral receipts.
- Keep committed receipts/ as audit trail.

## 9. Civ Game Layer as Governed Extension (Locked)
- Simple core mechanics (turns, resources/yields, founding actions, FunForge fun/quality scoring) that are infinitely extendible via pluggable modules (MechanicsRegistry, strategies, events, victory conditions).
- All extensions developed through the governed play loop (propose as work packs → FunForge gate on emergence/pacing/juice → integrate).
- Human play: Required gamified Command Center dashboard (agent avatars, receipt timeline, workstream map, propose/gate/quality HUD).
- Agent play: Full API/MCP (auth-gated)/CLI/handoff support — external agents register and participate.
- See: planning/production_deployment_assessment.md (required elements), ROADMAP.md (Civ Game track), AGENTS.md (expanded role registry: GameMechanicDesigner, PlayerAgent, MechanicsSimulator, UICoordinator, InfraGovernor; plus agents/role_registry.json), docs/GIT_LANES_POLICY.md (parallel lanes), docs/CIV_GAME_MECHANICS_INSPIRATION.md (abstract historical concepts only for the required simulation layer), receipts/LOCKED-CIV-GAME-PLAN-*.md and orphan-cleanup-*.md.
- No legacy: Pure new Python; feeds existing orchestrator/receipts/gate. Separation preserved. Pre-realign artifacts consolidated to _archive/.

## 10. Git Lanes for Parallel Development (Governed Meta)
- Use Git Worktrees + gh CLI + Draft PRs for safe parallel lanes (e.g., lane/civ-game-mechanics, lane/simulation-layer, lane/dashboard, lane/agent-play, lane/infra-required).
- All lane work follows literal verification, propose/gate/receipt.
- Policy doc: docs/GIT_LANES_POLICY.md (do not edit SEPARATION.md for this).
- Policy: docs/GIT_LANES_POLICY.md (do not put branching rules in SEPARATION.md).
- See AGENTS.md (governed meta-actions, bootstrap), ORCHESTRATION_PATTERNS.md.

## Usage for Other Projects
1. Copy/adapt core/ patterns into new governance workspace.
2. Create SEPARATION.md.
3. Build deploy-*/ bridge with literal rules specific to target.
4. Run backend + CLI for governance.
5. Use receipts/ for all history.
6. For game-like layers: Adopt Civ Game patterns (simple extendible mechanics + governed proposals + role registry + lanes).
7. Cross-workspace: Use HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md for bootstrap.

These keep workspaces clean, projects separate, and work auditable/low-waste. Extend the patterns for "Civ Game as first-class governed playable layer".
