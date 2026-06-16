# Work Pack: Grok Mechanics Proposal 001

**ID:** `WP-GROK-MECHANICS-PROPOSE-001`  
**Lane:** `lane/civ-game-mechanics` + `lane/grok-swarm-planning`  
**Owner:** Grok swarm (planning) → **Cursor** (code kinds) / **kernel** (runtime kinds)  
**Label:** `planning` until Cursor execution receipt  
**Supersedes:** simulation-only `WP-GROK-MECHANICS-SIM-001` closure claims for *new* mechanic authoring

## Swarm alignment

| Field | Value |
|-------|-------|
| `receipt_class` | `planning` |
| `authority_lane` | `grok_swarm` |
| `side_effect_class` | `planning_only` (Grok) → `local_kernel` (runtime apply via MCP) |
| `human_review_required` | `false` |
| `required_receipt_links` | `receipts/swarm-mechanics-propose-001-closure-*.md`, `receipts/cursor-execution-*.md` |

Template: `docs/WORK_PACK_TEMPLATE_V1.md`  
Proposal lane: `docs/GAME_MECHANICS_SWARM_PROPOSAL_LANE_V1.md`

---

## Objective

Use the **mechanics proposal lane** (not just `advance_turn` / `what_if`) so Grok swarm can propose governed mechanic updates:

- Runtime patches (district yields, lane params, cadence, session params)
- Planning payloads for new policies/forks/tick modules (Cursor implements)

---

## Grok swarm steps (grok.com — planning only)

Author proposals in work-pack prose; Cursor or MCP agent applies on `:8080`.

### Example runtime proposals (MCP)

```json
{
  "kind": "district_yield_override",
  "title": "Research campus sci +1",
  "payload": { "district_id": "research-campus", "yield_bonus": { "sci": 3 } },
  "work_pack_id": "WP-GROK-MECHANICS-PROPOSE-001"
}
```

```json
{
  "kind": "param_override",
  "title": "Trade route sci yield +2",
  "payload": { "trade_route_sci_bonus": 2 }
}
```

### Example planning proposals (Cursor WP)

```json
{
  "kind": "policy_definition",
  "title": "Envoy network tier-2 diplomacy",
  "payload": {
    "id": "envoy_network",
    "branch_id": "diplomacy",
    "tier": 2,
    "effect": "One free negotiate every 3 turns"
  }
}
```

Flow: `civforge_propose_mechanics` → `civforge_gate_mechanics` → `civforge_apply_mechanics` (runtime) or export to Cursor WP (planning).

---

## Cursor execution (when planning kinds land)

1. Add policy/fork to `backend/civstudy_metadata.py`
2. Wire effect in `backend/civstudy_mechanics_bridge.py` / `backend/game_session.py`
3. Register tick module in `core/mechanics_registry.py` if `tick_module` kind
4. pytest + update `docs/GAME_MECHANICS_WIRING_INVENTORY_V1.md`

---

## Verification (mandatory)

```bash
python3 -m pytest tests/test_mechanics_proposals.py -q
python3 -m pytest tests/ -q
bash tools/turnkey-governance-posture.sh
git rev-parse --short HEAD
```

### Receipt must include

- `mechanics_proposals` from live `GET /state`
- At least one `APPLIED` runtime proposal OR linked Cursor WP for planning kind
- Real `fun_score` from `/state` (not invented)

---

## Forbidden

- Claiming simulation ticks = proposing new mechanics
- Auto-applying `policy_definition` without Cursor code
- wt promotion claims

---

## Closure

`receipts/swarm-mechanics-propose-001-closure-YYYYMMDD.md`
