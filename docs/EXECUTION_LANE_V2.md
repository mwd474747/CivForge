# Execution Lane v2 — Grok Swarm · Cursor · OpenClaw

**Status:** `current` — canonical lane model (2026-06-15)  
**Supersedes:** three-way overlap (local Grok terminal + Cursor + OpenClaw on CivForge ops)

---

## 1. Lane map

| Lane | Where it runs | Role | Executes on Mac Studio? |
|------|---------------|------|---------------------------|
| **Grok swarm** | [grok.com](https://grok.com) project / swarm UI | Planning, work packs, PRIME receipts (criteria only), roadmap | **No** |
| **Cursor** | Cursor IDE on Mac Studio | All local CivForge code, kernel, tests, vercel, poller, git push | **Yes** |
| **OpenClaw** | OpenClaw runtime / wt | dawsOS promotion truth, boundary menus, storage apply, C2 — **on escalation only** | When triggered |

**Removed:** Local Grok terminal instance (`.grok/config.toml`, ForgeMaster local executor). No Mac Studio Grok CLI agent.

---

## 2. Grok swarm (planning only)

**Does:**
- Author `WP-*` work packs with acceptance criteria
- Prioritize roadmap lanes (`docs/GIT_LANES_POLICY.md`)
- Issue PRIME receipts as **planning class** (not execution proof)
- Deliberate multi-agent game design (Harper/Sebastian in-game roles — not terminal agents)

**Does not:**
- Run terminal on Mac Studio
- Commit to CivForge or wt
- Claim `git HEAD` without linked Cursor execution receipt
- Use `civforge_cli.py status | grep vercel` as verify

**Bootstrap:** `prompts/grok_swarm_handoff_seed.md` + `receipts/HANDOFF-GROK-SWARM-20260615.md`

---

## 3. Cursor (local executor)

**Does:**
- Implement all CivForge source changes
- `bash tools/start-kernel-8080.sh`, `validate-game.sh`, `turnkey-cursor-local.sh`
- Poller daemon, Vercel `--prod` (when Mike approves in chat)
- CivForge `git commit` / `push` to `main`
- Write **execution receipts** with literal probes + `git rev-parse --short HEAD`

**Does not:**
- wt commit / push / C2 / main movement (unless Mike gives exact approval text)
- Storage cleanup apply, LaunchAgent mutation, Trivium mutation
- Claim dawsOS promotion truth (`reports/ops/*`)

**Verify packet:** `bash tools/turnkey-cursor-local.sh`  
**Governance posture (read-only):** `bash tools/turnkey-governance-posture.sh`

---

## 4. OpenClaw (escalation only)

**Trigger when:**
1. wt `reports/ops/*` must refresh for promotion / C2 claims
2. Boundary menu has `ready_decision_ids` needing apply
3. DawsOS API `:8000` or workflow dispatch blocked
4. Storage / protected apply / cron sustainment (scheduled)
5. Cursor escalation packet tagged `blocked` with wt receipt

**Does not run for:** CivForge feature work, kernel restarts, vercel, pytest, handoff docs.

**Packet:** `docs/OPENCLAW_ESCALATION_PACKET_V1.md`

---

## 5. Truth plane (anti-drift)

Read **`docs/TRUTH_ORDER.md`** before any status claim. Machine index: **`config/work_pack_registry.yaml`**. Live summary: `GET /state` → `work_pack_registry`.

## 6. Receipt chain

```
Grok WP (criteria) → Cursor executes → Cursor execution receipt (HEAD + tests)
                  → Grok PRIME closes against Cursor receipt (optional)
                  → OpenClaw only if wt escalation needed
```

| Receipt class | Author | Authority |
|---------------|--------|-----------|
| Work pack `WP-*` | Grok swarm | Planning |
| `cursor-execution-*.md` | Cursor | CivForge execution proof |
| `governance-cycle-*.md` | `:8080` kernel | Game loop (auto) |
| `reports/ops/*` | OpenClaw builders | dawsOS promotion truth |

---

## 7. Approvals

| Action | Approver | Executor |
|--------|----------|----------|
| CivForge code / test / commit | Mike in chat | Cursor |
| Kernel / poller / vercel | Mike in chat | Cursor |
| FunForge gate ritual | Optional `:8080` | Cursor via CLI |
| wt promotion / C2 / storage | Boundary menu + exact text | OpenClaw |

---

## 8. Local control surfaces (Cursor)

| Tool | Purpose |
|------|---------|
| `tools/civforge_cli.py` | CLI driver |
| `bridge/civforge_http_bridge.py` | Python HTTP to `:8080` |
| `tools/mcp_server.py` | MCP for agent-play lane |
| `bash tools/turnkey-cursor-local.sh` | Full local verify |

---

## 9. Swarm class (CivForge ≠ dawsOS registry swarms)

CivForge is **dawsOS-shaped** (proposal-first, receipt-first, bounded bridges) but **not** a `swarm-registry.v0.json` workflow swarm.

Three layers — do not conflate:

1. **Grok swarm** (grok.com) — planning / work packs only
2. **AgentBrain personas** (`forge-coordinator`, `harper`, `sebastian`) — in-kernel simulation/governance
3. **dawsos-nexus bridge** — telemetry + propose-only command intake

Full comparison: `docs/CIVFORGE_SWARM_CLASS_V1.md`

---

## 10. Migration note

Historical receipts referencing local Grok terminal, `.grok/config.toml`, or `nexus_ctrl` naming are **archived context**. Active execution uses this document. Nexus canon: `docs/dawsos_nexus_reference.md`.
