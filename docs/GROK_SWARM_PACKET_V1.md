# Grok Swarm Packet v1

**Status:** `current` — planning lane on grok.com only  
**Execution:** Cursor on Mac Studio (`docs/EXECUTION_LANE_V2.md`)  
**Handoff seed:** `prompts/grok_swarm_handoff_seed.md`

---

## 1. You do NOT execute locally

Grok swarm runs on **grok.com**. No Mac Studio terminal, no `.grok/config.toml`, no local git.

**Require from Cursor before closing PRIME receipts:**
- `receipts/cursor-execution-*.md` with real `git HEAD` + test output
- Or: `bash tools/turnkey-cursor-local.sh` log pasted by Mike/Cursor

---

## 2. Default next lane (planning only)

| Priority | Work pack topic | Cursor implements |
|----------|-----------------|-------------------|
| 1 | **Mechanics proposal lane** (runtime + planning kinds) | `backend/mechanics_proposals.py` + MCP |
| 2 | Policy-tree tier effects | `backend/civstudy_mechanics_bridge.py` |
| 2 | Negotiation backlog sweep | `tools/negotiation-sweep.sh` |
| 3 | `:8081` JWT identity | `tools/dawsos_auth_client.py` + sim_api |
| 4 | Git worktrees | `docs/GIT_LANES_POLICY.md` |

**Forbidden:** UI rebuild, fake commits, local terminal claims.

---

## 3. Acceptance criteria (put in every WP)

```bash
bash tools/turnkey-cursor-local.sh
bash tools/validate-game.sh
git rev-parse --short HEAD   # Cursor provides
```

Never: `civforge_cli.py status | grep vercel`

---

## 4. MCP tools (agent-play — Cursor maintains)

16 tools in `tools/mcp_server.py` — see `docs/GAME_PLAY_GUIDE_V1.md`

**Mechanics proposal lane (not simulation):** `civforge_propose_mechanics`, `civforge_gate_mechanics`, `civforge_apply_mechanics`, `civforge_list_mechanics_proposals` — see `docs/GAME_MECHANICS_SWARM_PROPOSAL_LANE_V1.md`

---

## 5. PRIME receipt rules

1. Planning class only until Cursor execution receipt linked
2. No invented `fun_score` — cite live `/state`
3. Tag stale over-claims explicitly
4. OpenClaw/wt promotion = escalate, not swarm claim

---

## 6. grok.com tools (not impacted by lane v2)

Removed: CivForge-local `.grok/config.toml` (Mac terminal agent).  
Unchanged: global `~/.grok/config.toml` + grok.com project MCP settings.

| Tool class | grok.com | Cursor Mac |
|------------|----------|------------|
| dawsOS MCPs (gitnexus, memory, trivium) | keep connected | via Cursor MCP |
| CivForge `tools/mcp_server.py` (16 tools) | optional remote bridge | local stdio |
| Terminal / git on CivForge | planning only | executes |

See `prompts/grok_swarm_handoff_seed.md` § dawsOS MCP tools.

---

## 7. Work pack template

`docs/WORK_PACK_TEMPLATE_V1.md` — swarm-field aligned (`side_effect_class`, `required_receipt_links`)

`receipts/work-pack-grok-mechanics-sim-001.md` (example)

---

## 8. Canonical docs

- `docs/EXECUTION_LANE_V2.md`
- `docs/dawsos_nexus_reference.md` (all apps use dawsos-nexus pattern)
- `receipts/HANDOFF-GROK-SWARM-20260615.md`
- `docs/OPENCLAW_ESCALATION_PACKET_V1.md` (when wt needed)
