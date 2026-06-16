# Game Mechanics Wiring Inventory (v2 — complete)

**Updated:** 2026-06-16  
**Scope:** CivForge game engine mechanics — all metadata effects wired.  
**Label:** `prototype-only` (passes 80 pytest; live kernel smoke recommended)

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
| Send envoy | `POST /game/send_envoy` | 6 influence | **Wired** — +10 negotiation success bonus on target alliance (turn-limited shield) |
| Action catalog | `GET /game/actions` | — | **Wired** |

| Dashboard | district/policy panel + clickable map + **mechanics proposals tab** |

MCP: `civforge_select_district`, `civforge_unlock_policy`, `civforge_claim_tile`, `civforge_send_envoy` (**17 tools** total — see below).

---

## Policy tree — all wired

| Policy | Effect | Implementation |
|--------|--------|----------------|
| `open_negotiation` | Waive negotiate influence | `negotiation_influence_cost()` |
| `alliance_cap_3` | Soft cap 2→3 | `alliance_soft_cap()` on accept |
| `envoy_network` | Softer betrayal drift + lower watch break odds | `multi_agent_state` when tier-2 unlocked (12 influence) |
| `shared_intel` | +25% negotiation success when active | `trust_erosion.negotiation_success_rate()` + HUD rates (10 influence) |
| `betrayal_watch` | HUD + betrayal break events | Risk ≥55 + 12% break/turn under watch |
| `institution_charter` | +1 institution | Lane on unlock |
| `trade_route_map` | Sci-trade yield | District pulse + economic tick +sci |
| `yield_surge` | +5% yield | Lane on unlock |
| `symposium_chain` | Earlier cultural chains | Cadence 6→4 |
| `influence_spread` | +2 spread | Lane on unlock |
| `festival_receipts` | +2 victory on chain complete | Cultural tick bonus |

Policies unlock via **auto tick** OR **player spend** (`POST /game/policy/unlock`). **11 policies** total (diplomacy 5, economy 3, culture 3).

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

**Defeat sim seed:** `POST /game/reset` with `{"seed_profile":"defeat_cascade"}` applies low-fun posture (turn 22, fun 30, broken alliance) and finalizes `fun_floor` defeat + `defeat-outcome-*.md` receipt for review sims.

---

## `/state` observability (batch-005)

| Field | Purpose |
|-------|---------|
| `victory_hud` | Progress %, cultural path, defeat warnings, milestones |
| `trust_erosion` | Per-agent `negotiation_success_rates`, alliance risk tiers |
| `mechanics_proposals` / `mechanics_overrides` | Proposal lane + applied `param_override` |
| `civstudy_reference` | Read-only policy/fork/district catalog (includes `shared_intel`, **12 corpus cards**, adjacency synergies) |

---

## Multi-agent layer — all wired

Map drift, betrayal risk + **break events**, AI negotiations, player negotiate/respond, alliance cap, milestone truth, map claim, defeat checks, player cycle decision in orchestrator receipt.

---

## MCP tools (17)

Play/governance: `civforge_status`, `civforge_advance_turn`, `civforge_reset_game`, `civforge_found_city`, `civforge_negotiate`, `civforge_negotiate_respond`, `civforge_send_envoy`, `civforge_what_if`, `civforge_governance_propose`, `civforge_governance_gate`, `civforge_select_district`, `civforge_unlock_policy`, `civforge_claim_tile`.

Mechanics proposal lane: `civforge_propose_mechanics`, `civforge_gate_mechanics`, `civforge_apply_mechanics`, `civforge_list_mechanics_proposals`.

See `docs/GAME_MECHANICS_SWARM_PROPOSAL_LANE_V1.md` for propose → gate → apply flow.

---

## Mechanics proposal lane — wired

| Kind class | Examples | Apply on kernel |
|------------|----------|-----------------|
| Runtime | `lane_param`, `district_yield_override`, `tick_cadence_override`, `param_override` | Yes (after FunForge gate ≥78) |
| Planning | `policy_definition`, `fork_definition`, `tick_module`, `code_change` | No — Cursor code land (e.g. `envoy_network` via WP-GROK-POLICY-002) |

Routes: `POST /game/mechanics/propose|gate|apply`, `GET /game/mechanics/proposals`. `/state` exposes `mechanics_proposals` + `mechanics_overrides`.

---

## Validation

```bash
cd ~/CivForge
bash tools/start-kernel-8080.sh
python3 -m pytest tests/ -q
bash tools/validate-game.sh --read-only
bash tools/turnkey-governance-posture.sh
python3 tools/civforge_contract_parity.py
```

---

## Related

- `docs/GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md`
- `docs/GAME_PLAY_GUIDE_V1.md`
- `docs/MECHANICS_TICK_CONTRACT_V1.md`
