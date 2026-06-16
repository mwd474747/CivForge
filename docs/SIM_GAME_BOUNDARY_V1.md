# Simulation vs Game Mechanics Boundary (v1)

**Updated:** 2026-06-16  
**Work packs:** WP-SIM-GAME-CLARITY-001/002, WP-DEEP-DIVE-ANALYSIS-003, WP-SIM-GAME-OVERLAP-ANALYSIS-004  
**Label:** `prototype-only`

---

## 1. Boundary review

| Layer | Responsibility | Key modules |
|-------|----------------|-------------|
| **Simulation (orchestration)** | Turn loop, map/alliances/negotiations, competition scoring, milestones, FunForge gate, receipts, `:8082` telemetry | `core/orchestrator.py`, `backend/simulation_boundary.py`, `backend/multi_agent_state.py`, `backend/competition_modes.py`, `backend/turn_simulation.py` (sim phase) |
| **Game mechanics (pluggable rules)** | Districts, policies, CivStudy ticks, military/economic/cultural lanes | `core/mechanics_registry.py`, `backend/civstudy_mechanics_bridge.py`, `backend/game_actions.py` |

**Turn order (enforced):**

```
orchestrator.advance_cycle()
  → run_turn_simulation()
       → run_simulation_layer()      # simulation only
       → registry.pass_through_tick() # mechanics only
```

Audit keys on `/state.simulation_boundary`: `_simulation_boundary`, `_mechanics_tick_audit`.

---

## 2. Overlap points (honest)

| Location | Overlap | Status |
|----------|---------|--------|
| `tick_multi_agent_state` mutates `victory_progress`, map, alliances | Simulation layer, not registry | **Documented** — kept in `run_simulation_layer` |
| `mechanics_lanes` defaults in `telemetry_extra_from_state` | Read-only fallback init | Low risk; no tick logic |
| CivStudy bridge registered in registry | Correct — metadata-driven mechanics | **Clean** |
| FunForge scoring in orchestrator | Simulation/governance, not civ rules | **By design** |

**Subtle leak (mitigated):** Previously `run_turn_simulation` called `tick_multi_agent_state` then `tick_all` without explicit layer labels. Now separated with audit metadata.

---

## 3. Replacement feasibility

**Can simulation be replaced entirely by MechanicsRegistry?**

| Verdict | **Partial — not yet full replacement** |
|---------|----------------------------------------|
| Effort | Medium–high (multi_agent needs `decisions` context; competition modes need orchestrator hooks) |
| Gain | Simpler mental model, one tick entry point |
| Loss | Orchestrator coupling, harder to keep `:8082` thin-bridge separation |

**Recommended path (low-risk):**

1. Keep `run_simulation_layer` explicit (current).
2. Register *new* rules as mechanics modules (`reg.register(...)`).
3. Optional future WP: wrap `tick_multi_agent_state` as registry module `"diplomacy_layer"` with decision injection.

---

## 4. Proposed refactor WP draft — WP-GROK-REFRACTOR-SIM-001

| Step | Action |
|------|--------|
| 1 | Register `diplomacy_layer` tick wrapper calling `tick_multi_agent_state` |
| 2 | Move competition tick to registry module `"competition"` |
| 3 | Reduce `run_simulation_layer` to milestone sync only |
| 4 | Add pytest asserting zero direct `mechanics_lanes` writes outside registry |
| 5 | Preserve receipt-first + CivStudy extensibility |

**Not in scope for this slice** — documented for Grok planning lane.

---

## 5. Agent control primitives

| Field / route | Purpose |
|---------------|---------|
| `/state.agent_controls` | Active governor, override flag, per-agent goals |
| `POST /game/agent/select` | Select active agent |
| `POST /game/agent/directive` | Issue directive (player override) |
| `POST /game/agent/autonomy` | Toggle autonomous vs directed control |

Entity: **AgentGovernor** — `agent_id`, `goal`, `control_level`, `player_override`, `score`, `last_directive`.

---

## 6. Competition modes

| Mode | ID | Win condition broadcast |
|------|-----|-------------------------|
| Standard | `none` | — |
| PvA Duel | `pva_duel` | First to 50 duel points |
| Free-For-All | `free_for_all` | Leader at turn 30 |
| Alliance League | `alliance_league` | Bloc standings every 10 turns |
| Shared-Victory Co-op | `shared_victory_coop` | Joint progress ≥ 100 |

Routes: `POST /game/competition/mode`, `GET /game/competition/spectator`.

---

## 7. Extensibility registries (deep-dive items)

| Registry | Module | Purpose |
|----------|--------|---------|
| `CorpusCardRegistry` | `backend/corpus_card_registry.py` | One-line CivStudy card add |
| `DashboardComponentRegistry` | `backend/dashboard_components.py` | Tab/panel metadata |
| `MechanicsRegistry.pass_through_tick` | `core/mechanics_registry.py` | Mechanics boundary enforcement |
| `enrich_telemetry_payload` | `backend/telemetry_enrich.py` | Metadata-only `:8082` enrich |

---

## Validation

```bash
cd ~/CivForge
python3 -m pytest tests/test_sim_game_clarity_bundle.py tests/test_sim_game_boundary.py -q
python3 -m pytest tests/ -q
```
