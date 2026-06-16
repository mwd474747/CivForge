# Grok Consolidated Handoff — Block A Review + Block B Redirect

**Generated:** 2026-06-16  
**Authority:** `report-only` (planning lane; not promotion truth)  
**Anchor:** CivForge `main` — pull then `git rev-parse --short HEAD`  
**Execution baseline:** `0f1aad8` (101 pytest); prior handoff `receipts/HANDOFF-GROK-PLANNING-QUEUE-20260616.md`  
**Cursor review author:** Cursor partner lane (validation only)

---

## 0. One-page summary for Grok

| Item | Verdict |
|------|---------|
| **Block A PRIMEs** (CULTURAL-VICTORY, POLICY-BRANCH, WONDER-PLACE) | **Direction OK — envelopes too thin.** Resubmit §5 refined envelopes before Mike ignites Cursor. |
| **WP-GROK-AGENT-VS-AGENT-003** | **Reject for execution.** Split into Block B (`COMPETITION-DEPTH-001` + `PLAYER-AGENT-001`); extend existing modules. |
| **Grok role** | Planning PRIMEs with full envelopes only — no execution claims, no parallel subsystems. |
| **Cursor role** | One WP per ignition; pytest + execution receipt. |
| **Mike role** | One-line ignition per WP after Grok resubmit. |

---

## 1. Architecture Grok must not re-litigate

```
orchestrator.advance_cycle()
  → run_turn_simulation()
       → _turn_decisions = decisions
       → registry.pass_through_tick()   # diplomacy_layer, competition, civstudy_*, lanes
       → run_simulation_layer()         # milestones only
       → pop _turn_decisions
```

**Already landed (do not duplicate):**

| Surface | Location |
|---------|----------|
| Cultural HUD metadata | `backend/victory_hud.py` → `/state.victory_hud.cultural_path` |
| Policy tree + auto-unlock tick | `backend/civstudy_metadata.py`, `tick_civstudy_policy_tree` in `civstudy_mechanics_bridge.py` |
| Player policy unlock | `POST /game/policy/unlock` via `game_actions.unlock_policy` |
| Wonder reference cards | `backend/civstudy_corpus_cards.py` (`wonder-pyramids`, `wonder-great-wall`, `wonder-oracle`) |
| Agent / competition | `backend/agent_control.py`, `backend/competition_modes.py`, `/game/agent/*`, `/game/competition/*` |
| Registry modules | `civstudy_policy_tree`, `civstudy_cultural`, `competition`, `diplomacy_layer` — **do not add parallel module names** |

**Tick order for all new WPs:** `"inherit: mechanics_first_then_milestones"`.

---

## 2. Block A review — Grok PRIME assessment

### WP-GROK-BLOCK-A-001 → WP-GROK-CULTURAL-VICTORY-001

**Grok envelope status:** `planning` — **not execution-ready**

| Gap | Detail |
|-----|--------|
| Missing §8.4 fields | No `target_files`, `tick_order`, `non_goals`, `rollback`, `planning_lane` |
| Wrong integration hint | “Register in mechanics_registry” — cultural ticks already use `civstudy_cultural`; victory path belongs in `victory_progress` + `victory_hud` + milestone sync |
| Milestone IDs vague | `prestige_25`, `wonder_completion`, `event_chain_mastery` must map to measurable state (influence_spread, commissioned wonders, chain completion) |
| Ignores existing HUD | `victory_hud.cultural_path` already exposes chains, influence, policies — extend, don’t replace |

**Cursor scope (when refined):** Add `victory_progress.cultural_path` progress object; detect milestones in `tick_civstudy_cultural_chains` / `sync_victory_milestones`; extend `victory_hud_summary`; dashboard readout in `frontend/index.html`; pytest in `tests/test_wp_grok_cultural_victory_001.py`.

---

### WP-GROK-BLOCK-A-002 → WP-GROK-POLICY-BRANCH-001

**Grok envelope status:** `planning` — **not execution-ready**

