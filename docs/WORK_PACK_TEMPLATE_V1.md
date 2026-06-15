# Work Pack Template v1 (dawsOS swarm-field aligned)

**Status:** `current`  
**Use for:** Grok swarm planning receipts → Cursor execution  
**Not:** wt `swarm-registry` registration (CivForge stays external plane)

Copy this block into every new `WP-*` work pack.

---

## Header (required)

```markdown
# Work Pack: {Title}

**ID:** `WP-{FAMILY}-{NNN}`
**Lane:** `{lane/id}`
**Owner:** Grok swarm (planning) → **Cursor** (execution) | OpenClaw if `wt_escalation`
**Label:** `planning` | `prototype-only` | `current`

## Swarm alignment (CivForge-local — mirrors dawsOS registry fields)

| Field | Value |
|-------|-------|
| `receipt_class` | `planning` \| `execution` \| `posture` \| `governance_cycle` |
| `authority_lane` | `grok_swarm` \| `cursor` \| `openclaw` |
| `side_effect_class` | see taxonomy below |
| `human_review_required` | `true` if `wt_escalation` or operator gate; else `false` |
| `required_receipt_links` | list paths that must exist before closure |

### `side_effect_class` taxonomy

| Class | Executor | Allowed effects |
|-------|----------|-----------------|
| `planning_only` | Grok swarm | Work packs, PRIME criteria — no `:8080` mutation |
| `local_kernel` | Cursor | Kernel `:8080`, SQLite, receipts, poller |
| `local_git` | Cursor | CivForge repo commit/push, vercel |
| `wt_escalation` | OpenClaw | wt `reports/ops`, registry, boundary apply |

**Rule:** One primary `side_effect_class` per WP. Escalation requires explicit packet (`docs/OPENCLAW_ESCALATION_PACKET_V1.md`).

### `required_receipt_links` (closure)

| Closure type | Required links |
|--------------|----------------|
| Planning WP | `receipts/cursor-execution-*.md` with real `git HEAD` |
| Governance WP | `receipts/civforge-governance-posture-latest.json` → `pass` |
| OpenClaw ops | `receipts/openclaw-ops-run-*.md` + wt probe `generated_at` |

---

## Body sections

### Objective
One paragraph — what changes and why.

### Acceptance criteria
```bash
bash tools/turnkey-governance-posture.sh    # read-only default
# or bash tools/turnkey-cursor-local.sh     # when gameplay proof needed
git rev-parse --short HEAD
```

### Forbidden
- Fake HEAD / fun_score
- wt promotion claims from Grok swarm
- `civforge_cli.py status | grep vercel`

### Closure
`receipts/{family}-closure-YYYYMMDD.md` referencing this WP.

---

## dawsOS role mapping (informal)

| WP owner lane | dawsOS `governed_agents` analogue |
|---------------|----------------------------------|
| `grok_swarm` | `planning` |
| `cursor` | `engineering` |
| `openclaw` | `chief_of_staff` |
| Harper persona (in-sim) | `evidence` |
| Sebastian persona (in-sim) | `review` |

See `docs/CIVFORGE_SWARM_CLASS_V1.md`, `agents/role_registry.json`.
