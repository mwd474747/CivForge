# Work Pack Lifecycle

**Status:** `current`  
**Registry:** `config/work_pack_registry.yaml`

---

## State machine

```
planning ──(Mike: "Execute WP-…")──► ignited ──► executing ──► closed
    │                                    │
    └──────── superseded / retired ◄─────┘ (scope replaced or rejected)
```

| State | Who sets it | Meaning |
|-------|-------------|---------|
| `planning` | Grok | Criteria / envelope only — **no code truth** |
| `ignited` | Mike | Explicit execute command to Cursor |
| `executing` | Cursor | Work in progress on branch or wt |
| `closed` | Cursor | `cursor-execution-*` receipt + pytest + commit on `main` |
| `retired` | Consolidated handoff | Must not execute (e.g. AGENT-VS-AGENT-003) |
| `superseded` | Cursor doc update | Replaced by closure doc or process hardening |

---

## Grok PRIME rules

1. **First lines of every PRIME:**
   ```
   HEAD: <run git rev-parse or cite Cursor receipt>
   Registry: config/work_pack_registry.yaml → <WP id> → lifecycle
   Status: planning • no execution claimed
   ```
2. Copy §5 envelopes **verbatim** from `HANDOFF-GROK-CONSOLIDATED-20260616.md` — do not paraphrase acceptance criteria.
3. If registry says `closed`, emit **closure PRIME** only (`closure_class: planning_validated_against_cursor_execution`) — do not re-plan.
4. Never assign Cursor meta-analysis WPs (bias/root-cause/hindsight) unless Mike explicitly ignites.

---

## Cursor execution rules

1. One WP family per commit when possible.
2. Write `receipts/cursor-execution-wp-<slug>-YYYYMMDD.md`.
3. Update `config/work_pack_registry.yaml` (`head`, `pytest_total`, WP `lifecycle: closed`).
4. Run full `pytest tests/ -q` + `bash tools/verify-truth-anchor.sh`.
5. Restart kernel when routes/state shape change: `bash tools/start-kernel-8080.sh`.

---

## Closure checklist

- [ ] pytest pass count recorded
- [ ] `git rev-parse --short HEAD` in receipt
- [ ] Registry YAML updated
- [ ] Consolidated handoff §0 / closure doc updated if block completes
- [ ] `IMPLEMENTATION_STATUS.md` factual counts only
