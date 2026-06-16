# Work Pack: Send Envoy Player Action (Grok planning)

**ID:** `WP-GROK-POLICY-003`  
**Lane:** `lane/civ-game-mechanics` + `lane/grok-swarm-planning`  
**Owner:** Grok swarm (planning) → **Cursor** (execution)  
**Label:** `planning` — no Cursor execution receipt yet

---

## Swarm alignment

| Field | Value |
|-------|-------|
| `receipt_class` | `planning` |
| `authority_lane` | `grok_swarm` |
| `side_effect_class` | `planning_only` |
| `human_review_required` | `false` |
| `required_receipt_links` | `receipts/cursor-execution-wp-grok-policy-003-*.md` (future) |

Template: `docs/WORK_PACK_TEMPLATE_V1.md`

---

## Objective

Extend **`envoy_network`** policy with a player action **`send_envoy`** that spends influence to soften betrayal risk on a chosen alliance for N turns. Grok authors the planning envelope; Cursor lands `game_actions.py` + tick hook + tests.

**Depends on:** `WP-GROK-POLICY-002` (`envoy_network` metadata + flags — **landed**).

---

## Planning proposal envelope (on `:8080` — gate only)

```json
POST /game/mechanics/propose
{
  "kind": "code_change",
  "title": "Player action send_envoy under envoy_network",
  "payload": {
    "description": "POST /game/diplomacy/send_envoy {alliance_id} — 6 influence, -15 betrayal risk for 3 turns",
    "target_files": ["backend/game_actions.py", "backend/multi_agent_state.py", "frontend/index.html"]
  },
  "work_pack_id": "WP-GROK-POLICY-003",
  "author": "grok_swarm",
  "rationale": "Makes envoy_network tactically visible beyond passive drift softening"
}
```

**Expected:** propose → gate ≥78 → apply **rejected** (planning kind) → Cursor implements.

---

## Cursor execution checklist (when assigned)

| Item | Acceptance |
|------|------------|
| `POST /game/diplomacy/send_envoy` | Requires `policy_flags.envoy_network`, costs 6 influence |
| Effect | Target alliance `betrayal_risk -= 15` (floor 0) for 3 turns |
| Dashboard | Button in Player Actions when envoy unlocked |
| MCP | Optional `civforge_send_envoy` (update contract parity + GAME_PLAY_GUIDE) |
| Tests | `tests/test_send_envoy_action.py` |
| Receipt | `receipts/cursor-execution-wp-grok-policy-003-YYYYMMDD.md` |

**Out of scope for v1:** `shared_intel`, 25% negotiation bonus (defer to WP-GROK-POLICY-004).

---

## Grok PRIME closure rules

1. Tag receipt **planning** until Cursor execution receipt exists with real `git HEAD`
2. Do not claim apply → APPLIED for `code_change`
3. Cite live `/state` `policy_flags.envoy_network` after Cursor lands code

---

## Verify (Cursor runs after implementation)

```bash
cd ~/CivForge
python3 -m pytest tests/test_send_envoy_action.py tests/ -q
bash tools/validate-game.sh --read-only
bash tools/turnkey-governance-posture.sh
```
