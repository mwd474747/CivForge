# Synthesis: lane v2 + dawsos-nexus + OpenClaw CivForge governance

**Date:** 2026-06-15  
**Label:** `current` for active posture; historical receipts unchanged

---

## 1. Why "nexus control" / `nexus_ctrl` appeared

| Term | Meaning | Status |
|------|---------|--------|
| **nexus_ctrl** | Old private repo / Replit "Nexus Mission Control" product name | **Legacy label only** |
| **dawsos-nexus** | Mac Studio implementation on `:8082` | **Canonical runtime** |
| **Nexus control proxy** | Pull-control via `metricsUrl` hitting app HTTP | **Blocked** (CF-AP-05) |
| **Command queue** | Nexus → poller → local propose | **Allowed** (thin bridge) |

June 2026 swarm receipts reviewed `nexus_ctrl` source to plan local deploy. That work **completed** as dawsos-nexus. Active docs now use `docs/dawsos_nexus_reference.md` only.

**All apps** (CivForge, OpenClaw cron satellites, dawsos-api) share the same dawsos-nexus satellite pattern: register in wt + Nexus, telemetry push/pull per connector class, commands → propose path.

---

## 2. Three-plane stack (synthesized)

```
grok.com (swarm)     →  work packs, PRIME criteria, dawsOS MCPs for planning
Cursor (Mac Studio)  →  CivForge :8080 code, tests, git, vercel, poller
dawsos-nexus :8082   →  fleet telemetry + command intents (all satellites)
dawsOS wt            →  registry, probes, mirrors — OpenClaw on escalation
auth-prototype :8081 →  JWT identity (separate from Nexus machine key)
```

CivForge is **not** a wt execution satellite. wt recognizes `civforge_kernel` for policy + liveness only.

---

## 3. Lane v2 impact on grok.com tools

| Asset | Lane v2 change | grok.com impact |
|-------|----------------|-----------------|
| `CivForge/.grok/config.toml` | **Deleted** | **None** — was local terminal only |
| `~/.grok/config.toml` (global) | Untouched | **MCP unchanged** |
| `tools/mcp_server.py` | Unchanged (8 tools) | grok.com uses via tunnel only if you configure; default = Cursor |
| dawsOS MCP (gitnexus, memory, trivium) | Still documented in handoff seed | **Keep in grok.com project** |
| `search_tool` / `use_tool` | Removed from AGENTS (local grok) | **Still valid on grok.com** — add to swarm project rules |

---

## 4. OpenClaw CivForge governance extension (2026-06-15)

Receipt: `receipts/openclaw-civforge-governance-hardening-20260615-1450.md`

| Layer | What OpenClaw added |
|-------|---------------------|
| **Kernel** | Persistent proposal/gate in SQLite; receipt-backed events |
| **Security** | Optional `CIVFORGE_PUBLIC_MODE=1` token guard on mutating routes |
| **Bridge** | POST `/integrate/civforge` (HTTP bridge contract fix) |
| **Posture tools** | `civforge_governance_posture.py`, `civforge_poller_posture.py`, `civforge_receipt_index.py`, `civforge_contract_parity.py` |
| **Runtime** | Kernel + poller in detached `screen` sessions |
| **Validation** | 13 pytest pass; contract parity `pass`; poller posture `pass` |

**wt:** Read-only — no `reports/ops` writes from CivForge posture builders (correct separation).

**Uncommitted:** OpenClaw left source in working tree per lane v2 (Cursor commits CivForge). **Next:** Cursor lands governance-hardening packet as one commit family.

---

## 5. OpenClaw wt duties (already done + ongoing)

| Done (WP-001) | Ongoing (escalation) |
|---------------|----------------------|
| wt probes pass @ 17:49:12Z | Projection / C2 when promoted |
| `civforge_kernel` registry row | Boundary menu apply |
| Nexus heartbeat screen loops | Scheduled fleet mirror builders |
| Integration 7/7 incl. `:8080/state` | GAP-PROD-002 wt closure |

Routine CivForge ops → **Cursor**. wt truth → **OpenClaw when escalated**.

---

## 6. Single roadmap (merged)

| Priority | Executor | Item |
|----------|----------|------|
| 1 | Cursor | Land OpenClaw governance-hardening uncommitted diff |
| 2 | Cursor | Policy-tree mechanics, negotiation sweep |
| 3 | Grok swarm | Work packs only — link Cursor receipts |
| 4 | OpenClaw | wt promotion when Mike approves |
| Deferred | — | Nexus-absorbs-auth (historical; keep `:8081`) |

---

## 7. Canonical doc index

| Doc | Purpose |
|-----|---------|
| `docs/EXECUTION_LANE_V2.md` | Grok / Cursor / OpenClaw split |
| `docs/dawsos_nexus_reference.md` | Nexus pattern (not nexus_ctrl) |
| `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` | Cross-plane contract |
| `docs/OPENCLAW_ESCALATION_PACKET_V1.md` | When to ping OpenClaw |
| `prompts/grok_swarm_handoff_seed.md` | grok.com paste + MCP note |
