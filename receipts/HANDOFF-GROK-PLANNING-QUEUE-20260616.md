# Grok Planning Handoff — Post REFACTOR-SIM-001

> **Consolidated review (Block A + Agent-vs-Agent):** see **`receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md`** — use that for Grok’s next PRIME resubmit.

**Generated:** 2026-06-16  
**Cursor HEAD (CivForge `main`):** pull `main` → `git rev-parse --short HEAD` (execution baseline **`0f1aad8`**)  
**Tag:** `report-only` (planning lane input; not promotion truth)

---

## 1. Completion gate — approved to progress open items

The following Cursor execution receipts are **landed on `main`** with pytest proof. Grok may treat these as **closed for planning** and build the next blocks on top.

| Work pack | Receipt | Approx HEAD | pytest | Status |
|-----------|---------|-------------|--------|--------|
| WP-GROK-MECH-DISTRICT-001 | `cursor-execution-wp-grok-mech-district-001-20260616.md` | `4b57418` | — | **Done** (propose→gate→apply on `:8080`) |
| WP-GROK-POLICY-002 | `cursor-execution-wp-grok-policy-002-20260616.md` | `8d10225` | — | **Done** (`envoy_network`) |
| Dashboard mechanics panel | `cursor-execution-dashboard-mechanics-panel-20260616.md` | `867a5e8` | — | **Done** |
| WP-GROK-SYNC-HANDOFF-004 | `cursor-execution-wp-grok-sync-handoff-004-20260616.md` | `a1235dc` | — | **Done** (`send_envoy`, trust erosion) |
| WP-GROK-BATCH-005 | `cursor-execution-wp-grok-batch-005-20260616.md` | `907d2e1` | 81+ | **Done** |
| WP-GROK-AUTHENTIC-AUDIT-003 | `cursor-execution-wp-grok-authentic-audit-003-20260616.md` | `72934b9` | 86+ | **Done** |
| WP-SIM-GAME-CLARITY bundle | `cursor-execution-wp-sim-game-clarity-bundle-20260616.md` | `89c2dbe` | 96+ | **Done** |
| WP-GROK-REFRACTOR-SIM-001 | `cursor-execution-wp-grok-refactor-sim-001-20260616.md` | **`0f1aad8`** | **101** | **Done** |

**Approval to progress:** All rows above have Cursor execution receipts on `main`. Grok may close matching PRIME receipts and author Blocks A–D without re-litigating landed architecture.

**Live kernel note:** Kernel on `:8080` may still reflect pre-refactor `/state` (`tick_order: null`, no `diplomacy_layer` in modules) until `bash tools/start-kernel-8080.sh` on `0f1aad8`. Code + pytest truth = git; live proof is operator action (Mike ignition: *"Restart kernel on 0f1aad8"*).

**Correction alignment (WP-CORRECTION-ALIGN-036):** Grok posture matches Cursor receipts — no full sim replacement, no execution claims from planning lane, dashboard/Vercel not authority.

---

## 2. Current architecture (Grok must anchor here)

See `docs/SIM_GAME_BOUNDARY_V1.md` (§4 **landed**).

```
run_turn_simulation:
  _turn_decisions = decisions
  pass_through_tick()   # diplomacy_layer, competition, military, economic, cultural, civstudy_*
  run_simulation_layer() # milestones only
  pop _turn_decisions
```

**Registries extensibility:**
- `MechanicsRegistry` + `pass_through_tick`
- `CorpusCardRegistry` — CivStudy reference cards
- `DashboardComponentRegistry` — tab/panel metadata
- `agent_controls` + `competition_mode` on `/state`
- `:8082` — metadata-only `enrich_telemetry_payload` (thin bridge; no authority)

---

## 3. Recommended Grok planning blocks (larger batches)

Author as **planning-class PRIME receipts** with refined JSON envelopes. Cursor executes one block at a time; Mike approves ignition in chat.

### Block A — **Mechanics depth** (P1, ~3 WPs)

| WP ID (suggested) | Title | Cursor scope |
|-------------------|-------|--------------|
| WP-GROK-CULTURAL-VICTORY-001 | Cultural victory path as playable mechanics | Register cultural victory progress module; wire `victory_hud.cultural_path` to real tick outcomes; dashboard progress |
| WP-GROK-POLICY-BRANCH-001 | Policy tree branching + unlock checklist | Metadata branches, prereq graph, dashboard checklist UI, tests per policy |
| WP-GROK-WONDER-PLACE-001 | Wonder placement (reference → soft mechanic) | Corpus wonder cards → optional `POST /game/wonder/commission` (influence cost); receipt on commission |

