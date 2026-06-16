# Repo Hygiene Cleanup — 2026-06-16

**Label:** `current`  
**Authority:** Cursor partner lane  
**HEAD:** set after commit

---

## Actions

| Action | Detail |
|--------|--------|
| Delete remote branch | `feature/full-hybrid-scaffold-v1` (pre-realign; PR #1 superseded) |
| Remove `_archive/` | 16 tracked files — Godot MVP, auth-prototype stubs, hybrid orphans |
| Untrack runtime receipts | 101 `governance-cycle-*`, 2 `military-conflict-defeat-sim-*`, 4 `openclaw-governance-turnkey-*` |
| `.gitignore` | Expanded ephemeral receipt patterns; removed `_archive/pre-realign-orphans/` |
| Docs | `docs/REPO_HYGIENE.md`, README, IMPLEMENTATION_STATUS, HANDOFF_CONTEXT, borrowable patterns |
| CLI | `tools/civforge_cli.py` — removed stale `tools/auth-prototype/` paths |
| Handoff | `HANDOFF-GROK-CONSOLIDATED-20260616.md` § hygiene note |

---

## Verification

```bash
cd ~/CivForge
git branch -r                    # origin/main only (no feature branches)
test ! -d _archive && echo OK    # no _archive dir
python3 -m pytest tests/ -q
python3 tools/civforge_contract_parity.py  # optional; stale_auth_bridge_ref should clear
```

---

## Not in scope

- Historical planning receipts under `receipts/` (orphan-cleanup, LOCKED plans) — kept for audit
- `receipts/_archive/` — gitignored; not in active tree
- wt/dawsOS promotion receipts
