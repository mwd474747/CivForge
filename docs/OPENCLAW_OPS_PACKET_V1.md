# OpenClaw Ops Packet v1

**Status:** `current` — **escalation reference** (routine CivForge ops → Cursor)  
**Primary:** `docs/OPENCLAW_ESCALATION_PACKET_V1.md`  
**Lane model:** `~/CivForge/docs/EXECUTION_LANE_V2.md`

---

## 1. One-command turnkey

```bash
cd ~/CivForge
git pull origin main
bash tools/turnkey-full-stack.sh              # :8081 auth + :8080 kernel + validate + OpenClaw probe
bash tools/turnkey-full-stack.sh --auth-on    # also issue govern JWT (export CIVFORGE_AUTH_TOKEN)
bash tools/turnkey-governance-posture.sh      # OpenClaw CF-GOV-* posture (read-only)
bash tools/turnkey-openclaw-ops.sh            # probes + poller --once + receipt scaffold
bash tools/turnkey-openclaw-ops.sh --daemon   # start poller daemon (needs key + 8082)
bash tools/turnkey-gaps-all.sh --restart      # full stack: tests + cursor + openclaw
```

**Governance proposal closure:** `receipts/work-pack-openclaw-civforge-governance-001.md`

---

## 2. Ordered checklist (authority lane)

| Step | Action | Verify |
|------|--------|--------|
| 1 | dawsos-auth `:8081` | `curl -sf http://127.0.0.1:8081/health` |
| 2 | Kernel `:8080` | `curl -sf http://127.0.0.1:8080/state` |
| 3 | dawsos-nexus `:8082` | `curl -sf http://127.0.0.1:8082/api/health` |
| 4 | Satellite key | `~/.openclaw/runtime/nexus-satellite-api-keys.json` → `civforge-kernel` |
| 5 | Poller once | `NEXUS_API_KEY=… python3 tools/nexus_command_poller.py --once` |
| 6 | Poller daemon | `bash tools/start-poller-daemon.sh` |
| 7 | wt mirror | Apply `docs/OPENCLAW_WT_APPLY_PACKET_V1.md` |
| 8 | wt receipts | Refresh minimum packet (projection, dispatch, gap-prod-002 if touching wt) |
| 9 | Vercel | `vercel --prod` after `frontend/index.html` changes |

---

## 3. OpenClaw must NOT

- Treat CivForge `receipts/*.md` as dawsOS promotion truth
- Call `/advance_turn` or `/found_city` from Nexus without FunForge propose/gate path
- Mutate dawsos-nexus source tree from CivForge
- Rebuild dashboard from scratch (extensions only)

---

## 4. wt integration (thin bridge)

| Artifact | wt path |
|----------|---------|
| Boundary contract | `engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` |
| Connector row | `engine-src/active/config/ops/governed-connectors-registry.v1.json` → `civforge_kernel` |
| Nexus receipts | `reports/ops/nexus-*` (mirror builders) |

Copy commands: **`docs/OPENCLAW_WT_APPLY_PACKET_V1.md`**

---

## 5. Work pack

Full governed packet: **`receipts/work-pack-openclaw-civforge-ops-001.md`**

---

## 6. Receipt label

Every OpenClaw ops run should append or reference:

- `receipts/openclaw-ops-run-*.md` (auto from turnkey script)
- wt `reports/ops/*-latest.json` with `generated_at` cited in chat

**Tag:** `prototype-only` until wt freshest blocking receipt is green.
