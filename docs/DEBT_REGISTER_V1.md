# Debt Register v1

**Status:** `current` (post Block B @ `2530fc2`, hygiene @ `80dfbbf`)  
**Not promotion truth** — engineering backlog for CivForge kernel only.

---

## High

| ID | Debt | Notes |
|----|------|-------|
| D-H1 | Cultural path has no win epilogue | `alternate_victory_eligible` flag only; joint victory path unchanged |
| D-H2 | Handoff / PRIME proliferation | Mitigated by `config/work_pack_registry.yaml` + truth order — still many historical `.md` files |
| D-H3 | Grok temporal staleness | Process fix in `AGENT_CLAIMS_POLICY.md`; requires Grok to read registry each session |

---

## Medium

| ID | Debt | Notes |
|----|------|-------|
| D-M1 | Policy branch metadata split | `policy_branch_extensions()` in metadata; checklist in `policy_branching.py` — intentional, document in wiring inventory |
| D-M2 | Wonder effects are soft lane bumps | Not full card-text simulation |
| D-M3 | ~~validate-game Block B probes missing~~ | **Fixed** — competition + player_agent probes in validate-game |
| D-OPS-1 | ~~verify auto-sync anchor chase~~ | **Fixed** — verify read-only; `--sync` explicit after land |
| D-M4 | ~~Block B not started~~ | **Closed** — Block B @ BLOCK-B-CLOSURE-20260616 |

---

## Low / closed misconceptions

| ID | Was claimed | Actual |
|----|-------------|--------|
| D-L1 | Missing CorpusCardRegistry | **Closed** — exists, used by wonder commission |
| D-L2 | Dashboard missing multi-agent UI | **Stale** — `/dashboard` has map, agents, Block A controls |

---

## Retired (do not rebuild)

- Godot MVP / `_archive/` hybrid scaffold
- `WP-GROK-AGENT-VS-AGENT-003` monolith
- Local Grok terminal executor
