# CivForge completion checklist v1

**Status:** `current` — swarm multi-agent layer landed (`227da70`+); review patches applied 2026-06-15
**Boundary:** `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`
**Play guide:** `docs/GAME_PLAY_GUIDE_V1.md`

---

## Done (verified live)

| Item | Evidence |
|------|----------|
| Kernel `:8080` live | `bash tools/start-kernel-8080.sh` → `GET /state` |
| Multi-agent `/state` | 25 `map_tiles`, `alliances`, `negotiations`, `victory_progress`, `mechanics_lanes` |
| Local dashboard | http://127.0.0.1:8080/dashboard — Multi-Agent Command + view tabs |
| Nexus `:8082` health | `GET /api/health` → ok |
| `civforge-kernel` satellite | registered; telemetry on advance/found |
| MCP agent-play | `tools/mcp_server.py` — 6 tools incl. `civforge_negotiate_respond` |
| Docker compose | `docker-compose.yml`; DB volume → `/app/gravity_backend.db` |
| Unit tests | `tests/test_multi_agent_state.py` |
| Full validation | `bash tools/validate-game.sh --restart` |
| Vercel static shell | https://civforge.vercel.app (`?api_base=` for live kernel) |

---

## Review fixes (2026-06-15)

- [x] Docker SQLite volume aligned to `gravity_backend.db`
- [x] Negotiation IDs sequenced (`neg-player-harper-48-1`, `-2`, …)
- [x] `/state` returns all pending negotiations + resolved tail
- [x] Joint victory milestone syncs when progress ≥ target
- [x] MCP `civforge_negotiate_respond` tool

---

## Multi-Agent UI (WP-UI-MULTI-AGENT-EXTENSION)

| Layer | Path |
|-------|------|
| State engine | `backend/multi_agent_state.py` |
| Mechanics | `core/mechanics_registry.py` |
| API | `backend/sim_api.py` |
| Dashboard | `frontend/index.html` |
| Turnkey | `tools/turnkey-multi-ui-full.sh` |

---

## Quick validation

```bash
bash tools/validate-game.sh --restart
open http://127.0.0.1:8080/dashboard
```

Poller (optional):

```bash
export NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$HOME/.openclaw/runtime/nexus-satellite-api-keys.json'))['civforge-kernel']['apiKey'])")"
export NEXUS_URL=http://127.0.0.1:8082
python3 tools/nexus_command_poller.py --once
```

---

## Out of scope / later

- Auth-prototype `:8081` for product identity
- Live civstudy corpus (reference panel only today)
- wt `CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` pointer (OpenClaw packet)
- Railway/Render/Fly hosting push (operator)
- Git lane worktrees + draft PRs per `GIT_LANES_POLICY.md`