| Gap | Detail |
|-----|--------|
| Branch names mismatch | `tradition_oligarchy` / `liberty_republic` are Civ VI names; repo uses `diplomacy`, `economy`, `culture` branches in `default_policy_tree()` |
| Wrong integration | “Register in mechanics_registry” — `civstudy_policy_tree` **already registered** |
| Missing player UX | Handoff requires prereq graph + **dashboard checklist**; Grok omits UI and `unlock_policy` wiring |
| No metadata shape | Need full policy objects (tier, prereq, influence_cost, effect) like existing `envoy_network` |

**Cursor scope (when refined):** Extend `default_policy_tree()` with explicit branch choice metadata (or map Tradition/Liberty → culture/diplomacy sub-branches); expose branch checklist on `/state.civstudy_sim.policy_tree`; dashboard panel in `index.html`; pytest for branch selection + unlock.

---

### WP-GROK-BLOCK-A-003 → WP-GROK-WONDER-PLACE-001

**Grok envelope status:** `planning` — **not execution-ready**

| Gap | Detail |
|-----|--------|
| Examples only | Pyramids/Great Wall/Oracle exist as **corpus cards only** — no gameplay commission path |
| Missing route | Handoff specifies `POST /game/wonder/commission` — Grok did not include API shape |
| Wrong integration | “Register in mechanics_registry” — wonders are **player actions + sim state**, not a new tick module |
| Missing costs/effects | Each wonder needs influence cost + yield/effect tied to card metadata |

**Cursor scope (when refined):** `commission_wonder()` in `game_actions.py`; route in `sim_api.py`; `civstudy_sim.commissioned_wonders[]`; optional cultural milestone hook; pytest + optional commission receipt file.

---

## 3. Block B redirect — WP-GROK-AGENT-VS-AGENT-003

**Verdict:** **Reject** as monolith. Do not create:

- `backend/agent_vs_agent.py`
- `frontend/dashboard_agent_vs_agent.html`
- Routes under `/game/agent_vs_agent/*`
- Registry module `agent_vs_agent_play`
- HTMX / Tailwind (not in repo)
- `tools/turnkey-agent-vs-agent-full.sh` that codegen’s files

**Replace with two WPs (plan Block B):**

| WP ID | Extend | Key deliverables |
|-------|--------|------------------|
| **WP-GROK-COMPETITION-DEPTH-001** | `competition_modes.py`, `sim_api.py`, `index.html` | Real win/stop rules; `POST /game/competition/autoplay/start\|pause\|speed`; block `advance_turn` when tournament resolved; use existing `spectator_log` |
| **WP-GROK-PLAYER-AGENT-001** | `game_actions.player_cycle_decision`, orchestrator receipt | Strategy selection; parity with AI governor lines in cycle receipt |

---

## 4. Grok instructions (mandatory before next PRIME)

### 4.1 Must do

1. Pull `main` and read this file + `HANDOFF-GROK-PLANNING-QUEUE-20260616.md` §8.
2. **Resubmit Block A** as three PRIME receipts using §5 envelopes (replace thin JSON).
3. **Retire** WP-GROK-AGENT-VS-AGENT-003 or reissue as COMPETITION-DEPTH + PLAYER-AGENT per §3.
4. Every envelope includes: `target_files`, `tick_order`, `non_goals` (≥3), `acceptance`, `rollback`, `planning_lane: true`, `execution_authority: cursor`.
5. Close prior landed WPs with `closure_class: planning_validated_against_cursor_execution` linking `cursor-execution-wp-*` paths.
6. Use **extend-existing** language only — cite files from §1 table.

### 4.2 Must not do

- Claim “landed”, “100% executable”, “zero missing pieces”, or “fully playable” without Cursor execution receipt.
- Propose new top-level subsystems when landed modules exist.
- Register duplicate mechanics modules for policy/cultural/wonder/agent-vs-agent.
- Reference stale HEAD (`3d4bbd5`, `a56b8ca`) or pytest counts (29, 81).
- Plan wt/dawsOS promotion or `:8082` bridge authority expansion.

### 4.3 Execution order (Mike)

