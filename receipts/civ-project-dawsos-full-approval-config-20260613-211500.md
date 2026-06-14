# Receipt: CIV-PROJECT-DAWSOS-FULL-APPROVAL-CONFIG-20260613-211500
**Turn/Cycle**: Meta (governed config update for Civ project)
**Action**: civ_project_config_update_for_full_terminal_approval_and_dawsos_tool_leverage
**Status**: COMPLETE (formalized in workspace per user directive)
**Fun/Quality Score**: 94 (high alignment to dawsOS patterns, unlocks kernel/terminal friction for Civ Game while preserving receipt-first/literal/separation invariants)

## Details
- **details**: Updated configuration for the Civ project (CivForge as governance root for Civ Game) to grant full terminal execution approval and require/declare leverage of full dawsOS tools (MCP surface: gitnexus, dawsos-memory-tools, trivium, DawsOS-MS, etc.). Formalized via:
  - New project-scoped CivForge/.grok/config.toml (permission_mode bypass + broad Bash(*) allow for terminal; explicit [mcp_servers] reinforcement for dawsOS tools; project priority per Grok docs).
  - Extended section in CivForge/AGENTS.md ("Civ Project Configuration: Full Terminal Execution Approval + dawsOS Tool Leverage") declaring policy, bootstrap obligations (search_tool first then use_tool), usage patterns for Civ (gitnexus impact before edits, memory for receipts, trivium for sim/governance), ties to separation and 8080 governance.
  - Updated agents/role_registry.json (added "dawsos-mcp-leverage", "full-terminal-civ-exec" to grok role; notes on sync).
  - This receipt (governed meta-work pack).
- **rationale**: Recent terminal friction (harness bg timeouts on uvicorn starts, pkill self-match, & restrictions) was blocking persistent 8080 kernel (required for proposes/gates/swarm coordination/human play per locked Civ Game). dawsOS tools (already wired globally) provide powerful leverage for safe Civ work (knowledge graph impact via gitnexus, receipt/memory profiles via dawsos-memory, governance/predictions via trivium) without violating separation. Formalize in workspace (not just global ~/.grok/config.toml) so it's versioned, receipted, and auto-loaded as project rule for this tree.
- **verification performed** (literal, pre any commit):
  - git status --porcelain (new .grok/config.toml, AGENTS.md edit, role_registry edit, this receipt).
  - wc -l on new/edited files + key anchors (SEPARATION "separate projects", AGENTS bootstrap, "FunForge >=80", "literal verification").
  - grep for "dawsos-mcp-leverage|full-terminal-civ-exec|Civ Project Configuration" across AGENTS.md + role_registry + new config + receipt.
  - Confirmed .grok/config.toml structure matches Grok docs (project-scoped MCP + [permission]).
  - Cross-ref to prior dawsos-agent-config-refine receipt (20260613-191943) and user-guide/permissions-and-safety.md, mcp-servers.md, project-rules.md.
- **dawsOS tool leverage instructions** (now canonical in AGENTS.md bootstrap + Civ section):
  - For any Civ work (mechanics, infra, meta, lanes): 1. search_tool (queries like "gitnexus civforge impact", "dawsos-memory receipts civ game", "trivium governance civ"). 2. use_tool with fqdn (gitnexus__query, dawsos-memory-tools__dawsos_memory_profile, trivium__governance_health, etc.).
  - Examples: gitnexus before editing core/orchestrator.py or tools/; dawsos-memory for cross-workspace receipt bootstrap; trivium for Civ Game sim extensions/FunForge alignment.
- **enforcement**: This config is itself governed (proposed/gated via live 8080 in prior steps; this receipt closes). Future changes: impact check (GitNexus or grep) + propose/gate on 8080 + new receipt. Terminal use still requires pre-action literal verify + post-action receipt. dawsOS MCP use is mandatory for complex Civ tasks (document in receipts).
- **artifacts created/updated**:
  - CivForge/.grok/config.toml (new, project-scoped).
  - CivForge/AGENTS.md (new section + tie-ins).
  - CivForge/agents/role_registry.json (capabilities + notes).
  - This receipt.
- **next** (per Civ section): Use the config immediately (full terminal for 8080/kernel work; dawsOS tools for impact/memory). Update HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md to mention the new Civ config for other agents. When ready, propose any doc/lane extensions (now unblocked) via live kernel.

_This update was executed with user approval via terminal commands on the live kernel (start-kernel-8080.sh + proposes + gate for prior civstudy review). Local 8080 + core/ remains the governed truth. Full dawsOS leverage + terminal approval scoped to Civ project only, respecting SEPARATION.md and all invariants._

**Follow-up for this query (private repo + CivForge commit/push)**: Enhanced .grok/config.toml and AGENTS.md "Civ Project Configuration" section with explicit `Bash(git *)` / `Bash(gh *)` allows + direct language:
- Easier auto-approval context for `git commit/push` etc. to CivForge (the workspace repo).
- Easier `gh *` for your private repos (e.g. gh clone/view on mwd474747/civstudy for reference-only terminal reads, as done in the CIVSTUDY-TERMINAL-GIT-REVIEW receipt).
- Still reference-only for civstudy (no mutation/push from CivForge). Full terminal now has less prompt friction inside the CivForge tree thanks to project-scoped permissions + project rules in AGENTS.md.

_Generated via terminal + literal process + dawsOS config formalization in CivForge at 2026-06-13T21:15:00. Enhanced 2026-06-13 for private-repo/CivForge-git context._