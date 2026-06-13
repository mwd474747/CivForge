# Local Governance for CivForge (dawsOS-inspired, realigned)

**Proposal-first. Quiet-by-default (local 8080 backend). Receipts mandatory for all (including meta).**

## Core Principles (Borrowed + Adapted from dawsOS)
- **Proposal / Gate / Receipt / Execute**: All work (gravity targets, auth enablement, this repo's docs/bridges/syncs, handoff artifacts) starts as proposal. FunForge quality gate (>=80). Execute only via strict bridges. Always produce receipt (md + SQLite via ReceiptStore). Evidence reconstructable from receipts + config.
- **Literal Verification First** (REPO_OPS + dawsOS hygiene): Before any change (edits, commits, pushes, even to these docs): `git status --short`, branch/remotes, `wc -l` + `grep` golden anchors ("separate projects", "literal verification", "FunForge", "auth-prototype", "handoff"), confirm canonical root. Impact check (manual grep or GitNexus-style if available). No raw/direct mutation of targets.
- **Strict Separation** (see SEPARATION.md): CivForge = governance layer only. Gravity-mosaic = independent target (only via deploy.sh). dawsos-auth-prototype = sister identity root (only via thin client + tools/auth-prototype/ bridge). Three roots — do not conflate. Use handoff artifacts for cross-workspace.
- **Auth as Governance Layer**: Optional but first-class. Enable separate prototype (8081) via bridge. Use for "govern" scope tokens on protected actions (e.g. /governance/protected_advance). Register via client or `civforge_cli.py auth`.
- **Agent Role Registry Alignment** (see AGENTS.md): grok (main), harper (memory), sebastian (safety). Capabilities explicit. Keep runtime (sim_api.py registrations + orchestrator) in sync with conceptual. Sub/swarm on-demand.
- **Write-It-Down / No Mental Notes**: Agent decisions, context, lessons → receipts/ or daily notes. Text > brain. Bootstrap other Grok with HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md (the "birth certificate" / context sync).
- **Self-Governance / Meta**: Updates to agent configs (this file, AGENTS.md, ORCHESTRATION_PATTERNS.md, skills/) are governed meta-actions. Propose, impact (literal + GitNexus-style), gate, receipt before push. These files govern their own evolution.
- **Quiet-by-Default + Swarm Etiquette**: Local-first (Mac Studio 8080 truth). For external/other Grok / headless / MCP: use context prompt + bootstrap section in AGENTS.md. Contribute only with value; follow literal + receipt rules. Group chat / swarm: smart etiquette (dawsOS style).

## Runtime Reality vs Conceptual (Alignment Check)
- **Current mode**: Governed single + swarm (main Grok + registered sub-agents in orchestrator).
- **Verified capabilities** (local shell, git, 8080 backend, auth client, bridges, literal tools): Yes for operator work, repo, governance, DawsOS-pattern application.
- **Limitations**: No unlimited authority. Verify before non-trivial (use CLI propose/gate). Not yet full public exposure (see production assessment).
- **Default targets**: CivForge root for governance/bridges. Separate roots for gravity/auth (bridges only). Receipts/ for artifacts.

## Operating Procedure (Every Action)
1. Bootstrap/literal verify (AGENTS.md rules + REPO_OPS).
2. Propose if mutation (CLI or /governance/propose).
3. Gate (FunForge or manual).
4. Execute via bridge only.
5. Receipt (always).
6. For cross-workspace: handoff via artifacts + prompt.

**Grok is trusted federated agent #001** (with sub-agents per registry). All under receipt-first, proposal-first, literal, separated governance.

See: AGENTS.md (full roles/bootstrap), ORCHESTRATION_PATTERNS.md (loops), SEPARATION.md (roots), docs/patterns/borrowable-governance-patterns.md (reuse), HANDOFF_CONTEXT.md (other agents), tools/auth-prototype/ + deploy.sh (bridges). 

Update this spec only via governed process (propose + receipt).