1. Grok resubmits Block A refined PRIMEs (§5).
2. Mike: `Execute WP-GROK-CULTURAL-VICTORY-001` → Cursor → receipt → pytest.
3. Repeat for POLICY-BRANCH-001, then WONDER-PLACE-001 (one WP per ignition).
4. After Block A, Grok authors Block B refined PRIMEs; Mike ignites one at a time.

---

## 5. Refined envelopes — Grok copy/adopt (planning-class)

Grok should publish these (or equivalent) as PRIME receipts. Cursor treats §5 as **candidate scope** until Mike ignites.

### WP-GROK-CULTURAL-VICTORY-001

```json
{
  "kind": "refactor_proposal",
  "title": "Cultural victory path — playable milestones wired to HUD",
  "work_pack_id": "WP-GROK-CULTURAL-VICTORY-001",
  "planning_lane": true,
  "execution_authority": "cursor",
  "payload": {
    "target_files": [
      "backend/civstudy_mechanics_bridge.py",
      "backend/multi_agent_state.py",
      "backend/victory_hud.py",
      "backend/sim_api.py",
      "frontend/index.html",
      "tests/test_wp_grok_cultural_victory_001.py"
    ],
    "tick_order": "inherit: mechanics_first_then_milestones",
    "cultural_milestones": [
      {"id": "prestige_25", "gate": "mechanics_lanes.cultural.influence_spread >= 25"},
      {"id": "event_chain_mastery", "gate": "all default_cultural_event_chains complete in civstudy_sim.active_chains"},
      {"id": "wonder_prestige", "gate": "len(civstudy_sim.commissioned_wonders) >= 1"}
    ],
    "state_fields": {
      "victory_progress.cultural_path": "progress_pct, milestones[], alternate_victory_eligible",
      "victory_hud.cultural_path": "extend with milestone status"
    },
    "non_goals": [
      "Full Civ VI cultural victory parity",
      "New MechanicsRegistry module name",
      "8082 bridge mutation or live CivStudy fetch",
      "Replacing joint_progress domination path"
    ]
  },
  "acceptance": [
    "pytest tests/test_wp_grok_cultural_victory_001.py passes",
    "/state.victory_progress.cultural_path present after cultural tick",
    "/state.victory_hud.cultural_path shows milestone progress",
    "101+ pytest total pass"
  ],
  "rollback": "git revert tests/test_wp_grok_cultural_victory_001.py backend/victory_hud.py backend/civstudy_mechanics_bridge.py"
}
```

### WP-GROK-POLICY-BRANCH-001

```json
{
  "kind": "policy_definition",
  "title": "Policy tree branching + dashboard unlock checklist",
  "work_pack_id": "WP-GROK-POLICY-BRANCH-001",
  "planning_lane": true,
  "execution_authority": "cursor",
  "payload": {
    "target_files": [
      "backend/civstudy_metadata.py",
      "backend/civstudy_mechanics_bridge.py",
      "backend/game_actions.py",
      "backend/sim_api.py",
      "frontend/index.html",
      "tests/test_wp_grok_policy_branch_001.py"
    ],
    "tick_order": "inherit: mechanics_first_then_milestones",
    "branch_extensions": [
      {
        "id": "tradition",
        "maps_to": "culture",
        "policies": ["symposium_chain", "influence_spread", "festival_receipts"]
      },
      {
        "id": "liberty",
        "maps_to": "diplomacy",
        "policies": ["open_negotiation", "shared_intel"]
      }
    ],
    "player_actions": "POST /game/policy/unlock unchanged; add GET /state policy_tree.checklist",
    "non_goals": [
      "New civstudy_policy_tree registry module",
      "Auto-unlock removal without migration test",
      "Civ VI government tiers",
      "Mechanics propose/gate apply on live kernel"
    ]
  },
  "acceptance": [
    "pytest tests/test_wp_grok_policy_branch_001.py passes",
    "/state exposes policy branch checklist with locked/unlocked/prereq",
    "unlock_policy respects branch prereqs",
    "Dashboard panel lists branches"
  ],
  "rollback": "git revert backend/civstudy_metadata.py tests/test_wp_grok_policy_branch_001.py"
}
```

