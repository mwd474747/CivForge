# Game Engine Implementation Gap Inventory (v1)

**Generated:** 2026-06-15  
**Scope:** CivForge governance kernel + civ game layer (`~/CivForge`, `:8080`)  
**Label:** `report-only` — inventory of what exists vs what a *functioning* game engine still needs.

---

## Executive summary

CivForge has a **working governance kernel** with a **prototype civ layer**: turn advance, multi-agent map/diplomacy, mechanics registry ticks, CivStudy policy-tree bridge, victory progress, receipts, dashboard, and 9 MCP tools (including `civforge_reset_game`).

It is **not yet** a complete standalone game engine. The largest gaps are **session lifecycle polish**, **player agency**, **policy→mechanics wiring**, **milestone truth**, and **auth/observability parity**.

---

## Implemented (prototype / live)

| Area | Status | Notes |
|------|--------|-------|
| Governance core | ✅ | `GovernanceOrchestrator`, AgentBrains, FunForge gate, cycle receipts |
| Persistence | ✅ | SQLite `gravity_backend.db` + disk receipts |
| Turn simulation | ✅ | `run_turn_simulation()` — multi-agent + `MechanicsRegistry.tick_all` + victory sync |
| Mechanics extension | ✅ | `MechanicsRegistry.register`, tick contract v1, CivStudy modules registered |
| Multi-agent civ | ✅ | Map tiles, alliances, negotiations, victory milestones |
| CivStudy bridge | ✅ | District/discovery/cultural/policy-tree ticks; reference metadata panel |
| Victory outcomes | ✅ | `outcome: victory` at 100%; one-time `victory-outcome-*.md` receipt |
| Game reset | ✅ | `POST /game/reset`, MCP `civforge_reset_game`, dashboard button |
| Dashboard | ✅ | Map, agents, negotiations, alliances, mechanics lanes, policy HUD |
| MCP agent lane | ✅ | 9 tools via `tools/mcp_server.py` |
| Nexus telemetry | ✅ | Heartbeats with turn/fun/resources/victoryProgress (thin bridge) |
| Tests | ✅ | 29+ pytest (mechanics, turn sim, reset, governance tools) |

---

## Missing for a functioning game engine

Prioritized backlog. **P0** = blocks “playable loop”; **P1** = core fun/integrity; **P2** = polish/scale.

### P0 — Session & loop integrity

| Gap | Why it matters | Suggested work |
|-----|----------------|----------------|
| Post-victory mode | Victory sets `outcome` but loop continues unchanged | **Done (2026-06-15)** — `session_phase: epilogue` blocks advance; dashboard disables Advance |
| Defeat / stall conditions | No lose state or stalemate | Define failure triggers (betrayal collapse, fun floor, turn cap) |
| Milestone truth | “First alliance” / “Shared map control” not tied to real alliances/tiles | **Done (2026-06-15)** — `milestone_truth()` in `sync_victory_milestones` |
| E2E HTTP test | No full `advance_turn` → victory receipt path in CI | **Done (2026-06-15)** — `tests/test_game_loop_e2e.py` |

### P1 — Mechanics & player agency

| Gap | Why it matters | Suggested work |
|-----|----------------|----------------|
| Policy effect wiring | `open_negotiation`, `symposium_chain` set flags only | **Partial (2026-06-15)** — open_negotiation waives negotiate cost; symposium_chain shortens cultural cadence; see `GAME_MECHANICS_WIRING_INVENTORY_V1.md` |
| Player map actions | No claim tile, move garrison, choose district | `POST /game/map/*` or district selection endpoint |
| Player policy choices | Policies unlock via ticks only | `POST /game/policy/unlock` with influence cost |
| Agent play parity | Brains decide; player is mostly observer | Register `PlayerAgent` decisions in orchestrator cycle |
| Betrayal resolution | Risk displayed; no betrayal event | Tick hook when risk > threshold under `betrayal_watch` |

### P1 — Platform & integration

| Gap | Why it matters | Suggested work |
|-----|----------------|----------------|
| Auth on mutators | Local `:8080` ungated; protected path is demo only | **Partial (2026-06-15)** — `CIVFORGE_REQUIRE_AUTH=1` forces token on mutators |
| CivStudy corpus | Reference metadata only | Optional live read of CivStudy repo for district/policy definitions |
| Nexus outcome telemetry | Sends `victoryProgress` number, not `outcome` | **Done (2026-06-15)** — `victoryOutcome` + `sessionPhase` in telemetry |
| Documentation drift | `IMPLEMENTATION_STATUS.md` lagged | Keep status doc aligned with mechanics integration receipts |

### P2 — Game feel & operations

| Gap | Why it matters | Suggested work |
|-----|----------------|----------------|
| Turn pacing / costs | Resources tick +1 every advance regardless of actions | Action costs, upkeep, diminishing returns |
| AI diplomacy depth | Negotiations accept/decline; limited AI initiative | AgentBrain negotiation proposals each cycle |
| Save slots | Single SQLite snapshot | Named sessions / export-import JSON |
| Concurrency | Single in-memory `game_state` | Document single-player assumption or add locking |
| Load / soak tests | None | Scripted N-turn advance under pytest |
| Godot / render layer | Archived; not in scope for kernel | Separate client if 3D/visual civ desired |

---

## Architecture reference (current loop)

```
POST /advance_turn
  → orchestrator.advance_cycle()     # agents + FunForge + gate
  → run_turn_simulation()            # multi_agent_state + mechanics_registry
  → sync_victory_milestones()
  → maybe_emit_victory_receipt()
  → receipt_store.append + save_state
```

**Extension surface:** `MechanicsRegistry.register(name, tick_fn)` on shared `game_state` dict.

**Registered modules:** `civstudy_district`, `civstudy_discovery`, `civstudy_cultural`, `civstudy_policy_tree`.

---

## Recommended next slices (path-sliced)

1. **Milestone truth** — `multi_agent_state.sync_victory_milestones` reads alliance count + map ownership.
2. **Post-victory epilogue** — when `outcome == "victory"`, return `session_phase: "epilogue"` from `/state`; dashboard disables advance.
3. **Policy wiring** — `open_negotiation` reduces influence cost on `POST /game/negotiate`.
4. **E2E test** — TestClient advances until victory receipt file exists.
5. **Auth gate** — optional `CIVFORGE_REQUIRE_AUTH=1` on mutating routes.

---

## Validation commands

```bash
cd ~/CivForge
python3 -m pytest tests/ -q
bash tools/turnkey-governance-posture.sh
bash tools/validate-game.sh --read-only
curl -s http://127.0.0.1:8080/state | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8080/game/reset
```

---

## Related docs

- `docs/MECHANICS_TICK_CONTRACT_V1.md`
- `docs/GAME_PLAY_GUIDE_V1.md`
- `docs/CIVFORGE_SWARM_CLASS_V1.md`
- `IMPLEMENTATION_STATUS.md`
