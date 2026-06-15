# Mechanics tick module contract v1

**Status:** `current` — CivForge kernel extension surface

## Contract

```python
def tick_your_module(game_state: dict) -> list[str]:
    ...
```

| Rule | Detail |
|------|--------|
| Input | Live `game_state` from `backend/sim_api.py` (SQLite-restored) |
| Required keys | `turn` (int), `player` (dict with `resources`) |
| Mutation | In-place only; persisted via `ReceiptStore.save_state` after `/advance_turn` |
| Output | `List[str]` event lines appended to `game_state["events"]` |
| Errors | Unexpected exceptions become `"Mechanics {name} tick error: …"` |

## Registration

```python
from core.mechanics_registry import MechanicsRegistry
from core.mechanics_tick_contract import wrap_tick

registry = MechanicsRegistry()
registry.register("my_module", wrap_tick(tick_my_module))
```

Default registry (`build_default_registry`) auto-wraps all modules.

## Turn order (`POST /advance_turn`)

1. `GovernanceOrchestrator.advance_cycle()` — brains, FunForge, gate
2. `tick_multi_agent_state()` — map, diplomacy, victory increment
3. `MechanicsRegistry.tick_all()` — lanes + CivStudy bridge modules
4. `sync_victory_milestones()` — post-tick milestone/outcome sync
5. Victory outcome receipt (first transition only)
6. Governance cycle receipt + SQLite snapshot

## CivStudy integration pattern

Read-only metadata in `backend/civstudy_metadata.py` → tick in `backend/civstudy_mechanics_bridge.py` → `register_civstudy_mechanics(registry)`.

Modules: `civstudy_district`, `civstudy_discovery`, `civstudy_cultural`, `civstudy_policy_tree`.