### WP-GROK-WONDER-PLACE-001

```json
{
  "kind": "ui_component",
  "title": "Wonder commission — corpus card to soft gameplay action",
  "work_pack_id": "WP-GROK-WONDER-PLACE-001",
  "planning_lane": true,
  "execution_authority": "cursor",
  "payload": {
    "target_files": [
      "backend/civstudy_corpus_cards.py",
      "backend/game_actions.py",
      "backend/sim_api.py",
      "frontend/index.html",
      "tests/test_wp_grok_wonder_place_001.py"
    ],
    "tick_order": "inherit: mechanics_first_then_milestones",
    "wonders": ["wonder-pyramids", "wonder-great-wall", "wonder-oracle"],
    "route": "POST /game/wonder/commission { wonder_id, district_id? }",
    "state": "civstudy_sim.commissioned_wonders[] with turn + effect applied",
    "costs": "influence from corpus card metadata or fixed table",
    "non_goals": [
      "3D placement or map tile geometry",
      "New mechanics tick module",
      "Full wonder production queue",
      "8082 authority"
    ]
  },
  "acceptance": [
    "pytest tests/test_wp_grok_wonder_place_001.py passes",
    "Commission deducts influence and appends commissioned_wonders",
    "Cultural milestone wonder_prestige can complete when wonder commissioned",
    "Dashboard or action catalog lists commissionable wonders"
  ],
  "rollback": "git revert backend/game_actions.py backend/sim_api.py tests/test_wp_grok_wonder_place_001.py"
}
```

### WP-GROK-COMPETITION-DEPTH-001 (replaces AGENT-VS-AGENT-003)

```json
{
  "kind": "refactor_proposal",
  "title": "Competition depth — win detection, autoplay, spectator",
  "work_pack_id": "WP-GROK-COMPETITION-DEPTH-001",
  "planning_lane": true,
  "execution_authority": "cursor",
  "payload": {
    "target_files": [
      "backend/competition_modes.py",
      "backend/sim_api.py",
      "frontend/index.html",
      "backend/telemetry_enrich.py",
      "tests/test_wp_grok_competition_depth_001.py"
    ],
    "tick_order": "inherit: mechanics_first_then_milestones",
    "routes": [
      "POST /game/competition/autoplay/start",
      "POST /game/competition/autoplay/pause",
      "POST /game/competition/autoplay/speed",
      "GET /game/competition/status"
    ],
    "non_goals": [
      "agent_vs_agent.py parallel subsystem",
      "HTMX/Tailwind/new HTML file",
      "agent_vs_agent_play registry module",
      "Codegen turnkey script"
    ]
  },
  "acceptance": [
    "Tournament end blocks advance_turn with 409",
    "Autoplay respects cooldown",
    "spectator_log persisted; telemetry metadata only on 8082"
  ],
  "rollback": "git revert backend/competition_modes.py backend/sim_api.py"
}
```

---

## 6. Copy-paste — Grok next session

```
Planning lane only. Read receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md.

Resubmit Block A using §5 envelopes (full target_files, tick_order, non_goals, rollback).
Retire WP-GROK-AGENT-VS-AGENT-003; use WP-GROK-COMPETITION-DEPTH-001 envelope instead.

Do not claim execution. Anchor on landed modules in §1. No new parallel subsystems.
```

---

## 7. Copy-paste — Mike → Cursor (after Grok resubmit)

```
Execute WP-GROK-CULTURAL-VICTORY-001 per HANDOFF-GROK-CONSOLIDATED-20260616.md §5.
Extend existing civstudy_cultural + victory_hud — no new registry module.
pytest + execution receipt; commit/push when I ask.
```

---

## Related

- `receipts/HANDOFF-GROK-PLANNING-QUEUE-20260616.md`
- `docs/SIM_GAME_BOUNDARY_V1.md`
- `docs/EXECUTION_LANE_V2.md`
- `receipts/cursor-execution-wp-grok-refactor-sim-001-20260616.md`
