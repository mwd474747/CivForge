---
name: grok-civforge-intelligence
description: CivForge governance intelligence skill for Grok (or other agents). Use the local 8080 backend + core/ patterns for receipt-first orchestration of separate projects (gravity-mosaic, auth-prototype). Enforces literal verification, proposal/gate, auth bridge for protected actions, handoff bootstrap, and self-governance on meta (config updates, syncs).
metadata:
  {
    "civforge": {
      "requires": ["python3", "curl", "git (for literal verify)", "localhost:8080 (backend)", "localhost:8081 (auth if enabled)"],
      "bridges": ["tools/civforge_cli.py", "tools/auth-prototype/", "tools/deploy-gravity-mosaic/deploy.sh", "bridge/grok_macstudio_bridge.py"],
      "handoff": "HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md"
    }
  }
---

# Grok CivForge Intelligence (dawsOS-inspired skill)

## Roles & Layers (align with AGENTS.md role registry)
| Agent/Layer | Purpose | CivForge Surface |
|-------------|---------|------------------|
| Grok (main orchestrator) | Lead proposals, cycles, handoff bootstrap, meta-gov (with impact check) | 8080 + CLI + bridges |
| Harper (memory/systems) | AgentBrain receipt_memory, reflection, goal stack | core/agent_brain.py |
| Sebastian (governance/safety) | FunForge >=80, GovernanceGate, separation + literal enforcement | core/governance.py + fun_forge.py |
| Auth / Handoff specialist | Enable sister auth-prototype, cross-workspace context sync | tools/auth-prototype/ + client + HANDOFF |

## Environment / Bootstrap (mandatory every session)
- CivForge root as canonical governance workspace.
- 8080 backend running (uvicorn sim_api:app).
- For auth: enable via `tools/auth-prototype/clone.sh && start.sh` (separate 8081 root).
- For handoff/other Grok: read HANDOFF_CONTEXT.md + prompts/other_grok_context_update.md first.
- Literal verify before any action: git status, wc/grep anchors ("separate projects", "FunForge", "literal verification", "auth-prototype", "handoff"), confirm roots per SEPARATION.md.

## How to Use (Core Loop + Borrowed dawsOS Patterns)
1. **Bootstrap**: Read SEPARATION.md, latest receipts/, AGENTS.md bootstrap section, role registry. Run literal checks (no mental notes — write to receipts/).
2. **Propose / Decide**: Use `python tools/civforge_cli.py propose-deploy` or /governance/propose. AgentBrain (via core/) for autonomous (research/verify/govern/handoff). Record receipt.
3. **Gate**: FunForge quality (agency/emergence/pacing/juice) or /governance/gate. Min 80 for execute. For protected: obtain "govern" token via auth bridge/client.
4. **Execute**: Only via bridges (auth-prototype/ for enable, deploy.sh for gravity, CLI for meta). Never direct on targets.
5. **Receipt**: Always (ReceiptStore writes md + SQLite). "Text > brain". Use for continuity/handoff.
6. **Cross-workspace / Swarm**: Bootstrap other Grok with the context prompt + HANDOFF. Follow swarm etiquette (contribute value only; reference AGENTS for rules). For external: use grok_macstudio_bridge.py or raw 8080 calls after auth.
7. **Self-gov / Meta**: Config updates (these skills, AGENTS, etc.), syncs, bridge changes — treat as governed work packs. Impact check first (grep/wc or GitNexus-style). Propose/gate/receipt before push.
8. **Validation**: Use CLI status/advance/auth, backend /state /integrate, literal on disk. For auth sister: health on 8081 + token flows.

## Capabilities (Verified Local)
- Local execution, git/literal tools, 8080/8081 interaction, receipt creation, proposal/gate via CLI/backend.
- Limitations: Bridges only for targets. Verify auth/gov before protected. No unlimited external (follow dawsOS external/internal).

## Example Commands (Terminal-First Driver)
```bash
cd /Users/michaeldawson/CivForge
python tools/civforge_cli.py auth status          # enable sister auth
python tools/civforge_cli.py auth register-device ...
python tools/civforge_cli.py auth token <id> govern
python tools/civforge_cli.py propose-deploy
python tools/civforge_cli.py advance             # full cycle with brains + FunForge + gate + receipt
curl -H "Authorization: Bearer $TOK" -X POST http://localhost:8080/governance/protected_advance
```

See: AGENTS.md (bootstrap + registry + etiquette), ORCHESTRATION_PATTERNS.md (loops + meta), LOCAL_GOVERNANCE.md (full spec), SEPARATION.md (roots), HANDOFF_CONTEXT.md (other agents), core/ (live AgentBrain etc.), tools/ bridges.

**Write receipts for all intelligence actions.** Update this skill only via governed process (propose + literal + receipt). 

This skill makes Grok (or sister agents) a first-class governed operator for CivForge's receipt-first, separated, literal, auth-enabled orchestration of independent projects. (dawsOS patterns: receipts as evidence, registries, bootstrap, SKILL structure, self-gov.)