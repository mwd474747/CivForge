# Cursor Execution — WP-GROK-MECH-DISTRICT-001

**Date:** 2026-06-16  
**Label:** `current`  
**Work pack:** Grok planning `WP-GROK-MECH-DISTRICT-001` (district_yield_override)  
**Authority lane:** `cursor`  
**Receipt class:** `execution`  
**Grok PRIME may close against:** this file only (planning-class Grok receipt links here)

---

## Objective

Prove mechanics proposal lane end-to-end on live `:8080`: propose → FunForge gate → apply → `/state` overrides.

---

## Preconditions

```bash
cd ~/CivForge
git rev-parse --short HEAD   # 4b57418
bash tools/start-kernel-8080.sh
```

---

## Execution (literal)

### Propose

```json
POST /game/mechanics/propose
{
  "kind": "district_yield_override",
  "title": "Research campus sci pulse +1",
  "payload": { "district_id": "research-campus", "yield_bonus": { "sci": 3 } },
  "author": "grok_swarm",
  "work_pack_id": "WP-GROK-MECH-DISTRICT-001",
  "rationale": "Tune district pulse sci without new tick module"
}
```

**Result:** proposal `6edc05db`, status `PROPOSED`

### Gate

```json
POST /game/mechanics/gate
{ "proposal_id": "6edc05db", "fun_score_override": 85.0 }
```

**Result:** `approved: true`, `fun_score: 85.0`, status `GATED_APPROVED`

### Apply

```json
POST /game/mechanics/apply
{ "proposal_id": "6edc05db" }
```

**Result:** `applied: true`, detail `district research-campus yield ← {'sci': 3}`

### `/state` after apply

| Field | Value |
|-------|-------|
| `fun_score` | `87.0` |
| `session_phase` | `active` |
| `mechanics_proposals.total` | `1` |
| `mechanics_proposals.recent[0].status` | `APPLIED` |
| `mechanics_overrides.district_yields.research-campus` | `{ "sci": 3 }` |

---

## Validation

```bash
python3 -m pytest tests/ -q                    # 53 passed
bash tools/turnkey-governance-posture.sh       # PASSED
python3 tools/civforge_contract_parity.py      # pass, mcp 16, routes 24
python3 tools/civforge_cli.py status           # includes mechanics_proposals + mechanics_overrides
```

---

## HEAD

**Repo:** `4b57418` on `main` (feature landed `956d251`)

---

## Grok note

Do not re-run or claim these probes from grok.com. Close planning PRIME with link to this receipt only.
