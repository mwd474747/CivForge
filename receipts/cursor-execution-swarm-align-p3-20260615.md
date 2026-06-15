# Cursor execution — swarm alignment P3

**Date:** 2026-06-15  
**WP:** `WP-SWARM-ALIGN-P3-001`  
**side_effect_class:** `local_kernel`

## Scope

- Rename in-kernel AgentBrain id `grok` → `forge-coordinator` (`core/swarm_join.py`, `sim_api.py`, orchestrator)
- `agents/role_registry.json` — `kernel_agent_id` aligned
- Contract parity — sim registration + kernel id checks
- wt candidate: `planning-inputs.v0.json` + `CIVFORGE_SWARM_CLASS_POINTER_V1.md` (uncommitted, OpenClaw lane)

## Validation

```bash
python3 -m pytest tests/test_orchestrator_join.py tests/test_civforge_governance_tools.py -q
python3 tools/civforge_contract_parity.py
bash tools/turnkey-governance-posture.sh
```

## HEAD

Set after commit.
