# OpenClaw wt Apply Packet v1

**Label:** `approval-gated` — OpenClaw executes in `~/.openclaw/dawsos-workspace-wt`  
**Source of truth:** `~/CivForge/docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`

---

## 1. Mirror boundary contract

```bash
export CIVFORGE_ROOT="$HOME/CivForge"
export WT_ROOT="${DAWSCO_WORKSPACE_ROOT:-$HOME/.openclaw/dawsos-workspace-wt}"

mkdir -p "$WT_ROOT/engine-src/active/docs/planning"
cp "$CIVFORGE_ROOT/docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md" \
   "$WT_ROOT/engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md"
```

---

## 2. governed-connectors-registry row

OpenClaw verifies or adds `civforge_kernel` in:

`engine-src/active/config/governed-connectors-registry.v1.json`

Minimum fields (see full contract §5):

- `app_id`: `civforge-kernel`
- `plane`: `governance_kernel`
- `probe`: `http://127.0.0.1:8080/state`
- `nexus_satellite`: true

---

## 3. wt receipt refresh (minimum packet)

From wt root, after mirror:

```bash
cd "$WT_ROOT"
git rev-parse --short HEAD
git status --short
# Refresh builders per OpenClaw cron / manual:
# reports/ops/dawsos-projection-pipeline-receipt-latest.json
# reports/ops/workflow-dispatch-health-probe-latest.json
```

---

## 4. Optional handoff doc in wt

OpenClaw may add (separate commit family):

`engine-src/active/docs/planning/CIVFORGE_OPENCLAW_HANDOFF_V1.md`

Pointer-only summary linking to:

- `~/CivForge/docs/OPENCLAW_OPS_PACKET_V1.md`
- `~/CivForge/receipts/work-pack-openclaw-civforge-ops-001.md`

Cursor does **not** stage/commit wt unless Mike approves.

---

## 5. Rollback

```bash
git checkout -- engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md
# Revert registry row via governed PR
```
