# CivForge Repo Hygiene

**Updated:** 2026-06-16  
**Status:** `current` — active tree is FastAPI kernel + Python `core/` only

---

## Active tree (canonical)

| Path | Role |
|------|------|
| `backend/` | FastAPI kernel (`sim_api.py`), game mechanics modules |
| `core/` | Orchestrator, AgentBrain, FunForge, MechanicsRegistry |
| `frontend/` | Dashboard (`index.html`) |
| `tools/` | CLI, MCP, validate-game, verify-truth-anchor, check-agent-shell-hygiene, start-kernel-8080 |
| `docs/` | Lane model, boundary, play guide |
| `receipts/` | **Execution + planning receipts only** (not runtime cycle dumps) |

**Removed 2026-06-16:** entire `_archive/` (Godot MVP, pre-realign orphans, auth-prototype stubs). History lives in git only.

**Deleted remote branch:** `feature/full-hybrid-scaffold-v1` (pre-realign; PR #1 superseded by repo realign).

---

## Branches

- **`main`** — sole active branch
- No long-lived feature branches; use Cursor execution receipts + short-lived local branches if needed

---

## Receipts policy

**Commit:** cursor-execution, handoff, planning PRIME, LOCKED plans, posture `*-latest.*`

**Do not commit** (`.gitignore`):

- `receipts/governance-cycle-*.md`
- `receipts/governance-gate-*.md`
- `receipts/governance-proposal-*.md`
- `receipts/game-reset-*.md`
- `receipts/gravity-rec-*.md`
- `receipts/defeat-outcome-*.md`
- `receipts/military-conflict-defeat-sim-*`
- `receipts/openclaw-governance-turnkey-*.md`
- `receipts/openclaw-ops-run-*.md`

If previously tracked, remove with `git rm --cached` once; files may remain locally for debugging.

---

## Pre-push checklist

```bash
cd ~/CivForge
git status --short
python3 -m pytest tests/ -q
bash tools/verify-truth-anchor.sh              # read-only anchor check
bash tools/check-agent-shell-hygiene.sh        # optional; --kill stale Cursor wrappers
bash tools/validate-game.sh    # optional; needs :8080
```

**After a land commit** (when `anchor.head` should move):

```bash
bash tools/verify-truth-anchor.sh --sync
git add config/work_pack_registry.yaml && git commit -m "Sync registry anchor.head to land commit."
```

Verify accepts `anchor.head == HEAD` **or** `anchor.head == HEAD~1` when the latest commit is the anchor sync follow-up (land commit + registry sync = two-commit pattern).

Default verify mode is **read-only** — it does not mutate the registry (2026-06-16 hygiene fix).

- No `_archive/` or Godot paths in active docs
- No `tools/auth-prototype/` references (identity → sibling `dawsos-auth-prototype` repo)
- `docs/EXECUTION_LANE_V2.md` lane model unchanged unless intentional

---

## Separation (unchanged)

CivForge governs; **gravity-mosaic** and **dawsos-auth-prototype** are separate repos. Deploy only via `tools/deploy-gravity-mosaic/deploy.sh`.

See `SEPARATION.md`, `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`.
