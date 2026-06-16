# Game Mechanics Wiring Inventory (v1)

**Generated:** 2026-06-15  
**Scope:** Every registered mechanic, CivStudy metadata effect, and civ-layer behavior — wired vs partial vs missing.  
**Label:** `report-only`

---

## Summary

| Layer | Wired | Partial | Missing |
|-------|-------|---------|---------|
| Core mechanics lanes (military/economic/cultural) | 3 ticks | 0 | 0 |
| CivStudy bridge modules | 4 ticks | 0 | 0 |
| Policy tree (9 policies) | 5 | 3 | 1 |
| Discovery forks (4) | 3 | 1 | 0 |
| Districts (4) | 1 active pulse | 3 player-select | 0 |
| Cultural chains (3) | 3 progress | 0 | 0 |
| Multi-agent civ layer | 6 behaviors | 4 | 3 |

---

## Turn pipeline (wired)

```
POST /advance_turn
  → orchestrator.advance_cycle()
  → run_turn_simulation()
       → tick_multi_agent_state()      # map, alliances, negotiations, victory drift
       → mechanics_registry.tick_all() # core lanes + civstudy modules
       → sync_victory_milestones(game_state)  # live truth + progress
  → maybe_emit_victory_receipt()
  → session_phase == "epilogue" blocks further advance (409)
```

---

## Core mechanics lanes (`core/mechanics_registry.py`)

| Module | Tick behavior | Status | Notes |
|--------|---------------|--------|-------|
| `military` | +0–2 strength/turn; legacy point every 5 turns | **Wired** | Drives `legacy-doctrine` fork prereq |
| `economic` | +1 institution every 4 turns | **Wired** | Overlaps `institution_charter` policy |
| `cultural` | +0–3 influence spread/turn; chain counter every 6 turns | **Wired** | Overlaps `influence_spread` policy |

**Missing wiring:** lanes do not read policy flags except via separate CivStudy ticks; no player-directed lane investment.

---

## CivStudy bridge modules (`backend/civstudy_mechanics_bridge.py`)

| Module | Tick cadence | Status | What it does |
|--------|--------------|--------|--------------|
| `civstudy_district` | every 3 turns | **Wired** | Applies `active_district_id` yield bonuses to player resources |
| `civstudy_discovery` | every tick | **Wired** | Unlocks forks when prereqs met; applies lane bonuses |
| `civstudy_cultural` | every 4 or 6 turns | **Wired** | Progresses cultural chains; `symposium_chain` → cadence 4 |
| `civstudy_policy_tree` | every 4 turns | **Wired** | Auto-unlocks policies when turn/resource gates met |

**Missing wiring:** player cannot choose district or policy branch; all unlocks are automatic ticks.

---

## Policy tree — per-policy wiring

| Policy | Branch | Declared effect | Wiring status | Implementation |
|--------|--------|-----------------|---------------|----------------|
| `open_negotiation` | Diplomacy T1 | Extra negotiation slot / lower cost | **Wired** | Waives 2 influence cost on `POST /game/negotiate` |
| `alliance_cap_3` | Diplomacy T2 | Raise active alliance soft cap | **Wired** | Cap 2 → 3 for player alliances on accept |
| `betrayal_watch` | Diplomacy T3 | Surface betrayal risk in HUD | **Partial** | HUD banner + alliance risk boost; no betrayal *event* |
| `institution_charter` | Economy T1 | +1 economic institution / 4 turns | **Wired** | `eco.institutions += 1` on unlock |
| `trade_route_map` | Economy T2 | Sci-trade yield bonus | **Partial** | `trade_routes += 1`; no sci yield hook |
| `yield_surge` | Economy T3 | +5% lane yield bonus | **Wired** | `yield_bonus_pct += 5` |
| `symposium_chain` | Culture T1 | Start cultural chains earlier | **Wired** | Cultural tick cadence 6 → 4 |
| `influence_spread` | Culture T2 | +2 influence spread / 6 turns | **Wired** | `influence_spread += 2` on unlock |
| `festival_receipts` | Culture T3 | Cultural milestones +2 victory | **Wired** | Chain completion bonus +2 when flag set |

---

## Discovery forks — per-fork wiring

| Fork | Prereq | Unlocks | Status | Implementation |
|------|--------|---------|--------|----------------|
| `sci-trade-route` | sci≥8, prod≥6 | `economic_institution_boost` | **Wired** | `yield_bonus_pct += 5` |
| `receipt-quorum` | verify_budget≥7 | `governance_quorum_milestone_hint` | **Missing effect** | Unlocks in log only; no milestone/quorum hook |
| `legacy-doctrine` | military_strength≥45 | `military_legacy_accelerator` | **Wired** | `legacy_points += 1` |
| `cross-faction-symposium` | influence_spread≥15 | `cultural_event_chain_bonus` | **Wired** | `event_chains += 1` |

