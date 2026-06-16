# Cursor Execution — WP-GROK-POLICY-002 (envoy_network)

**Date:** 2026-06-16  
**Label:** `current`  
**Work pack:** `receipts/work-pack-grok-policy-002.md`  
**Grok planning PRIME:** WP-GROK-POLICY-002 (planning-class)  
**Authority lane:** `cursor`  
**Receipt class:** `execution`

---

## Summary

Landed **`envoy_network`** tier-2 diplomacy policy per Grok planning envelope. Recorded **propose → gate** on `:8080` (planning kind — **apply correctly rejected**). Gameplay visible in `civstudy_reference` and player unlock flow.

---

## Planning lane on `:8080` (literal)

```json
POST /game/mechanics/propose
{
  "kind": "policy_definition",
  "title": "tier-2 diplomacy branch envoy_network",
  "payload": {
    "id": "envoy_network",
    "branch_id": "diplomacy",
    "tier": 2,
    "effect": "diplomatic_outpost_network"
  },
  "work_pack_id": "WP-GROK-POLICY-002"
}
```

| Step | Result |
|------|--------|
| Propose | `c1c0f132` → `PROPOSED` |
| Gate | `GATED_APPROVED`, fun_score **86.0** |
| Apply | **Rejected** — `planning-only kind` (expected) |

---

## Code landed

| Path | Change |
|------|--------|
| `backend/civstudy_metadata.py` | `envoy_network` policy (tier 2, influence_cost 12) |
| `backend/civstudy_mechanics_bridge.py` | `apply_policy_effect` → `envoy_network` flag |
| `backend/multi_agent_state.py` | Softer betrayal drift + lower watch break odds (12→7) when envoy active |
| `backend/game_actions.py` | Per-policy `influence_cost` support |
| `tests/test_envoy_network_policy.py` | Metadata, unlock, planning gate, catalog cost |

**Coexistence:** `alliance_cap_3` unchanged (hard cap); `envoy_network` is soft diplomacy modifier.

---

## Gameplay proof

- `GET /state` → `civstudy_reference.policy_tree` includes **`envoy_network`**
- Player unlock at turn ≥12 with `open_negotiation` → sets `policy_flags.envoy_network`
- Catalog shows **12 influence** unlock cost for envoy

---

## Validation

```bash
python3 -m pytest tests/test_envoy_network_policy.py tests/ -q   # 57 passed
bash tools/turnkey-governance-posture.sh                          # PASSED (after game reset)
```

---

## Grok closure

Grok may close **WP-GROK-POLICY-002** planning PRIME by linking this file only. Tag Grok receipt: **planning**. Tag this file: **current**.

**HEAD:** _(filled at commit)_
