# OpenClaw Escalation Packet v1

**Status:** `current`  
**Label:** `approval-gated` — invoke OpenClaw only for triggers below  
**Replaces:** routine CivForge ops via OpenClaw (see `EXECUTION_LANE_V2.md`)

---

## When to escalate (OpenClaw required)

| Trigger | wt artifact | Action |
|---------|-------------|--------|
| Promotion / C2 claim | `decision-window-reducer-latest.json` | Refresh projection + reducer |
| Boundary apply ready | `boundary-approval-decision-menu-latest.json` → `ready_decision_ids` | Execute exact approval packet |
| API dispatch blocked | `workflow-dispatch-health-probe-latest.json` → fail | Runtime repair (LaunchAgent) |
| GAP-PROD-002 closure | `gap-prod-002-closure-audit-latest.json` | wt land + receipt |
| Scheduled sustainment | cron / Nexus fleet builders | Autonomous (not per CivForge task) |

---

## When NOT to escalate (Cursor handles)

- CivForge commits, kernel `:8080`, poller, Vercel
- `validate-game.sh`, pytest, MCP tools
- Grok handoff docs, work packs
- CivForge `receipts/*.md` (not promotion truth)

---

## Escalation packet template (Cursor → OpenClaw)

```markdown
# Escalation: [ID]
**From:** Cursor
**Trigger:** [row from table above]
**wt receipt:** path + generated_at + status
**CivForge HEAD:** `git rev-parse --short HEAD`
**Blocked action:** [what Cursor cannot do]
**Requested:** [exact OpenClaw action]
```

---

## wt registry canon

`engine-src/active/config/ops/governed-connectors-registry.v1.json` → `civforge_kernel`

Pointer-only boundary: `engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`

---

## Minimum wt receipt packet (promotion claims only)

- `reports/ops/dawsos-projection-pipeline-receipt-latest.json`
- `reports/ops/workflow-dispatch-health-probe-latest.json`
- `reports/ops/decision-window-reducer-latest.json`
- `reports/ops/boundary-approval-decision-menu-latest.json`

CivForge `receipts/openclaw-ops-run-*.md` = **prototype-only**; not substitute for wt receipts.
