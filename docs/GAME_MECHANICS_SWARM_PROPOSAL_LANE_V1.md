# Game Mechanics Swarm Proposal Lane (v1)

**Updated:** 2026-06-16  
**Label:** `prototype-only` — passes pytest; live kernel smoke recommended  
**Purpose:** Separate **simulation** from **mechanics proposal** so Grok swarm can author governed mechanic updates.

---

## Two lanes (do not conflate)

| Lane | Tools / endpoints | What it does |
|------|-------------------|--------------|
| **Simulation** | `civforge_advance_turn`, `civforge_what_if`, `POST /advance_turn` | Ticks existing `MechanicsRegistry` modules on current rules |
| **Proposal** | `civforge_propose_mechanics`, `civforge_gate_mechanics`, `civforge_apply_mechanics` | Grok swarm drafts mechanic changes → FunForge gate → kernel applies runtime patches |

Gravity/meta work stays on `/governance/propose` (separate from game mechanics).

---

## Proposal kinds

### Runtime (kernel auto-apply after gate)

| Kind | Payload shape | Effect |
|------|---------------|--------|
| `lane_param` | `{ lane, params }` | Patch `mechanics_lanes` + persisted overrides |
| `district_yield_override` | `{ district_id, yield_bonus }` | Override district pulse yields |
| `tick_cadence_override` | `{ cultural_cadence: 2-12 }` | Override cultural chain cadence |
| `param_override` | session param keys | `trade_route_sci_bonus`, `receipt_quorum_*`, etc. |

### Planning (Grok → Cursor WP — no kernel auto-apply)

| Kind | Payload shape | Executor |
|------|---------------|----------|
| `policy_definition` | `{ id, branch_id, tier, effect }` | Cursor wires `apply_policy_effect` + ticks |
| `fork_definition` | `{ id, name, prereq }` | Cursor wires discovery fork ticks |
| `tick_module` | `{ module_name, description }` | Cursor registers `MechanicsRegistry` module |
| `code_change` | `{ description, target_files? }` | Cursor commits + pytest |

---

## API flow

```
POST /game/mechanics/propose   → status PROPOSED
POST /game/mechanics/gate      → GATED_APPROVED | GATED_REJECTED (FunForge ≥78)
POST /game/mechanics/apply     → APPLIED (runtime kinds only)
GET  /game/mechanics/proposals → list + summary
```

`/state` exposes `mechanics_proposals` summary and `mechanics_overrides`.

---

## MCP tools (16 total)

| Tool | Route |
|------|-------|
| `civforge_propose_mechanics` | `POST /game/mechanics/propose` |
| `civforge_gate_mechanics` | `POST /game/mechanics/gate` |
| `civforge_apply_mechanics` | `POST /game/mechanics/apply` |
| `civforge_list_mechanics_proposals` | `GET /game/mechanics/proposals` |

Plus existing 12 play/governance tools — see `docs/GAME_PLAY_GUIDE_V1.md` (16 tools listed there).

---

## Grok swarm work pack pattern

1. **Plan** on grok.com — author `WP-GROK-MECHANICS-PROPOSE-*` with proposal payloads (not terminal claims).
2. **Cursor executes** — land tick modules / metadata for `planning` kinds; runtime kinds can be exercised via MCP on `:8080`.
3. **Receipt** — cite live `/state` `mechanics_proposals` + `fun_score`; link `receipts/cursor-execution-*.md`.

Example work pack: `receipts/work-pack-grok-mechanics-propose-001.md`

---

## Wired vs still simulation-only

| Surface | Status |
|---------|--------|
| All 10 policies, 4 forks, 4 districts, player actions | **Wired** (ticks + actions) |
| Mechanics proposal lane | **Wired** (propose/gate/apply + overrides + dashboard tab) |
| `MechanicsRegistry.register` from proposals | **Planning only** — requires Cursor code |
| Live CivStudy corpus | **Reference metadata only** |
| `:8081` JWT | **Out of scope** |

---

## Validation

```bash
cd ~/CivForge
python3 -m pytest tests/test_mechanics_proposals.py tests/ -q
bash tools/turnkey-governance-posture.sh
python3 tools/civforge_contract_parity.py
```

---

## Related

- `docs/GAME_MECHANICS_WIRING_INVENTORY_V1.md`
- `docs/GROK_SWARM_PACKET_V1.md`
- `docs/WORK_PACK_TEMPLATE_V1.md`
- `backend/mechanics_proposals.py`
