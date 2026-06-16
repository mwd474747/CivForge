# Simulation milestone sync decision (WP-GROK-REFRACTOR-SIM-002)

**Status:** `current` — Block C @ Cursor execution  
**Tag:** architecture decision (not promotion truth for dawsOS wt)

---

## Question

Should `sync_victory_milestones()` move behind `MechanicsRegistry` as a registered tick module?

## Decision

**Keep milestone sync in the simulation layer** (`backend/simulation_boundary.py` → `run_simulation_layer`).

| Factor | Simulation layer | MechanicsRegistry |
|--------|------------------|-------------------|
| Role | Orchestrator-adjacent coordination | Pluggable rule ticks on shared `game_state` |
| Joint victory | Milestone truth + `joint_progress` target | Would mix victory orchestration with lane rules |
| Alternate victory | Runs immediately before milestone sync | Would split cultural/domination path closure across layers |
| Audit | `_simulation_boundary` documents phases | `_mechanics_tick_audit` documents rule modules |

## Landed tick order (Block C)

```
MechanicsRegistry.pass_through_tick()
  → diplomacy_layer (incl. AI negotiation proposals)
  → competition, military, economic, cultural, civstudy_*
run_simulation_layer()
  → sync_alternate_victory_outcomes()   # cultural + domination epilogue
  → sync_victory_milestones()           # joint path @ target
```

`TICK_ORDER`: `mechanics_first_then_alternate_victory_then_milestones`

## When to revisit

- If milestone sync needs per-module override hooks (e.g. competition mode replaces joint target)
- If pytest soak shows ordering bugs between alternate and joint on the same turn

Until then: **document-only closure** — no registry move.
