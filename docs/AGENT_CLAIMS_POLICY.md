# Agent Claims Policy — anti-drift hardening

**Status:** `current` (2026-06-16)  
**Applies to:** Grok swarm, Cursor, any agent writing CivForge status text.

---

## 1. Prefix (mandatory)

### Grok (every response touching CivForge status)

```
HEAD: <sha from registry or "unknown — ask Cursor">
WP lifecycle: <from config/work_pack_registry.yaml>
Status: planning • no execution claimed
```

Skip only for pure game-design brainstorming with zero status claims.

### Cursor (execution complete)

```
Tag: current | prototype-only | report-only
Receipt: receipts/cursor-execution-*.md @ <sha>
pytest: <N> passed
```

---

## 2. Banned words without tier-1 receipt

| Banned | Use instead |
|--------|-------------|
| completed / done (for code) | `closed @ <sha>` + receipt path |
| live / deployed | `kernel probe OK` or `vercel per Mike approval` |
| verified / confirmed | cite pytest output or curl literal |
| registry updated | cite file diff or `extends existing module X` |
| fully playable / 100% executable | list what pytest + `/state` actually prove |
| expert swarm reviewed | omit — not verifiable |

---

## 3. Known false claims (do not repeat)

| Claim | Truth |
|-------|-------|
| "Missing CorpusCardRegistry" | **False** — `backend/corpus_card_registry.py` since clarity bundle |
| "Block A still planning" | **False** — closed @ `1037950`, see `BLOCK-A-CLOSURE` |
| "civstudy_policy_tree registry updated" | **Misleading** — Block A extends bridge + `policy_branching.py`, not new registry module |
| "8082 live bidirectional control" | **False** — thin telemetry bridge only (`docs/SIM_GAME_BOUNDARY_V1.md`) |

---

## 4. Retraction

If a prior message over-claimed, Grok adds:

```
Retraction: prior claim "<X>" superseded by <receipt or registry state>.
```

Do not leave stale optimism in chat without pointing to updated registry.

---

## 5. Scope authority

**Single envelope source:** `receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md` §5.

Grok PRIMEs that paraphrase §5 are **planning hints only** — Cursor executes from §5 + Mike ignition, not from RESUBMIT variants.
