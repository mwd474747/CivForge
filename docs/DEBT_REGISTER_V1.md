# Debt Register v1

**Status:** `current` (post Block D — run `git rev-parse --short HEAD` for anchor)  
**Not promotion truth** — engineering backlog for CivForge kernel only.

---

## High

| ID | Debt | Notes |
|----|------|-------|
| ~~D-H1~~ | ~~Cultural path has no win epilogue~~ | **Fixed Block C** — `alternate_victory` + epilogue_message + dashboard overlay |
| D-H2 | Handoff / PRIME proliferation | Mitigated by `HANDOFF-GROK-EXECUTION-PACK-20260616.md` + registry |
| D-H3 | Grok temporal staleness | Process fix in `AGENT_CLAIMS_POLICY.md`; requires Grok to read registry each session |

---

## Medium

| ID | Debt | Notes |
|----|------|-------|
| D-M1 | Policy branch metadata split | `policy_branch_extensions()` in metadata; checklist in `policy_branching.py` — intentional |
| D-M2 | Wonder effects are soft lane bumps | Not full card-text simulation |
| D-M3 | ~~validate-game Block B probes missing~~ | **Fixed** |
| D-OPS-1 | ~~verify auto-sync anchor chase~~ | **Fixed** |
| D-M4 | ~~Block B not started~~ | **Closed** Block B |
| D-M5 | ~~AI diplomacy initiative missing~~ | **Fixed Block C** — `tick_ai_negotiation_proposals` |
| D-M6 | ~~Domination victory path missing~~ | **Fixed Block C** — `domination_victory.py` |
| D-M7 | ~~`:8081` JWT on mutators~~ | **Fixed Block D** — `auth_identity.py` + `/game/auth/status` |

---

## Low / closed misconceptions

| ID | Was claimed | Actual |
|----|-------------|--------|
| D-L1 | Missing CorpusCardRegistry | **Closed** |
| D-L2 | Dashboard missing multi-agent UI | **Stale** |

---

## Retired (do not rebuild)

- Godot MVP / `_archive/` hybrid scaffold
- `WP-GROK-AGENT-VS-AGENT-003` monolith
- Local Grok terminal executor
