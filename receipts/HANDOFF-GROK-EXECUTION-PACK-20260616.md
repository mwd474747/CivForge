# Grok Execution Handoff Pack — Blocks A–D (committed)

**Generated:** 2026-06-16  
**Repo:** `~/CivForge` (`main`, `mwd474747/CivForge`)  
**Tag:** `current` — Cursor execution lane; use this as **primary Grok bootstrap**  
**Authority:** tier-3 planning input; closure proof = tier-1 Cursor receipts + git HEAD

---

## 0. Read this first (60 seconds)

| Step | Action |
|------|--------|
| 1 | `cd ~/CivForge && git pull && git rev-parse --short HEAD` |
| 2 | Read `config/work_pack_registry.yaml` → `anchor`, `blocks`, `work_packs` |
| 3 | Read `docs/TRUTH_ORDER.md` |
| 4 | **Do not** re-plan closed blocks; **do not** claim execution from Grok PRIMEs alone |

**Machine authority:** `config/work_pack_registry.yaml`  
**Human index:** `receipts/WORK_PACK_INDEX.md`  
**Scope authority (historical envelopes):** `receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md` §5

---

## 1. Truth order (mandatory)

| Tier | Source | Use for |
|------|--------|---------|
| 0 | `git rev-parse --short HEAD` | Code anchor |
| 1 | `receipts/cursor-execution-*.md` | Execution proof |
| 2 | `config/work_pack_registry.yaml` | WP lifecycle |
| 3 | **This pack** + consolidated handoff | Planning scope |
| 4 | `GET http://127.0.0.1:8080/state` | Live kernel (after restart on HEAD) |
| 5 | Grok PRIME receipts | Planning only — never closure |

**Verify:**

```bash
cd ~/CivForge
bash tools/verify-truth-anchor.sh
bash tools/validate-game.sh --read-only
python3 -m pytest tests/ -q
```

---

## 2. Blocks closed (Cursor execution)

| Block | Title | Closure | pytest slice | Key routes |
|-------|-------|---------|--------------|------------|
| **A** | Wonder → Cultural → Policy | `receipts/BLOCK-A-CLOSURE-20260616.md` | wonder/cultural/policy tests | `POST /game/wonder/commission`, `/game/policy/branch` |
| **B** | Competition + player agent | `receipts/BLOCK-B-CLOSURE-20260616.md` | competition + player_agent tests | `/game/competition/*`, `/game/player/strategy` |
| **C** | Alternate victory + soak + diplomacy + tooling | `receipts/BLOCK-C-CLOSURE-20260616.md` | `tests/test_wp_grok_block_c_001.py` | cultural/domination epilogue, `/game/mechanics/status`, `civforge_cli snapshot` |
| **D** | `:8081` JWT identity on mutators | `receipts/BLOCK-D-CLOSURE-20260616.md` | `tests/test_wp_grok_block_d_001.py` | `GET /game/auth/status`, JWT via `dawsos-auth-prototype` |

**Total pytest (anchor):** see `config/work_pack_registry.yaml` → `anchor.pytest_total` (147 after Block D).

**Execution receipts:**

- `receipts/cursor-execution-wp-grok-block-a-20260616.md`
- `receipts/cursor-execution-wp-grok-competition-depth-001-20260616.md`
- `receipts/cursor-execution-wp-grok-player-agent-001-20260616.md`
- `receipts/cursor-execution-wp-grok-block-c-20260616.md`
- `receipts/cursor-execution-wp-grok-block-d-20260616.md`

---

## 3. Architecture anchor (do not re-litigate)

```
POST /advance_turn
  → orchestrator.advance_cycle()
  → run_turn_simulation()
      MechanicsRegistry.pass_through_tick()   # diplomacy (+ AI proposals), competition, lanes, civstudy
      run_simulation_layer()
        sync_alternate_victory_outcomes()       # cultural_alternate | domination
        sync_victory_milestones()             # joint @ 100%
  → victory/defeat receipts
```

- **Tick order:** `mechanics_first_then_alternate_victory_then_milestones`
- **Milestone sync decision:** `docs/SIM_MILESTONE_SYNC_DECISION_V1.md` (stay in simulation layer)
- **Identity:** `dawsos-auth-prototype` `:8081` JWT — `backend/auth_identity.py`, `tools/dawsos_auth_identity_client.py`
- **Nexus:** `:8082` telemetry + machine satellite only — `tools/dawsos_auth_client.py`
- **Retired:** Godot, `WP-GROK-AGENT-VS-AGENT-003` monolith

