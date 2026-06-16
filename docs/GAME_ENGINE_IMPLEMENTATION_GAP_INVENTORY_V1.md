# Game Engine Implementation Gap Inventory (v1)

**Updated:** 2026-06-16 (Block C doc-sync)  
**Scope:** CivForge governance kernel + civ game layer (`~/CivForge`, `:8080`)  
**Label:** `current` for kernel inventory — not dawsOS promotion truth.

---

## Executive summary

CivForge has a **working governance kernel** with a **playable civ layer**: turn advance, multi-agent map/diplomacy (incl. AI-initiated negotiations), mechanics registry ticks, CivStudy policy-tree bridge, **joint + alternate victory paths** (cultural, domination), competition modes, player agent strategies, receipts, dashboard, and **17 MCP tools**.

Remaining gaps are mostly **platform** (JWT `:8081`, save slots, Vercel deploy) and **polish** (turn pacing costs, full wonder card-text).

**Validation baseline:** **138 pytest** · `bash tools/validate-game.sh --read-only`

---

## Implemented (landed)

| Area | Status | Notes |
|------|--------|-------|
| Governance core | ✅ | Orchestrator, AgentBrains, FunForge, cycle receipts |
| Turn simulation | ✅ | Mechanics first → alternate victory → joint milestones |
| Block A | ✅ closed | Wonder, cultural path, policy branch |
| Block B | ✅ closed | Competition depth, player agent |
| Block C | ✅ closed | Cultural epilogue, domination path, soak, AI diplomacy, tooling |
| Alternate victory | ✅ | `cultural_alternate`, `domination`, `joint` + epilogue UX |
| AI diplomacy | ✅ | Agents propose negotiations to player each cycle |
| Tooling | ✅ | `GET /game/mechanics/status`, `civforge_cli snapshot` |
| MCP agent lane | ✅ | 17 tools via `tools/mcp_server.py` |
| Dashboard | ✅ | Map, agents, competition, alternate victory overlay |

---

## Open gaps (prioritized)

### P1 — Platform

| Gap | Suggested work |
|-----|----------------|
| Auth on mutators | Partial — `CIVFORGE_REQUIRE_AUTH=1`; full JWT via `:8081` |
| CivStudy live corpus | Optional metadata fetch |
| Save slots | Named sessions / export JSON |

### P2 — Game feel

| Gap | Suggested work |
|-----|----------------|
| Turn pacing / action costs | Flat +1/turn; add upkeep model |
| Wonder card-text depth | D-M2 — extend commission effects |
| Godot / 3D client | Retired — separate client if needed |

---

## Architecture reference (current loop)

```
POST /advance_turn
  → orchestrator.advance_cycle()
  → run_turn_simulation()
      MechanicsRegistry.pass_through_tick()  # diplomacy (+ AI proposals), competition, lanes, civstudy
      run_simulation_layer()
        sync_alternate_victory_outcomes()
        sync_victory_milestones()
  → maybe_emit_victory_receipt / defeat
```

See `docs/SIM_MILESTONE_SYNC_DECISION_V1.md` for milestone sync placement (REFACTOR-SIM-002).

---

## Validation commands

```bash
cd ~/CivForge
python3 -m pytest tests/ -q
bash tools/verify-truth-anchor.sh
bash tools/validate-game.sh --read-only
curl -s http://127.0.0.1:8080/game/mechanics/status | python3 -m json.tool
python3 tools/civforge_cli.py snapshot
```
