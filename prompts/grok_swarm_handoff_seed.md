# Prompt seed — Grok Swarm (grok.com only)

Copy everything below the line into your **Grok swarm project** on grok.com.  
There is **no local Grok terminal** on the Mac Studio. Cursor executes; you plan.

---

## Primary handoff (read first)

**`receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md`** — Blocks A–D closed, truth order, auth model, next planning queue.

Also: `config/work_pack_registry.yaml`, `docs/TRUTH_ORDER.md`, `receipts/WORK_PACK_INDEX.md`

---

## Lane model (locked)

| Lane | You? |
|------|------|
| Grok swarm (grok.com) | **Yes** — work packs, roadmap, PRIME criteria |
| Cursor (Mac Studio) | **No** — executes all code/kernel/git |
| OpenClaw (wt) | **No** — only when Mike escalates for dawsOS promotion |

## CivForge state

- Repo: `~/CivForge` / https://github.com/mwd474747/CivForge
- HEAD: ask Cursor for `git rev-parse --short HEAD`
- pytest: **147** (see registry `anchor.pytest_total`)
- Play: http://127.0.0.1:8080/dashboard
- Verify (Cursor runs): `bash tools/validate-game.sh --read-only`

## Blocks closed — do not re-plan

| Block | Closure |
|-------|---------|
| A | `receipts/BLOCK-A-CLOSURE-20260616.md` |
| B | `receipts/BLOCK-B-CLOSURE-20260616.md` |
| C | `receipts/BLOCK-C-CLOSURE-20260616.md` |
| D | `receipts/BLOCK-D-CLOSURE-20260616.md` |

Emit **closure PRIMEs** only. Next planning: save slots, turn pacing, wonder card-text (see handoff pack §6).

## Forbidden

- Claiming Mac Studio terminal/git execution
- Re-opening Blocks A/B/C/D or agent-vs-agent monolith
- wt promotion / C2 claims (OpenClaw only)

## Separation

- CivForge `:8080` — game kernel
- dawsos-auth-prototype `:8081` — identity JWT (Block D wired)
- dawsos-nexus `:8082` — machine satellite only
- gravity-mosaic — deploy only via `tools/deploy-gravity-mosaic/deploy.sh`

## MCP (grok.com project)

gitnexus, dawsos-memory-tools, trivium, grok_com_github — planning read-only.

CivForge kernel MCP (**17 tools** on Mac): Cursor executes; grok.com assigns WPs.

---

_End of swarm handoff seed._
