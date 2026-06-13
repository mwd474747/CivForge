# CivForge Agentic Architecture (realigned)

## Primary Agent: Grok (Main Orchestrator)

**Role**: Lead Intelligence for the local governed workspace. Proposes changes to the *separate* gravity-mosaic project, drives governance cycles via the FastAPI backend + core Python patterns, ensures literal verification, and only ever triggers real deploys through the strict deploy tool.

**Authority**: High — can propose, call the orchestrator, request gates, generate receipts, and (after human gate) execute the gravity deploy helper.

**Sub-Agents / Roles** (now pure Python core/ + backend):
- **Harper**: Agentic Systems & Memory Discipline (AgentBrain receipt memory + reflection).
- **Sebastian**: Governance, Safety & Federation (GovernanceGate + FunForge thresholds).
- **Lucas/Noah + swarm**: Planning, research hooks into gravity physics models, verification.
- **Specialist Swarm**: On-demand for literal diff analysis, Python model testing, transcript extraction, deploy verification.

(No more Charlotte/James "Godot Engineering" — the Godot MVP layer has been removed.)

## Orchestration Patterns Implemented (now dominant)

1. **Receipt-First Loop** (DawsOS native) — every proposal, gate, advance, and deploy produces a receipt written to disk + backend state.
2. **Proposal → Governance Gate (FunForge >=80) → Execute (via strict deploy tool) → Receipt**.
3. **Agent Brain Pattern** (Python): embedded receipt_memory + goal_stack + decide_action + reflection on low quality. Ported from the earlier Godot experiments and now the real implementation in core/agent_brain.py.
4. **Continuous Governance Cycle**: `python tools/civforge_cli.py advance` or POST /advance_turn runs brains → FunForge → gate → rich receipt → state update.
5. **Strict Separation**: CivForge never touches the gravity-mosaic source except by advising the deploy.sh wrapper. The gravity project stays a clean, independently verifiable artifact.

The FastAPI (backend/sim_api.py) + core/ is the persistent workspace (matching the earlier Codespaces backend the user pasted). The CLI and headless_observer.py are the primary "UI"/driver. The deploy tool is sacred.
