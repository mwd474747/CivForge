# AGENTS.md - CivForge Agentic Architecture

**Bootstrap anchor:** `docs/TRUTH_ORDER.md` → `config/work_pack_registry.yaml` → `receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md`

---

## Grok planning bootstrap

Read **`receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md`** first (Blocks A–D closed, auth model, next queue).  
Short seed: `prompts/grok_swarm_handoff_seed.md`

---

## Execution lanes (canonical)

| Lane | Runtime | Role |
|------|---------|------|
| **Grok swarm** | grok.com | Planning PRIMEs only — **no Mac Studio terminal** |
| **Cursor** | Cursor IDE | **All local execution** — code, tests, git, kernel |
| **OpenClaw** | wt / escalation | dawsOS promotion — **only when triggered** |

Full lane map: `docs/EXECUTION_LANE_V2.md`  
Claims policy: `docs/AGENT_CLAIMS_POLICY.md`  
WP lifecycle: `docs/WORK_PACK_LIFECYCLE.md`

---

## Every session (all agents)

1. `cd ~/CivForge && git rev-parse --short HEAD`
2. Read `config/work_pack_registry.yaml` — check WP `lifecycle` before planning or claiming closure
3. Read `docs/TRUTH_ORDER.md` — do not conflate CivForge receipts with dawsOS `reports/ops/*`
4. If discussing landed work: open matching `receipts/cursor-execution-*.md` — **not** stale Grok PRIMEs

**Block A (closed):** `receipts/BLOCK-A-CLOSURE-20260616.md`  
**Block B (closed):** `receipts/BLOCK-B-CLOSURE-20260616.md`  
**Block C (closed):** `receipts/BLOCK-C-CLOSURE-20260616.md`  
**Block D (closed):** `receipts/BLOCK-D-CLOSURE-20260616.md` — JWT identity on mutators.

---

## Grok swarm (grok.com — planning only)

**Mandatory prefix:**

```
HEAD: <from registry or "unknown — ask Cursor">
WP lifecycle: <from config/work_pack_registry.yaml>
Status: planning • no execution claimed
```

**Does:**
- Author `WP-*` with §5 envelopes **verbatim** from `receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md`
- Close landed WPs with `closure_class: planning_validated_against_cursor_execution` + Cursor receipt link
- Retire `WP-GROK-AGENT-VS-AGENT-003` and all `WP-GROK-BLOCK-A-RESUBMIT-*` PRIMEs

**Does not:**
- Claim `completed`, `live`, `deployed`, `verified` without Cursor tier-1 receipt
- Re-plan closed Block A
- Assign Cursor meta-analysis WPs (bias/root-cause/hindsight) unless Mike explicitly ignites

Handoff seed: `prompts/grok_swarm_handoff_seed.md`

---

## Cursor (local executor)

**Does:**
- Implement ignited WPs one family at a time
- Write `receipts/cursor-execution-*.md` with `git rev-parse --short HEAD` + pytest count
- Update `config/work_pack_registry.yaml` (`pytest_total`, WP lifecycle) — use `verify-truth-anchor.sh --sync` for `anchor.head`
- Run `bash tools/verify-truth-anchor.sh` (read-only) and `bash tools/validate-game.sh`

**Does not:**
- wt commit / C2 / storage apply / LaunchAgents (escalate via `docs/OPENCLAW_ESCALATION_PACKET_V1.md`)

---

## OpenClaw (escalation only)

- wt `reports/ops/*` = promotion truth — not CivForge game state
- See `docs/OPENCLAW_ESCALATION_PACKET_V1.md`

---

## Kernel truth

- **Module:** `backend/sim_api.py` + `core/` on `:8080`
- **Routing gate:** `GET /state` includes `work_pack_registry` (registry summary)
- **Restart after code change:** `bash tools/start-kernel-8080.sh`
- **Verify:** `bash tools/verify-truth-anchor.sh` then `bash tools/validate-game.sh --read-only`
- **After land commit:** `bash tools/verify-truth-anchor.sh --sync` and commit registry anchor
- **Agent shell hygiene:** `bash tools/check-agent-shell-hygiene.sh` (`--kill` if stale wrappers found)

---

## In-game personas (simulation only)

`harper`, `sebastian`, `forge-coordinator` in AgentBrains — **not** grok.com swarm agents.  
Registry: `agents/role_registry.json`

---

## Current reality (2026-06-16)

| Item | Status |
|------|--------|
| Block A (wonder / cultural / policy) | **Closed** @ `1037950` |
| Block B (competition / player agent) | **Closed** — see `BLOCK-B-CLOSURE-20260616.md` |
| pytest | **130** |
| Dashboard | `GET /dashboard` on `:8080` — extend, do not rebuild |
| CorpusCardRegistry | `backend/corpus_card_registry.py` — **exists** |
| MCP tools | 17 — see `tools/mcp_server.py` |
| Debt backlog | `docs/DEBT_REGISTER_V1.md` |

Update this file via governed work pack + Cursor execution receipt only.
