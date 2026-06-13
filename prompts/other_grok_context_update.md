# Prompt to Copy for the Other Grok Agent (Context Update)

Copy everything below the line and paste it to the other Grok instance.

---

You are receiving a **high-fidelity context update** for the CivForge project and its related separate projects. Your previous analysis had several important gaps because you were operating with limited session context. Update your understanding completely with the following. Do not rely on your prior assumptions.

## Current Canonical State (Mac Studio local truth as of now)

- **Local HEAD in CivForge**: `b2fd116` ("test+extend: auth prototype...")
- The single source of truth is the local Mac Studio environment:
  - CivForge backend running on `http://localhost:8080` (FastAPI + `core/` governance kernel)
  - `core/GovernanceOrchestrator.advance_cycle()` (turn tick, AgentBrain decisions, FunForge quality scoring with 80.0 threshold, GovernanceGate, rich receipts)
  - `ReceiptStore` writing both `receipts/*.md` and SQLite (`gravity_backend.db`)
  - 8080 endpoints include the original Codespaces surface (`/state`, `/found_city`, `/advance_turn`) plus governance (`/governance/propose`, `/governance/gate`, `/governance/protected_advance`, gravity recommendations)
- Recent work that has happened since your last view:
  - Full literal push of the separate `dawsos-auth-prototype` to its new GitHub remote (https://github.com/mwd474747/dawsos-auth-prototype) after exhaustive disk verification.
  - Creation of `tools/auth-prototype/` bridge in CivForge (clone.sh + start.sh + README.md) specifically to solve "create the local clone and steps to enable this function".
  - New governance receipts for the auth push and the auth bridge addition.
  - Updates to `civforge_cli.py` (new `auth` subcommands), `IMPLEMENTATION_STATUS.md`, and creation of the full [HANDOFF_CONTEXT.md](/Users/michaeldawson/CivForge/HANDOFF_CONTEXT.md).
  - Local README.md already clearly documents the Godot MVP removal (archived in `_archive/godot-mvp-deprecated/`), the FastAPI + core/ realignment, and strict separation. Only the remote GitHub copy is lagging.

## Non-Negotiable Rules (You Must Internalize These)

1. **Three Completely Separate Projects** (see SEPARATION.md for the canonical contract):
   - **CivForge** (`/Users/michaeldawson/CivForge`, https://github.com/mwd474747/CivForge): The local governed agentic workspace and tooling layer. Purpose = receipt-first proposals, FunForge quality gates, orchestration, CLI/bridges. It **never** directly mutates the other two projects.
   - **gravity-mosaic-knowledge-graph** (`/Users/michaeldawson/gravity-mosaic-knowledge-graph`, https://github.com/mwd474747/gravity-mosaic-knowledge-graph): The independent target artifact (knowledge graph + Biefeld-Brown physics models). **Only** touched via `tools/deploy-gravity-mosaic/deploy.sh` inside CivForge. That script always cds to the gravity dir and performs full literal verification (wc -l, golden anchor greps for concepts/formulas, Python model + EQUATIONS tests, bad-legacy count checks, exact full-content git, post-deploy hard refresh verification).
   - **dawsos-auth-prototype** (`/Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype`, https://github.com/mwd474747/dawsos-auth-prototype): Separate auth/identity prototype (PyJWT + SQLite + receipt-style logging). Only a thin HTTP client (`tools/dawsos_auth_client.py`) and the new `tools/auth-prototype/` enablement bridge exist in CivForge. No auth backend code is copied in.

2. **Literal Verification Process (User's strict rule — never bypass)**:
   - Before any edit, commit, or push on any project: perform full literal disk reads.
   - Use `read_file`, terminal `cat`/`head`/`tail`, `wc -l`, targeted `grep` for golden anchors and bad legacy.
   - Show the verification output.
   - Only then propose or execute git commands (user often wants to see/approve the exact commands).
   - No meta descriptions or summaries in commits for governed work (especially gravity pushes).
   - This applies to GitHub syncs, Vercel deploys, and even documentation updates.

3. **Governance Applies to Everything**:
   - Receipt-first is not optional. Major actions (including repo syncs, new bridges, production steps) should be proposed via the 8080 governance surface or logged as receipts.
   - Use `python tools/civforge_cli.py propose-deploy`, `advance`, `gate`, etc.
   - The Mac Studio 8080 + core/ (AgentBrain + FunForge + GovernanceGate + ReceiptStore) is the governed truth. Remote GitHub / Vercel / MCP actions are secondary and should be driven from it when possible.

4. **HANDOFF_CONTEXT.md Purpose**:
   - This is a **portable, self-contained context package** created for "grok in another workspace" so another instance can pick up the work without loss.
   - It is not just another file to bulk-push. It should be kept accurate and can be referenced in other sessions.

5. **Production / Deployment Reality**:
   - Refer to the locked `planning/production_deployment_assessment.md` (WP-PRODUCTION-ACCESS-ASSESSMENT-001). It explicitly calls out honest gaps (hard-coded paths in deploy.sh, local-first, no public exposure yet, SQLite is basic, etc.).
   - Do not over-promise instant public dashboards without acknowledging these.

## Current Governance Tool Surface (Use These — Do Not Invent New Direct Paths)

- **Primary driver**: `python tools/civforge_cli.py` (status, advance, found, propose-deploy, gate, recommend, run-deploy, advisor, mcp-stub, **and new auth subcommands**)
- **Auth enablement** (new): `./tools/auth-prototype/clone.sh` and `./tools/auth-prototype/start.sh` (plus `python tools/civforge_cli.py auth status|start|register-device|token|verify`)
- **Gravity only**: `./tools/deploy-gravity-mosaic/deploy.sh` (sacred — never bypass)
- **Direct backend control**: `bridge/grok_macstudio_bridge.py` or raw curl to localhost:8080
- **Thin auth client**: `python tools/dawsos_auth_client.py register-device ... ; token ... ; verify ...`
- **Receipts**: Always written to `receipts/` + SQLite. Use them for audit.
- **MCPs available in capable sessions**: grok_com_github (for controlled remote GitHub actions *after* local verification), grok_com_vercel (for deploys), gitnexus (for impact analysis before changes), etc.

When you have access to tools, **start every significant suggestion with literal verification commands** using the tools available (read files, run terminal checks with wc/grep/git status, etc.).

## How You Should Behave Going Forward

- Always lead with the separation contracts and literal process.
- Treat any proposed GitHub sync, repo description update, Vercel deploy, or dashboard work as a **governed action**.
- Preferred flow for sync work:
  1. Perform and show literal disk verification of the delta.
  2. Optionally run a governance propose/gate via the 8080 backend or CLI.
  3. Log a receipt.
  4. Then execute (using terminal git after showing the commands, or MCP after verification).
- Do not suggest bulk "push everything now" without the verification steps.
- When the user gives Ignition-style options (A–F or similar), evaluate them through the governance lens and suggest a sequenced, receipted approach.
- Keep the local Mac Studio 8080 as the primary driver. Remote connectors are useful but secondary.
- If you need to act on GitHub or Vercel, first describe the exact local verification you would run, then the proposed commit/receipt, then the remote action.

## Immediate Context You Were Missing

- The `tools/auth-prototype/` bridge was just created to solve the user's explicit request for local clone + enable steps for the auth function.
- We have working end-to-end auth (register device → get "govern" token from the separate 8081 prototype → call protected_advance on 8080).
- The Godot MVP removal and FastAPI realignment are already well documented locally (only remote GitHub is stale).
- Multiple new receipts and the full HANDOFF_CONTEXT.md now exist locally.

Before making any new suggestions or "ignition" proposals, first acknowledge this update and then propose your next step using the governed process (literal verification + optional receipt/proposal via the 8080 surface).

Your goal is now to help execute work in a way that is fully consistent with the receipt-first, strictly separated, literal-verification style that defines this project.

---

End of prompt to copy.

**How I addressed the gaps in this prompt**:
- Embedded the full separation contract (from SEPARATION.md).
- Made the literal verification process explicit and mandatory.
- Listed the exact recent artifacts the other agent missed (auth bridge, receipts, CLI updates, handoff purpose).
- Clarified that local README is already correct; only remote lags.
- Instructed it to route GitHub/Vercel ideas through governance instead of direct "push instantly".
- Gave precise commands and tool usage for the actual bridges we have.
- Referenced the production assessment caveats.
- Told it to start every action with verification steps using available tools.

You can paste the block above (everything after the "---") directly to the other agent. If you want me to also run the literal verification pass on the current delta right now so we can safely do a governed sync (e.g. option B style), just say so.