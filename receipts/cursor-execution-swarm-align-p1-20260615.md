# Cursor execution — swarm alignment P1

**Date:** 2026-06-15  
**WP:** `WP-SWARM-ALIGN-P1-001`  
**Label:** `prototype-only`

## Scope

- `docs/WORK_PACK_TEMPLATE_V1.md` — side_effect_class, required_receipt_links
- `agents/role_registry.json` — openclaw-chief-of-staff, forge-coordinator, dawsos_role_map
- `civforge_contract_parity.py` — swarm alignment lint
- Cross-refs in swarm-class, borrowable patterns, mechanics WP

## Validation

```bash
python3 -m pytest tests/test_civforge_governance_tools.py -q
python3 tools/civforge_contract_parity.py
```

## HEAD

Set after commit on `main`.
