# Game Mechanics Wiring Inventory (v2 — complete)

**Updated:** 2026-06-16  
**Scope:** CivForge game engine mechanics — all metadata effects wired.  
**Label:** `prototype-only` (passes 46+ pytest; live kernel smoke recommended)

---

## Status: engine mechanics complete

All policy-tree policies, discovery forks, districts (player-select), cultural chains, core lanes, multi-agent behaviors, player actions, defeat/victory session phases, and MCP tools are **wired**.

Remaining **non-engine** gaps (out of scope for this slice): `:8081` JWT identity, full PlayerAgent orchestrator brain, 3D/Godot client.

---

## Player actions (`backend/game_actions.py`)

| Action | Endpoint | Cost | Status |
|--------|----------|------|--------|
| Select district | `POST /game/district/select` | 3 influence | **Wired** |
| Unlock policy | `POST /game/policy/unlock` | 5/8/12 by tier | **Wired** |
| Claim map tile | `POST /game/map/claim` | 4 influence | **Wired** |
| Action catalog | `GET /game/actions` | — | **Wired** |

Dashboard: district/policy panel + clickable claimable map tiles.

MCP: `civforge_select_district`, `civforge_unlock_policy`, `civforge_claim_tile` (12 tools total).

---

## Policy tree — all wired

| Policy | Effect | Implementation |
|--------|--------|----------------|
| `open_negotiation` | Waive negotiate influence | `negotiation_influence_cost()` |
| `alliance_cap_3` | Soft cap 2→3 | `alliance_soft_cap()` on accept |
| `betrayal_watch` | HUD + betrayal break events | Risk ≥55 + 12% break/turn under watch |
| `institution_charter` | +1 institution | Lane on unlock |
| `trade_route_map` | Sci-trade yield | District pulse + economic tick +sci |
| `yield_surge` | +5% yield | Lane on unlock |
| `symposium_chain` | Earlier cultural chains | Cadence 6→4 |
| `influence_spread` | +2 spread | Lane on unlock |
| `festival_receipts` | +2 victory on chain complete | Cultural tick bonus |

Policies unlock via **auto tick** OR **player spend** (`POST /game/policy/unlock`).

---

## Discovery forks — all wired

| Fork | Effect |
|------|--------|
| `sci-trade-route` | `yield_bonus_pct +5` |
| `receipt-quorum` | +5 progress on unlock; +2/3 turns on district pulse when verify_budget≥7 |
| `legacy-doctrine` | `legacy_points +1` |
| `cross-faction-symposium` | `event_chains +1` |

`receipt-quorum` also counts toward **governance quorum** milestone when verify_budget high.

---

## Districts — all wired

Player selects via `POST /game/district/select`. Active district pulses every 3 turns with yield bonuses + trade-route sci + receipt-quorum progress.

---

## Session outcomes

| Phase | Trigger | Behavior |
|-------|---------|----------|
| `active` | default | Normal play |
| `epilogue` | `outcome: victory` | Advance blocked (409); reset to continue |
| `defeat` | fun&lt;35, isolation, betrayal collapse, stall | Advance blocked; `defeat-outcome-*.md` receipt |

Defeat reasons: `fun_floor`, `diplomatic_isolation`, `betrayal_collapse`, `stalled_progress`.

---

## Multi-agent layer — all wired

Map drift, betrayal risk + **break events**, AI negotiations, player negotiate/respond, alliance cap, milestone truth, map claim, defeat checks, player cycle decision in orchestrator receipt.

---

## MCP tools (12)

`civforge_status`, `civforge_advance_turn`, `civforge_reset_game`, `civforge_found_city`, `civforge_negotiate`, `civforge_negotiate_respond`, `civforge_what_if`, `civforge_governance_propose`, `civforge_governance_gate`, `civforge_select_district`, `civforge_unlock_policy`, `civforge_claim_tile`.

---

## Validation

```bash
cd ~/CivForge
python3 -m pytest tests/ -q
bash tools/turnkey-governance-posture.sh
```

---

## Related

- `docs/GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md`
- `docs/GAME_PLAY_GUIDE_V1.md`
- `docs/MECHANICS_TICK_CONTRACT_V1.md`
