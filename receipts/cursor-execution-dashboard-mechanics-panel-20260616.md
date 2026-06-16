# Cursor Execution — Dashboard Mechanics Proposals Panel

**Date:** 2026-06-16  
**Label:** `prototype-only`  
**Authority lane:** `cursor`  
**Receipt class:** `execution`

---

## Summary

Added **Mechanics Proposals** tab to `frontend/index.html` — list, propose, gate, and apply runtime mechanics proposals against live `:8080` kernel (parity with MCP/API lane).

---

## Changes

| Path | Change |
|------|--------|
| `frontend/index.html` | New tab + panel: summary, JSON propose form, gate/apply per proposal |
| `.gitignore` | Ignore ephemeral runtime receipts (`game-reset-*`, `governance-cycle-*`, etc.) |
| `receipts/HANDOFF-GROK-SWARM-20260616.md` | HEAD → `c9b2db3` |
| `receipts/work-pack-grok-policy-003.md` | Grok planning WP for `send_envoy` action |
| `tools/validate-game.sh` | (prior) reset before probes + 16 MCP assertions |

---

## Validation

```bash
cd ~/CivForge
bash tools/start-kernel-8080.sh
bash tools/validate-game.sh --read-only
bash tools/turnkey-governance-posture.sh
python3 -m pytest tests/ -q
```

Dashboard: `http://127.0.0.1:8080/dashboard` → **Mechanics Proposals** tab.

---

**HEAD:** _(filled at commit)_
