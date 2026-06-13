# Gravity Mosaic Deploy Helper (CivForge Integration)

This is a **CivForge-governed deployment project** for the separate `gravity-mosaic-knowledge-graph` static site.

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

## Agent / Orchestration Usage
Use CivForge's primary agent (Grok) and sub-agents to govern deployments:

- **Proposal**: Agent proposes changes to gravity-mosaic (e.g. new nodes/edges for more physics concepts).
- **Governance Receipt**: Log a receipt in `receipts/gravity-mosaic-deploy-YYYYMMDD.md`
- **Execute**: Run `./tools/deploy-gravity-mosaic/deploy.sh` (or have the agent call it via bridge).
- **Verification Receipt**: After push, use browser tools (or simulate) and log results.
- **Simulation**: Use CivForge's Godot layer or Python bridge to simulate "what if" deployments.

See CivForge root files:
- AGENTS.md (roles: Grok main orchestrator, Harper for systems, etc.)
- ORCHESTRATION_PATTERNS.md
- PROJECT_MANIFESTO.md
- setup_hybrid.sh (for full hybrid activation)

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
- Add a Python skill in `skills/` that parses the gravity graph and proposes new anti-gravity concept nodes.
- Create a receipt template in `receipts/`.
- Integrate with CivForge's `bridge/` for Grok to autonomously propose + deploy (with human governance gate).
- Add Godot visualization of the gravity knowledge graph as a "simulation layer".

This keeps the gravity-mosaic as a clean, separate artifact while using CivForge as the intelligent deployment and governance layer on this computer.

Built with the same agentic patterns as CivForge itself.
