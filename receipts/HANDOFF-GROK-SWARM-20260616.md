# HANDOFF — Grok Swarm (mechanics proposal lane)

**Date:** 2026-06-16  
**Label:** `current` after Cursor commit + pytest  
**Lane model:** `docs/EXECUTION_LANE_V2.md` — **you plan on grok.com; Cursor executes**  
**Handoff seed:** `prompts/grok_swarm_handoff_seed.md`  
**Cursor execution:** `receipts/cursor-execution-mechanics-proposal-lane-20260616.md`  
**Work pack:** `receipts/work-pack-grok-mechanics-propose-001.md`  
**CivForge HEAD:** `f55aad4` on `main` (verify: `git pull && git rev-parse --short HEAD`; feature `956d251`)

**Cursor execution (live `:8080` proof):** `receipts/cursor-execution-wp-grok-mech-district-001-20260616.md`

---

## 1. What changed (read this first)

Simulation-only is no longer the only Grok lane for game mechanics.

| Lane | You use | Purpose |
|------|---------|---------|
| **Simulation** | `advance_turn`, `what_if` | Tick existing rules |
| **Proposal** | `propose_mechanics` → `gate` → `apply` | Author governed mechanic updates |

Full contract: **`docs/GAME_MECHANICS_SWARM_PROPOSAL_LANE_V1.md`**

Gravity/meta work stays on `/governance/propose` — do not conflate.

---

## 2. MCP tools (16 total)

New proposal tools (assign in work packs; Cursor/MCP executes on `:8080`):

| Tool | Route |
|------|-------|
| `civforge_propose_mechanics` | `POST /game/mechanics/propose` |
| `civforge_gate_mechanics` | `POST /game/mechanics/gate` |
| `civforge_apply_mechanics` | `POST /game/mechanics/apply` |
| `civforge_list_mechanics_proposals` | `GET /game/mechanics/proposals` |

Existing 12 play/governance tools unchanged — see `docs/GAME_PLAY_GUIDE_V1.md`.

---

## 3. Proposal kinds (what you can author)

### Runtime (kernel applies after FunForge gate ≥78)

| Kind | Example payload |
|------|-----------------|
| `lane_param` | `{ "lane": "economic", "params": { "yield_bonus_pct": 20 } }` |
| `district_yield_override` | `{ "district_id": "research-campus", "yield_bonus": { "sci": 3 } }` |
| `tick_cadence_override` | `{ "cultural_cadence": 5 }` |
| `param_override` | `{ "trade_route_sci_bonus": 2 }` |

### Planning (you propose → Cursor lands code)

| Kind | Executor |
|------|----------|
| `policy_definition` | Cursor — metadata + `apply_policy_effect` |
| `fork_definition` | Cursor — discovery fork ticks |
| `tick_module` | Cursor — `MechanicsRegistry.register` |
| `code_change` | Cursor — git commit |

Planning kinds **gate** but **do not auto-apply** — export to `WP-*` for Cursor.

---

## 4. Your default next work packs

| Priority | Topic | Notes |
|----------|-------|-------|
| 1 | Runtime tuning via proposal lane | Use `WP-GROK-MECHANICS-PROPOSE-001` template |
| 2 | New policy/fork definitions | `policy_definition` / `fork_definition` → Cursor WP |
| 3 | Negotiation backlog sweep | `civforge_negotiate_respond` loop |
| 4 | `:8081` JWT identity | infra lane — Cursor only |

**Forbidden:** UI rebuild, fake HEAD, wt promotion claims, local Mac terminal claims.

---

## 5. PRIME receipt rules (unchanged)

1. Planning class until linked **Cursor execution receipt** with real `git HEAD`
2. Cite live `GET /state` — `fun_score`, `mechanics_proposals`, `mechanics_overrides`
3. Tag stale claims explicitly
4. Verify commands (Cursor runs):

```bash
cd ~/CivForge
git pull origin main
python3 -m pytest tests/test_mechanics_proposals.py tests/ -q
bash tools/turnkey-governance-posture.sh
git rev-parse --short HEAD
```

---

## 6. Example proposal flow (for your work packs)

```json
{
  "kind": "district_yield_override",
  "title": "Research campus sci +1",
  "payload": {
    "district_id": "research-campus",
    "yield_bonus": { "sci": 3 }
  },
  "work_pack_id": "WP-GROK-MECHANICS-PROPOSE-001",
  "author": "grok_swarm",
  "rationale": "Boost late-game science pacing without new tick module"
}
```

Sequence: propose → gate (FunForge) → apply → confirm on `/state`.

---

## 7. Still out of scope (do not claim closed)

- `MechanicsRegistry.register` from proposals without Cursor code
- Live CivStudy corpus (reference metadata only)
- `:8081` JWT / protected advance identity
- 3D/Godot client
- wt `reports/ops` promotion truth (OpenClaw only)

---

## 8. Canonical cross-refs

| Doc | Purpose |
|-----|---------|
| `docs/GAME_MECHANICS_SWARM_PROPOSAL_LANE_V1.md` | Proposal lane contract |
| `docs/GAME_MECHANICS_WIRING_INVENTORY_V1.md` | Full wiring inventory |
| `docs/GROK_SWARM_PACKET_V1.md` | Swarm packet v1 |
| `docs/CIVFORGE_SWARM_CLASS_V1.md` | Swarm class vs dawsOS |
| `receipts/work-pack-grok-mechanics-propose-001.md` | Example WP |

---

_End of handoff — paste `prompts/grok_swarm_handoff_seed.md` + this file into grok.com project._