---

## Districts — per-district wiring

| District | Specialization | Yield bonus | Status | Gap |
|----------|----------------|-------------|--------|-----|
| `governance-quarter` | receipt_audit | verify_budget+1, influence+1 | **Wired** (default active) | Player cannot switch district |
| `systems-forge` | production_guild | prod+2, sci+1 | **Partial** | Metadata only unless `active_district_id` changed |
| `diplomatic-embassy` | negotiation_hub | influence+2 | **Partial** | No `POST /game/district/select` |
| `research-campus` | discovery_lab | sci+2 | **Partial** | No player selection |

---

## Cultural event chains

| Chain | Stages | Rewards | Status |
|-------|--------|---------|--------|
| `festival-of-receipts` | 3 | influence+3, victory+2 | **Wired** |
| `symposium-of-systems` | 3 | influence+4, victory+3 | **Wired** |
| `archivist-pilgrimage` | 3 | influence+2, sci+2 | **Wired** (no victory bonus) |

**Missing:** chains start only via cultural tick; no player trigger; `symposium-of-systems` name unrelated to `symposium_chain` policy beyond cadence.

---

## Multi-agent civ layer (`backend/multi_agent_state.py`)

| Mechanic | Status | Notes |
|----------|--------|-------|
| Map tile ownership drift | **Wired** | Contested/neutral capture every 3 turns |
| Alliance betrayal risk drift | **Wired** | Random drift; elevated event log >40% |
| AI negotiation offers | **Wired** | Every 4 turns |
| Player negotiate + respond | **Wired** | Influence cost; alliance formation; +8 victory |
| Alliance soft cap | **Wired** | 2 default, 3 with `alliance_cap_3` |
| Victory progress per turn | **Wired** | +1–3 random per advance |
| Milestone truth | **Wired** | Alliances, map share ≥40%, quorum, progress |
| Session epilogue | **Wired** | Blocks advance at victory; reset clears |
| Betrayal event (alliance breaks) | **Missing** | Risk displayed only |
| Defeat / lose condition | **Missing** | No fun floor or betrayal collapse |
| Player map claim / move | **Missing** | No `POST /game/map/*` |
| Direct policy unlock spend | **Missing** | Policies auto-unlock on ticks only |

---

## Governance kernel (non-civ but affects “game”)

| Surface | Status | Notes |
|---------|--------|-------|
| `POST /advance_turn` | **Wired** | Full cycle + sim |
| `POST /found_city` | **Wired** | Prod cost, territories, receipt |
| `POST /game/reset` | **Wired** | Fresh session |
| `POST /governance/propose` + `/gate` | **Wired** | FunForge gate; proposals persist |
| `CIVFORGE_PUBLIC_MODE` auth | **Wired** | Token on mutators when exposed |
| `CIVFORGE_REQUIRE_AUTH` | **Wired** | Forces token on mutators locally too |
| Player agent in orchestrator cycle | **Missing** | Brains only |
| `:8081` JWT identity | **Missing** | Nexus satellite key path only |

---

## Telemetry / observability gaps

| Field | Status |
|-------|--------|
| `victoryProgress` | **Wired** |
| `victoryOutcome` | **Wired** (this slice) |
| `sessionPhase` | **Wired** (this slice) |
| Per-policy flags in Nexus | **Missing** |
| Mechanics lane deltas per turn | **Partial** (`mechanicsSummary` snapshot only) |

---

## Recommended wiring order (next slices)

1. **`receipt-quorum` fork** → tie to governance quorum milestone or +progress when `verify_budget` high  
2. **`trade_route_map`** → add sci yield on district pulse or economic tick  
3. **`betrayal_watch`** → betrayal event when risk > 55% under active watch  
4. **`POST /game/district/select`** → influence cost to change `active_district_id`  
5. **`POST /game/policy/unlock`** → player spends influence to pick branch tier  
6. **Defeat condition** → `fun_score` floor or alliance collapse at risk 100%  
7. **Player map action** → claim adjacent neutral tile (influence cost)

---

## Related docs

- `docs/GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md`
- `docs/MECHANICS_TICK_CONTRACT_V1.md`
- `backend/civstudy_metadata.py` — source of truth for policy/fork/district definitions
