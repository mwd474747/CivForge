# CivForge swarm class v1 — dawsOS-shaped, not dawsOS-registered

**Status:** `current`  
**Label:** planning + architecture — not wt promotion truth  
**Related:** `docs/EXECUTION_LANE_V2.md`, `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`

---

## Verdict

CivForge is **recognizably dawsOS-shaped** (proposal-first, receipt-first, bounded side effects, role separation, quality gates, bridge boundaries) but is **not the same class** of swarm as planned/registered dawsOS swarms in wt `swarm-registry.v0.json`.

| Dimension | CivForge | dawsOS swarms |
|-----------|----------|---------------|
| **Authority** | Game/governance kernel on `:8080` | Workflow-owned, registry-backed operating machinery |
| **Registration** | `civforge_kernel` in governed-connectors (Nexus satellite) | `swarm-registry.v0.json` entry with coordinator/delegates |
| **Receipts** | `receipts/*.md` + SQLite (local truth) | Required `ops.*` receipt types in wt |
| **Side effects** | Bounded to CivForge repo/kernel | `allowed_side_effect_class` (e.g. `write_reports`) |
| **Human review** | FunForge gate + optional operator | `human_review_required: true` on registry rows |
| **Fanout / join** | In-game AgentBrains + orchestrator | `fanout_max`, `join_strategy`, `conflict_resolution_mode` |

**Similarity:** governance *pattern*.  
**Difference:** governance *authority* and wt workflow ownership.

---

## Three layers (do not conflate)

### Layer 1 — Grok swarm (planning only, grok.com)

- Authors `WP-*` work packs and PRIME receipts (planning class)
- Uses dawsOS MCPs on grok.com (gitnexus, memory, trivium) for *planning* — not execution
- **Does not** run Mac Studio terminal, commit, or advance `:8080` turns
- See `docs/EXECUTION_LANE_V2.md` §2

### Layer 2 — Local kernel agents (lightweight game/governance personas)

- `grok`, `harper`, `sebastian` (and lane specialists) are **`AgentBrain`** simulation personas
- `GovernanceOrchestrator.advance_cycle()` drives: decide → propose → FunForge → gate → receipt
- These are **in-kernel gameplay/governance actors**, not grok.com swarm delegates and not wt `chief_of_staff` / `evidence` roles
- See `core/orchestrator.py`, `core/agent_brain.py`, `agents/role_registry.json`

### Layer 3 — Nexus bridge (telemetry + proposal intake)

- Heartbeat push to dawsos-nexus `:8082`
- Command poll → local `/governance/propose` only — **no direct mutations**
- No wt `workflow_dispatch`, no `reports/ops` writes, no wt source edits
- See `docs/dawsos_nexus_reference.md`, `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` §4–5

---

## dawsOS swarm registry (reference only)

wt `engine-src/active/config/ops/swarm-registry.v0.json` defines formal swarms with:

- `coordinator_agent` (e.g. `chief_of_staff`)
- `delegate_agents` (e.g. `research_local`, `evidence`, `review`)
- `delegate_model_policy`, `fanout_max`, `join_strategy`
- `required_receipts`, `human_review_required`, `allowed_side_effect_class`

wt `agent-spec.yaml` defines orchestrator roles: discovery, planning, evidence, review, engineering, chief_of_staff.

**CivForge does not register here.** CivForge borrows the *ideas* (receipts, gates, role separation) without becoming a wt workflow satellite.

---

## Mapping (informal, not registry-backed)

| CivForge concept | dawsOS analogue | Notes |
|------------------|-----------------|-------|
| FunForge gate | review gate / quality checkpoint | Local `:8080`, not wt reducer |
| Harper AgentBrain | evidence / research delegate | In-sim only |
| Sebastian AgentBrain | review / separation delegate | In-sim only |
| Grok swarm WP | planning lane | grok.com, not registry row |
| Cursor executor | engineering delegate | Mac Studio, CivForge git |
| OpenClaw escalation | chief_of_staff + wt truth | wt only when triggered (`openclaw-chief-of-staff` in role_registry) |
| Nexus poller | command intent bridge | propose-only |
| In-kernel `grok` AgentBrain | forge-coordinator (Layer 2) | **Not** grok.com swarm — see `agents/role_registry.json` naming_notes |

---

## Work packs (swarm-field borrow)

CivForge WPs borrow dawsOS swarm-registry **fields** locally without wt registration:

- `receipt_class`, `authority_lane`, `side_effect_class`, `required_receipt_links`
- Template: `docs/WORK_PACK_TEMPLATE_V1.md`

### P2 — Sequential join (implemented)

`GovernanceOrchestrator.advance_cycle()` uses `core/swarm_join.py`:

- **Join order:** harper → sebastian → grok (`evidence_then_review`)
- **fanout_max:** 3
- **Conflict:** deploy vs verify/research → `delegate_conflict` → `NEEDS_REVIEW`
- Receipt index classifies files by `receipt_class`

---

## Validation tools — stateful caveat

| Tool | Advances turns? | Use when |
|------|-----------------|----------|
| `GET /state` | No | Architecture review, posture reads |
| `pytest` / `py_compile` | No | Code validation |
| `civforge_*_posture.py` | No | Governance parity checks |
| `validate-game.sh` | **Yes** (via `turnkey-multi-ui-full.sh` CLI advances) | Post-implementation verify |
| `turnkey-cursor-local.sh` | **Yes** (explicit `--advances N`) | Cursor execution proof |

For **read-only** architecture review, use:

```bash
bash tools/validate-game.sh --read-only
```

Never run full `validate-game.sh` during report-only reviews unless turn advance is intended.

---

## Canonical cross-refs

| Doc | Repo |
|-----|------|
| This file | CivForge |
| `CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` | CivForge (wt pointer) |
| `swarm-registry.v0.json` | dawsOS wt |
| `agent-spec.yaml` → orchestrator roles | dawsOS wt |
| `EXECUTION_LANE_V2.md` | CivForge |
