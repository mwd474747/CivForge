# CivForge Autonomous Agent Orchestration v1.0 (realigned)

## Core Patterns (now implemented in pure Python core/ + FastAPI)
- **Master Work Pack Executor**: `python tools/civforge_cli.py advance` or POST /advance_turn (orchestrator + brains + FunForge + gate + receipt).
- **Agent Brain Pattern** (Python): `core/agent_brain.py` — receipt_memory, goal_stack, decide_action(state), record_receipt + reflection on low fun/quality. Used for gravity work decisions (research vs. verify vs. propose deploy vs. govern).
- **Swarm Coordination**: Grok main + registered sub-agents (Harper, Sebastian, ...) in the orchestrator. Decisions logged as receipts.
- **Continuous Governance Loop**: Advance cycle → FunForge quality score → gate (min 80) → rich receipt to disk + backend state → update workstream "resources" / fun_score. Mirrors the earlier pasted FastAPI /advance_turn.
- **Autonomous / Headless Operation**: `bridge/headless_observer.py` + `tools/civforge_cli.py` drive the running backend from terminal or other agents. No Godot required.
- **Gravity Deploy Governance**: Proposals and gates happen here. Real execution is **always** the strict `tools/deploy-gravity-mosaic/deploy.sh` (literal verification on the separate project).

**Current Priorities** (post realign):
1. Core Python patterns (done: AgentBrain, FunForge, Governance, Orchestrator, ReceiptStore).
2. FastAPI workspace matching the earlier version (state shape + /state /found_city /advance_turn preserved + governance extensions).
3. CLI + headless observer as the driver.
4. Tight integration of the gravity deploy tool with pre/post receipts and gate checks.
5. All work on the separate gravity-mosaic project remains under the literal disk + verification contract.
