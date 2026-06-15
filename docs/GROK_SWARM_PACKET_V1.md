# Grok Swarm Packet v1

**Status:** `current` — alignment + verify + next-lane defaults  
**Locked truth plane:** receipts 020 → 021 → 024 → 025 + commit `cc80db3`+  
**Label:** execution claims require literal verify below

---

## 1. One-command turnkey

```bash
cd ~/CivForge
git pull origin main
bash tools/start-kernel-8080.sh
bash tools/turnkey-grok-play.sh --advances 5
```

Full gap closure:

```bash
bash tools/turnkey-gaps-all.sh
```

---

## 2. Default next lane (only these)

| Priority | Lane | Owner |
|----------|------|-------|
| 1 | CivStudy ↔ mechanics sim hooks | `backend/civstudy_mechanics_bridge.py` |
| 2 | MCP governance tools | `tools/mcp_server.py` |
| 3 | 8082 poller + telemetry | OpenClaw ops packet |
| 4 | Git lanes (mechanics/sim) | `docs/GIT_LANES_POLICY.md` |

**Forbidden default:** UI rebuild, “no dashboard” claims, fake commit hashes.

---

## 3. Literal verification (required)

```bash
bash tools/validate-game.sh
curl -sf http://127.0.0.1:8080/dashboard | grep -c "Multi-Agent Command"
python3 -m pytest tests/test_civstudy_mechanics_bridge.py -q
```

### Never use as sole proof

```bash
python3 tools/civforge_cli.py status | grep vercel   # always 0 matches — INVALID
```

### Honest UI/Vercel claims

- Local: `http://127.0.0.1:8080/dashboard`
- Static shell: `https://civforge.vercel.app` + `?api_base=` HTTPS tunnel to Mac `:8080`

---

## 4. MCP tools (agent-player)

| Tool | Endpoint |
|------|----------|
| `civforge_status` | `GET /state` |
| `civforge_advance_turn` | `POST /advance_turn` |
| `civforge_found_city` | `POST /found_city` |
| `civforge_negotiate` | `POST /game/negotiate` |
| `civforge_negotiate_respond` | `POST /game/negotiate/respond` |
| `civforge_what_if` | `POST /simulation/what_if` |
| `civforge_governance_propose` | `POST /governance/propose` |
| `civforge_governance_gate` | `POST /governance/gate` |

List: `echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 tools/mcp_server.py`

---

## 5. CivStudy simulation (landed)

`/state` exposes:

- `civstudy_reference` — read-only metadata (districts, policy_tree, forks, chains)
- `civstudy_sim` — live sim summary (district pulse, unlocked forks, chain progress)

Mechanics ticks: `civstudy_district`, `civstudy_discovery`, `civstudy_cultural` on each `advance_turn`.

---

## 6. Work pack

**`receipts/work-pack-grok-mechanics-sim-001.md`**

---

## 7. PRIME receipt rules

1. Cite `git rev-parse --short HEAD` — must exist on `main`
2. Cite probe output, not narrative
3. Tag over-claims as `stale` / `blocked`
4. No FunForge 100.0 without live `fun_score` from `/state`