**Non-goals:** Full Civ VI parity, 3D client, live CivStudy repo fetch.

### Block B — **Competition + agents** (P1, ~2 WPs)

| WP ID | Title | Cursor scope |
|-------|-------|--------------|
| WP-GROK-COMPETITION-DEPTH-001 | Real competition orchestrator | Replace prototype point rules with mode-specific win detection; spectator log → receipts; block advance on tournament end |
| WP-GROK-PLAYER-AGENT-001 | PlayerAgent in orchestrator cycle | Register player decisions in `advance_cycle` receipt; parity with AI civ lines |

### Block C — **Platform hardening** (P2, ~2 WPs)

| WP ID | Title | Cursor scope |
|-------|-------|--------------|
| WP-GROK-SOAK-001 | N-turn soak + boundary regression | pytest parametrize 50–100 turns; assert no boundary audit regressions |
| WP-GROK-DOC-SYNC-001 | Close documentation drift | Refresh `GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md`, `IMPLEMENTATION_STATUS.md` (17 MCP, 101 pytest, agent/competition fields) |

### Block D — **Optional registry follow-on** (P2, 1 WP)

| WP ID | Title | Cursor scope |
|-------|-------|--------------|
| WP-GROK-REFRACTOR-SIM-002 | Register milestone sync as mechanics or post-tick hook | Evaluate moving `sync_victory_milestones` behind registry vs keep orchestration-only; document decision |

---

## 4. Standard envelope template (Grok → Cursor)

Each WP should include:

```json
{
  "kind": "<planning|refactor_proposal|ui_component|...>",
  "title": "...",
  "payload": {
    "target_files": ["backend/...", "tests/..."],
    "changes": ["..."],
    "tick_order": "if applicable",
    "non_goals": ["..."]
  },
  "work_pack_id": "WP-GROK-...",
  "acceptance": ["pytest pass", "/state field X", "no 8082 bridge mutation"],
  "rollback": "git revert paths..."
}
```

Cursor replies with `receipts/cursor-execution-wp-*-YYYYMMDD.md` containing: commands run, HEAD, pytest count, `/state` snippet.

---

## 5. Can more authority transfer to Grok safely?

**Yes — within the planning lane. No — for execution or dawsOS truth.**

| More authority → Grok (safe) | Still Cursor / Mike / OpenClaw |
|------------------------------|----------------------------------|
| Batch 3–5 WPs per PRIME receipt with priorities | `git commit`, `git push`, kernel restart |
| Maintain rolling `PLANNING-BACKLOG.md` in CivForge | `reports/ops/*`, C2, wt promotion |
| Pre-refine payloads (tick order, `_turn_decisions`, non-goals) | Vercel `--prod`, LaunchAgent, storage apply |
| Close planning PRIME against Cursor execution receipts | Claim "landed" without Cursor receipt + pytest |
| Author `policy_definition` / `fork_definition` planning kinds | FunForge gate apply on mutating production |
| Propose mechanics via dashboard planning kinds | Trivium / Quad / Masonic mutation |

**Recommended authority upgrade (minimal risk):**

1. **Grok owns the planning queue** — Blocks A→D above; Mike picks block letter once per week.
2. **Grok writes refined envelopes only** — No execution verbs ("landed", "shipped", "100% coherent").
3. **Cursor auto-executes on Mike ignition** — `"Approve Block A WP-1"` → Cursor implements → receipt → Grok next WP.
4. **OpenClaw unchanged** — wt receipts, boundary menu, cron.

This lets Mike focus on **implementation approval** (one-line ignitions) instead of relaying Cursor architectural feedback.

---

## 6. Copy-paste ignition for Grok (next session)

```
Planning lane only. Anchor: CivForge main (latest pull), SIM_GAME_BOUNDARY_V1.md §4 landed, this handoff receipt.

Author Block A (cultural victory, policy branching, wonder placement) as three PRIME receipts
using the envelope template in receipts/HANDOFF-GROK-PLANNING-QUEUE-20260616.md.

Do not claim execution. Do not reference stale HEAD. Include non_goals and rollback per WP.
```

---

## 7. Copy-paste ignition for Mike → Cursor

```
Execute Block A WP-1 when Grok delivers refined envelope. Pull main, restart kernel,
pytest + validate-game, execution receipt, commit/push if I ask.
```

---

## 8. What Grok must update to execute and align

