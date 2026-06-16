# Truth Order — CivForge authority stack

**Status:** `current` (2026-06-16)  
**Purpose:** Stop truth-plane collision between Grok narrative, handoff docs, git, and live kernel.

---

## 1. Read order (before any claim)

| Tier | Source | Use for |
|------|--------|---------|
| **0** | `git rev-parse --short HEAD` on `main` | Code truth anchor |
| **1** | `receipts/cursor-execution-*.md` for the WP | Execution proof (tests, routes, commit) |
| **2** | `config/work_pack_registry.yaml` | WP lifecycle (`closed` / `planning` / `retired`) |
| **3** | `receipts/HANDOFF-GROK-CONSOLIDATED-20260616.md` §5 | **Scope authority** for Block A/B envelopes |
| **4** | Live `GET http://127.0.0.1:8080/state` | Runtime behavior (after kernel restart on HEAD) |
| **5** | Grok PRIME receipts | Planning input only — **never** closure proof |
| **6** | Chat history | Context hints only — **not** authority |

**Freshest tier-1 receipt wins** over Grok PRIMEs still marked `planning`.

---

## 2. Repo boundaries (do not conflate)

| Repo / plane | Role |
|--------------|------|
| **CivForge** (`~/CivForge`, `main`) | Game kernel `:8080`, Cursor execution, `receipts/cursor-execution-*` |
| **gravity-mosaic-knowledge-graph** | Separate project; deploy only via `tools/deploy-gravity-mosaic/deploy.sh` |
| **dawsOS wt** (`~/.openclaw/dawsos-workspace-wt`) | OpenClaw promotion truth (`reports/ops/*`) — not CivForge game state |

---

## 3. Mandatory verification commands

```bash
cd ~/CivForge
git rev-parse --short HEAD
python3 -m pytest tests/ -q
bash tools/verify-truth-anchor.sh              # read-only; fails if anchor.head drift
bash tools/verify-truth-anchor.sh --sync       # after land commit only
bash tools/check-agent-shell-hygiene.sh        # stale Cursor wrapper shells
bash tools/validate-game.sh --read-only   # or --restart after code change
```

---

## 4. Block A closure (current)

| Item | Value |
|------|-------|
| Status | **closed** |
| Commit | `1037950` (+ receipt doc `b3f3eb3`) |
| Receipt | `receipts/cursor-execution-wp-grok-block-a-20260616.md` |
| Index | `receipts/BLOCK-A-CLOSURE-20260616.md` |
| pytest | 138 (Block A: 12, Block B: 12, Block C: 8, hygiene + baseline) |

**Do not re-ignite Block A or Block B.** Grok RESUBMIT PRIMEs are **superseded**.

---

## 4b. Block C closure (Cursor execution)

| Field | Value |
|-------|--------|
| Status | **closed** |
| Receipt | `receipts/cursor-execution-wp-grok-block-c-20260616.md` |
| Closure | `receipts/BLOCK-C-CLOSURE-20260616.md` |
| Index | `config/work_pack_registry.yaml` → `blocks.block_c` |
| pytest | 138 |

**Do not re-ignite Block C.** Alternate victory, soak, AI diplomacy, and tooling WPs are closed.

---

## 4c. Block D closure (Cursor execution)

| Field | Value |
|-------|--------|
| Status | **closed** |
| Receipt | `receipts/cursor-execution-wp-grok-block-d-20260616.md` |
| Closure | `receipts/BLOCK-D-CLOSURE-20260616.md` |
| Grok pack | `receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md` |
| pytest | 147 |

**Do not re-ignite Block D.** JWT identity on mutators is closed.

---

## 5. Next open work

Blocks A, B, C, and D are **closed** — see closure receipts under `receipts/BLOCK-*-CLOSURE-20260616.md`.

**Grok bootstrap:** read `receipts/HANDOFF-GROK-EXECUTION-PACK-20260616.md` first.

Next planning: save slots, turn pacing, wonder card-text depth — no duplicate subsystems.

---

## 6. Banned closure language (without tier-1 receipt)

`completed`, `landed`, `live`, `deployed`, `verified`, `pushed`, `fully extended`, `100% executable`, `fully playable`, `registry updated` (unless git diff proves it).

Allowed with receipt link: `closed`, `execution proof at HEAD`, `pytest N passed`.

See `docs/AGENT_CLAIMS_POLICY.md`.
