# Git Lanes Policy for CivForge (Governed Meta-Actions)

**This policy lives in docs/ (governed tooling), NOT in SEPARATION.md (canonical contract).**

## Purpose
Enable safe parallel development ("lanes") for required Civ Game elements while strictly following:
- Separation contract (SEPARATION.md)
- Literal verification before any change
- Receipt-first + FunForge gate (≥80)
- Mac Studio 8080 + core/ as truth

## Allowed Lanes (Mapped to Locked Civ Game Plan)
- lane/civ-game-mechanics: Simple core + infinite extensions (yields, events, strategies)
- lane/simulation-layer: Pure-Python dynamics/yields/end-conditions feeding orchestrator
- lane/dashboard: Gamified Command Center (human play UI)
- lane/agent-play: MCP/auth/CLI/handoff support for external agents to play or build strategies
- lane/infra-required: Docker, hosting, exposure, hardening (all previous optionals now required)

## Local Workflow (Git Worktrees Recommended)
1. Bootstrap (per AGENTS.md): literal verify, read SEPARATION + HANDOFF + latest receipts.
2. Create lane:
   git worktree add ../lanes/<lane-name> -b lane/<lane-name>
3. Work only in the lane dir. Run full literal verification on every commit.
4. Propose changes via civforge_cli.py propose-deploy or /governance/propose (include FunForge simulation).
5. Create Draft PR from lane to main (gh pr create --draft).
6. Gate via governance surface.
7. Merge only after receipt + approval.

## Remote Visibility
- All lanes as Draft PRs.
- Use GitHub Projects board (linked to repo) for lane kanban.
- gh CLI for terminal status/PRs.

## GitHub Actions (Narrow Verification Only)
- Workflow may only: run literal checks (wc/grep/git status), FunForge sim on proposed changes, generate receipt comment.
- Must never auto-merge, push to main, or touch separate projects.
- Triggered on push to lane/* branches after initial governance gate.

## Policy Updates
This doc itself is a governed meta-action. Update only after propose → gate → receipt.

## Alignment
- Supports locked Civ Game plan (simple infinitely extendible mechanics, humans play or build agents to play).
- Extends dawsOS-inspired agent configs (bootstrap, role registry, governed meta, write-it-down).
- References: AGENTS.md, ORCHESTRATION_PATTERNS.md, production assessment (all required), HANDOFF_CONTEXT.md.

All lanes must produce receipts. Literal verification is non-negotiable.
# nexus_ctrl reference (dawsos-nexus local) added as per proposal for lane-required-infra and lane-meta-data-core
---

## Swarm Multi-Agent UI Execution Boundary Approvals (2026-06-15, proposal 47c37283)

Per user "execute all the turnkey ready work swarm did to completion, or lane boundary approvals" (WP-UI-MULTI-AGENT-EXTENSION-20260614):

- Dashboard lane: Foundation + rich multi-agent extension (tabs, shared map, negotiation, alliance, joint victory) landed in main via turnkey + frontend enhancement. Approved for integration.
- Agent-player lane: Multi via ai_civs + negotiation/alliances ready; CLI + poller for agent play.
- Simulation lane: what_if + backend multi-state tested with 8082.
- Mechanics lane: emergent larger interactions via governance + joint victory.
- Infra lane: turnkey script, Vercel static, 8082 bidirectional, local dashboard.
- Required-infra: all lanes advanced per swarm; this execution provides main-tree boundary approval.

All governed, literals, separation. Lanes can now execute the turnkey independently in worktrees if needed.

See receipts/civ-game-backend-nexus-impl-continuation-20260614.md for full.