---

## 4. Auth model (Block D)

| Mode | Env | Mutators |
|------|-----|----------|
| Local dev (default) | unset | Open |
| Require auth | `CIVFORGE_REQUIRE_AUTH=1` | Static token **or** govern JWT from `:8081` |
| Public exposure | `CIVFORGE_PUBLIC_MODE=1` + token | Same |

**Operator flow:**

```bash
# Terminal 1 — auth prototype
cd ~/Documents/GitHub/dawsos-auth-prototype
python3 -m uvicorn backend.auth_api:app --host 127.0.0.1 --port 8081

# Terminal 2 — kernel with auth required
cd ~/CivForge
export CIVFORGE_REQUIRE_AUTH=1
bash tools/start-kernel-8080.sh

python3 tools/civforge_cli.py auth register-device civforge-player pk-demo
python3 tools/civforge_cli.py auth token civforge-player govern
# Use returned JWT: Authorization: Bearer <token>
curl -s http://127.0.0.1:8080/game/auth/status | python3 -m json.tool
```

---

## 5. Grok lane rules

### Must do

- Read registry + this pack each session
- Author **planning-class** PRIMEs for **new** work only (save slots, turn pacing, wonder card-text)
- Link Cursor execution receipts when validating planning against landed code
- Use envelope template in `receipts/HANDOFF-GROK-PLANNING-QUEUE-20260616.md` §4

### Must not do

- Re-open Blocks A/B/C/D or RESUBMIT PRIMEs
- Claim `landed`, `closed`, `live` without tier-1 receipt + HEAD
- Restart `:8080`, commit, push, or mutate wt/dawsOS promotion truth
- Resurrect Godot, agent-vs-agent monolith, or parallel registry modules

### Superseded PRIMEs (report-only)

| ID | Superseded by |
|----|----------------|
| WP-HINDSIGHT-DEBT-ANALYSIS-001 | `docs/DEBT_REGISTER_V1.md` |
| WP-HISTORY-ORPHAN-REVIEW-042 | Orphan inventory — do not execute |
| WP-TOOLING-AWARENESS-PROPOSAL-001 | WP-TOOLING-AWARENESS-001 (Block C) |
| WP-GROK-AGENT-VS-AGENT-003 | Block B competition + player agent |

---

## 6. Next planning queue (post Block D)

| Priority | Topic | Lane |
|----------|-------|------|
| P2 | Save slots / session export JSON | Cursor WP when Mike ignites |
| P2 | Turn pacing / action costs | Cursor WP |
| P2 | Wonder card-text depth (D-M2) | Cursor WP |
| P3 | Vercel deploy | Platform / optional |

No Cursor execution WPs are open until Mike ignites in chat.

---

## 7. New WP envelope (copy for Grok)

```json
{
  "kind": "refactor_proposal",
  "work_pack_id": "WP-GROK-...",
  "planning_lane": true,
  "execution_authority": "cursor",
  "payload": {
    "target_files": ["backend/...", "tests/..."],
    "changes": ["..."],
    "non_goals": ["Godot", "8082 authority", "full sim replacement"]
  },
  "acceptance": ["pytest pass", "/state field X"],
  "rollback": "git revert paths..."
}
```

---

## 8. Verification checklist (operator)

```bash
cd ~/CivForge
git rev-parse --short HEAD
python3 -m pytest tests/ -q
bash tools/verify-truth-anchor.sh
bash tools/check-agent-shell-hygiene.sh
bash tools/validate-game.sh --read-only
curl -s http://127.0.0.1:8080/game/mechanics/status | python3 -m json.tool
curl -s http://127.0.0.1:8080/game/auth/status | python3 -m json.tool
python3 tools/civforge_cli.py snapshot
open http://127.0.0.1:8080/dashboard
```

---

## 9. Related docs

| Doc | Purpose |
|-----|---------|
| `docs/TRUTH_ORDER.md` | Authority stack |
| `docs/DEBT_REGISTER_V1.md` | Engineering debt |
| `docs/GAME_ENGINE_IMPLEMENTATION_GAP_INVENTORY_V1.md` | Remaining gaps |
| `docs/SIM_MILESTONE_SYNC_DECISION_V1.md` | REFACTOR-SIM-002 decision |
| `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` | 8080/8081/8082 planes |
| `prompts/grok_swarm_handoff_seed.md` | Short Grok session seed |

**End of handoff pack.**
