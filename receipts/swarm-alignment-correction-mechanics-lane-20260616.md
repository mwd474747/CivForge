# Swarm Alignment Correction — Mechanics Lane (2026-06-16)

**Label:** `current` — Cursor execution proof attached  
**For:** Grok swarm ingest (WP-CORRECTION-INGEST-VALIDATION-029 follow-up)  
**Cursor execution:** `receipts/cursor-execution-wp-grok-mech-district-001-20260616.md`

---

## Retired claims (do not repeat)

| Claim | Why wrong |
|-------|-----------|
| `MAC STUDIO TRUTH LOCKED` | Grok has no Mac execution authority |
| `FunForge 100.0` without `/state` | Forbidden — cite literal `fun_score` |
| Bash blocks in Grok PRIME as self-proof | Planning-class only; link Cursor execution receipt |
| `8082` as mechanics proposal lane | Mechanics = `:8080` `/game/mechanics/*`; `:8082` = Nexus bridge |
| `civforge_cli status \| grep mechanics` (old CLI) | Fixed: `cmd_status` now exposes `mechanics_proposals` / `mechanics_overrides` |
| `+1 sci on adjacency` for district override | Wrong — `district_yield_override` patches **district pulse yield_bonus** |

---

## Cursor-completed work (2026-06-16)

1. Restarted kernel on `4b57418` — `/state` now exposes `mechanics_proposals`, `mechanics_overrides`, `session_phase`
2. Executed **WP-GROK-MECH-DISTRICT-001** propose→gate→apply (proposal `6edc05db`, APPLIED)
3. `pytest` 53 passed, posture PASSED, contract parity pass
4. `civforge_cli.py status` includes mechanics fields for honest verify

---

## Grok role (locked)

| Grok | Cursor/Mike |
|------|-------------|
| Author `WP-*` + proposal JSON | Restart `:8080`, MCP/CLI execute |
| Planning-class PRIME | Execution receipts with literal probes |
| Specify acceptance criteria | pytest, posture, live `/state` |

---

## Close Grok PRIME with

- `receipt_class: planning`
- Link: `receipts/cursor-execution-wp-grok-mech-district-001-20260616.md`
- Cite `/state` fields from Cursor receipt (not re-run bash on grok.com)
