# Gravity Mosaic Deploy Helper

**Important**: Gravity-mosaic and CivForge are two completely separate projects.

This is the **strict, literal-verification deployment bridge** from the CivForge governance workspace into the independent `gravity-mosaic-knowledge-graph` project.

CivForge provides proposals, quality gates (FunForge), and receipts. The actual changes and git operations on gravity-mosaic happen only inside this helper, which always operates on the separate project's directory with full disk-based verification.

## Purpose
- Provides a safe, receipt-driven way to deploy updates to https://github.com/mwd474747/gravity-mosaic-knowledge-graph (and its GitHub Pages live site).
- Enforces the strict Process Rules established for the gravity-mosaic project:
  - Local disk = single source of truth
  - Full literal verification (wc, grep for anchors + features + 0 bad legacy) before any commit/push
  - Only exact full-content git operations
  - Post-deploy browser-tool verification
  - No meta descriptions, summaries, or placeholders in commits/pushes
- Integrates with CivForge's hybrid architecture (DawsOS receipts, governance, Grok agents, orchestration patterns).

## Location in CivForge
`tools/deploy-gravity-mosaic/`

This follows CivForge's modular structure (tools/, integrations/, receipts/, skills/, governance/).

## Quick Start (on this computer)
1. Ensure CivForge is your active workspace: `cd /Users/michaeldawson/CivForge`
2. Run the deployer:
   ```bash
   ./tools/deploy-gravity-mosaic/deploy.sh
   ```
3. The script will:
   - Run all verifications
   - Stage only the changed files
   - Commit with the full descriptive message
   - Push to origin main
4. Hard refresh the live site after push: https://mwd474747.github.io/gravity-mosaic-knowledge-graph/

## Agent / Orchestration Usage (realigned)
Use CivForge's FastAPI governance workspace + Python core (AgentBrain, FunForge, GovernanceGate, Orchestrator) + CLI/headless observer to drive proposals and receipts.

Typical governed flow for the separate gravity-mosaic project:

1. Make changes ONLY inside /Users/michaeldawson/gravity-mosaic-knowledge-graph (full literal reads on disk).
2. Use the CivForge backend (or CLI) to propose + gate the work:
   - curl http://localhost:8080/governance/propose ...
   - python tools/civforge_cli.py recommend
   - python tools/civforge_cli.py advance   (runs brains + FunForge quality + gate + receipt)
3. **Execute the actual deploy ONLY with the strict tool**:
   `./tools/deploy-gravity-mosaic/deploy.sh`
   (It performs wc -l, golden anchor greps, Python model + EQUATIONS tests, bad-legacy = 0, then literal git add/commit/push.)
4. Log verification receipt (browser hard-refresh + tool confirmation) back into receipts/.

The old Godot MVP (playable 4X UI) has been removed. All agentic patterns now live in pure Python core/ + the FastAPI workspace that matches the earlier Codespaces-style backend the user requested.

See CivForge root:
- README.md (realigned intent)
- backend/sim_api.py + core/ (AgentBrain, FunForge, etc.)
- tools/civforge_cli.py and bridge/headless_observer.py
- governance/ and receipts/ (first-class)
- AGENTS.md / ORCHESTRATION_PATTERNS.md (updated)

## Files in this Helper
- `deploy.sh` — The enforced deployment runner (verifs + literal git + post notes).
- `README.md` — This file.
- (Future) `receipts/`, `skills/deploy-verifier.py`, `governance/deploy-policy.md`

## Linking the Separate Project
The actual gravity-mosaic lives at:
`/Users/michaeldawson/gravity-mosaic-knowledge-graph`

It has been git-initialized with the correct remote during this setup.

All changes to the gravity-mosaic (new formula nodes, physics research extensions, UI fixes) should be made there, then deployed **only** through this CivForge helper to maintain governance.

## Next Steps / Ideas (CivForge Style)
- Add Python skills in `skills/` that parse the gravity graph (via literal reads) and propose new concept/formula nodes or transcript extensions.
- Receipts for every governed cycle are written by the backend + ReceiptStore.
- The `bridge/headless_observer.py` + CLI already let Grok propose + gate work; real execution always goes through the deploy tool after human review of the literal state on the separate gravity project.

This keeps the gravity-mosaic as a clean, separate artifact while using CivForge as the intelligent deployment and governance layer on this computer.

Built with the same agentic patterns as CivForge itself (now implemented in the FastAPI workspace + core/ Python after the aggressive realign that removed the Godot MVP layer).
