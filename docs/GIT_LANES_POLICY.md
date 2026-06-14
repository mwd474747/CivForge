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