Before authoring Block A PRIME receipts, Grok **must** reconcile planning state against this handoff. Treat anything below as **blocking** for new WPs.

### 8.1 Anchor facts (replace stale references)

| Field | Correct value | Retire / do not cite |
|-------|---------------|----------------------|
| CivForge `main` HEAD | `git rev-parse --short HEAD` after pull | `3d4bbd5`, `a56b8ca`, pre-refactor HEADs |
| pytest count | **101 passed** | 29, 81, 96 as "current" |
| MCP tools | **17** (see `tools/civforge_cli.py`) | "9 MCP tools" in gap inventory |
| Tick order | `mechanics_first_then_milestones` | milestones-before-diplomacy diagrams |
| Simulation layer | **milestones only** (`SIMULATION_PHASES`) | full `run_simulation_layer` as mechanics home |
| Diplomacy / competition | registry modules via `pass_through_tick` | optional future WP for `diplomacy_layer` |
| Execution proof | Cursor `receipts/cursor-execution-wp-*.md` + pytest | Grok PRIME alone, Vercel URL, dashboard screenshot |
| Authority | planning-class PRIME | "landed", "shipped", "100% coherent", "C2 ready" |

### 8.2 Close or supersede open Grok PRIME receipts

For each row in §1, Grok should emit a **planning closure** PRIME that:

1. Links the matching `cursor-execution-wp-*` receipt path (not Grok-only proof).
2. States `closure_class: planning_validated_against_cursor_execution`.
3. Does **not** re-open architecture already decided in `SIM_GAME_BOUNDARY_V1.md` §4.

Do **not** re-plan: REFACTOR-SIM-001 tick order, clarity bundle registries, batch-005 shared_intel/victory_hud, authentic-audit corpus cards.

### 8.3 Documents Grok should refresh (Block C WP or inline)

| Document | Required updates |
|----------|------------------|
| `docs/GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md` | MCP 17, pytest 101, agent_controls, competition_mode, simulation_boundary fields |
| `docs/IMPLEMENTATION_STATUS.md` (if present) | Same counters + landed WPs table from §1 |
| Grok-side backlog / swarm receipts | Point next work at Blocks A→D; remove defeated/refactored items |
| Any Grok diagram showing sim-first tick | Replace with §2 sequence |

Grok **plans** doc-sync in WP-GROK-DOC-SYNC-001; Cursor **lands** file edits.

### 8.4 Envelope rules for every new WP (Block A+)

Each PRIME receipt Grok authors **must** include:

- `work_pack_id` matching `WP-GROK-*` naming in §3
- `payload.target_files` — explicit paths under `backend/`, `tests/`, `frontend/` (no repo-wide refactors)
- `payload.tick_order` — `"inherit: mechanics_first_then_milestones"` unless proposing REFACTOR-SIM-002
- `payload.non_goals` — at least three items (Civ parity, 8082 authority, full sim replacement)
- `acceptance` — pytest command, `/state` field assertions, **no** live gate apply unless Mike ignition names the WP
- `rollback` — `git revert` paths or feature flag off
- `planning_lane: true` and `execution_authority: cursor`

**Kinds Grok may use:** `policy_definition`, `fork_definition`, `refactor_proposal`, `ui_component`, `district_yield_override` (planning only — Cursor runs propose/gate/apply on `:8080`).

**Kinds Grok must not use as execution:** `code_change` without Cursor receipt; any kind implying wt/dawsOS promotion.

### 8.5 Grok must not do (authority boundary)

- Commit, push, or restart `:8080` kernel
- Apply FunForge gate on live kernel without Mike ignition string
- Claim closure without citing Cursor execution receipt + HEAD
- Propose replacing `run_turn_simulation` orchestration in Block A/B (use registry modules)
- Expand `:8082` bridge beyond metadata enrichment

### 8.6 First deliverable after reading this handoff

**Deliver:** Three PRIME receipts for **Block A** (§3), each conforming to §8.4, saved under `receipts/work-pack-grok-*.md` or Grok PRIME path convention.

**Mike ignition → Cursor:** `"Execute WP-GROK-CULTURAL-VICTORY-001"` (or next Block A WP) after Grok delivery.

---

## Related

- `docs/EXECUTION_LANE_V2.md`
- `docs/SIM_GAME_BOUNDARY_V1.md`
- `docs/GAME_MECHANICS_WIRING_INVENTORY_V1.md`
- `receipts/cursor-execution-wp-grok-refactor-sim-001-20260616.md`
