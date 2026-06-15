# Work Pack: Swarm Alignment P1 Example

**ID:** `WP-SWARM-ALIGN-P1-001`  
**Lane:** `lane/governance-meta`  
**Owner:** Grok swarm (planning) → **Cursor** (execution)  
**Label:** `current`

## Swarm alignment

| Field | Value |
|-------|-------|
| `receipt_class` | `execution` |
| `authority_lane` | `cursor` |
| `side_effect_class` | `local_git` |
| `human_review_required` | `false` |
| `required_receipt_links` | `receipts/cursor-execution-swarm-align-p1-*.md`, `receipts/civforge-contract-parity-latest.json` |

## Objective

Land P1 swarm-field alignment: WP template, role_registry chief_of_staff mapping, contract parity swarm checks.

## Acceptance criteria

```bash
python3 -m pytest tests/test_civforge_governance_tools.py -q
python3 tools/civforge_contract_parity.py
git rev-parse --short HEAD
```

## Closure

This file demonstrates the template; see `docs/WORK_PACK_TEMPLATE_V1.md`.
