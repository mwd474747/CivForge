# Cursor execution — governance hardening + swarm class + dawsos-nexus canon

**Date:** 2026-06-15  
**Lane:** Cursor local executor (`docs/EXECUTION_LANE_V2.md`)  
**Label:** `prototype-only` until Mike confirms live posture after push

---

## Scope

1. OpenClaw governance hardening (proposal/gate persistence, posture builders, poller/kernel screen)
2. dawsos-nexus naming canon (retired active `nexus_ctrl_*` docs)
3. Swarm class gap doc (`CIVFORGE_SWARM_CLASS_V1.md`) — CivForge dawsOS-shaped ≠ wt registry swarms
4. `validate-game.sh --read-only` for non-mutating reviews
5. wt pointer update (swarm class cross-ref)

---

## Validation (read-only probes — no turn advance)

```bash
python3 -m pytest tests/test_multi_agent_state.py tests/test_civstudy_metadata.py \
  tests/test_civstudy_mechanics_bridge.py tests/test_civforge_governance_tools.py -q
bash tools/validate-game.sh --read-only
python3 tools/civforge_governance_posture.py
python3 tools/civforge_poller_posture.py
python3 tools/civforge_contract_parity.py
```

---

## Live posture at commit time (GET /state — no advance)

- turn: `76`
- fun_score: `86.6`
- status: `active`
- SQLite receipts: ~320 (per prior posture)
- posture artifacts: governance/parity/poller/receipt-index `pass`

---

## HEAD

`b06326a` on `main` (pushed to origin)
