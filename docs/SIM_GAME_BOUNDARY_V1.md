# Simulation vs Game Mechanics Boundary (v1)

**Updated:** 2026-06-16  
**Work packs:** WP-SIM-GAME-CLARITY-001/002, WP-DEEP-DIVE-ANALYSIS-003, WP-SIM-GAME-OVERLAP-ANALYSIS-004  
**Label:** `prototype-only`

---

## 1. Boundary review

| Layer | Responsibility | Key modules |
|-------|----------------|-------------|
| **Simulation (orchestration)** | Milestone sync after mechanics, FunForge gate, receipts, `:8082` telemetry | `core/orchestrator.py`, `backend/simulation_boundary.py`, `backend/turn_simulation.py` |
| **Game mechanics (pluggable rules)** | Diplomacy/competition, districts, policies, CivStudy ticks, military/economic/cultural lanes | `core/mechanics_registry.py`, `backend/mechanics_layer_modules.py`, `backend/civstudy_mechanics_bridge.py`, `backend/game_actions.py` |

**Turn order (enforced — WP-GROK-REFRACTOR-SIM-001 landed):**

```
orchestrator.advance_cycle()
  → run_turn_simulation()
       → game_state["_turn_decisions"] = decisions
       → registry.pass_through_tick()  # diplomacy_layer, competition, lanes, civstudy
       → run_simulation_layer()        # milestones only
       → pop _turn_decisions
```

Audit keys on `/state.simulation_boundary`: `_simulation_boundary`, `_mechanics_tick_audit`.

---

## 2. Overlap points (honest)

| Location | Overlap | Status |
|----------|---------|--------|
| `tick_multi_agent_state` / `tick_competition` | Registered as `diplomacy_layer` + `competition` mechanics modules | **Landed** — `backend/mechanics_layer_modules.py` |
| `mechanics_lanes` defaults in `telemetry_extra_from_state` | Read-only fallback init | Low risk; no tick logic |
| CivStudy bridge registered in registry | Correct — metadata-driven mechanics | **Clean** |
| FunForge scoring in orchestrator | Simulation/governance, not civ rules | **By design** |

**Subtle leak (mitigated):** Previously `run_turn_simulation` called `tick_multi_agent_state` then `tick_all` without explicit layer labels. Now separated with audit metadata.

---

## 3. Replacement feasibility

**Can simulation be replaced entirely by MechanicsRegistry?**

| Verdict | **Partial — diplomacy/competition now in registry; milestones remain orchestration** |
|---------|----------------------------------------|
| Effort | Medium–high (multi_agent needs `decisions` context; competition modes need orchestrator hooks) |
| Gain | Simpler mental model, one tick entry point |
| Loss | Orchestrator coupling, harder to keep `:8082` thin-bridge separation |

**Recommended path (low-risk):**

1. Keep `run_simulation_layer` explicit (current).
2. Register *new* rules as mechanics modules (`reg.register(...)`).
3. Milestone sync remains orchestration-only (`run_simulation_layer`); diplomacy/competition are registry modules (WP-GROK-REFRACTOR-SIM-001 landed).

---

## 4. WP-GROK-REFRACTOR-SIM-001 — **landed** (`89c2dbe`+)

| Step | Action | Status |
|------|--------|--------|
| 1 | Register `diplomacy_layer` tick wrapper (`_turn_decisions` passthrough) | **Done** |
| 2 | Register `competition` mechanics module | **Done** |
| 3 | `run_simulation_layer` → milestones only | **Done** |
| 4 | Tick order: `pass_through_tick()` then `run_simulation_layer()` | **Done** |
| 5 | pytest boundary + order tests | **Done** — `tests/test_wp_grok_refactor_sim_001.py` |

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
