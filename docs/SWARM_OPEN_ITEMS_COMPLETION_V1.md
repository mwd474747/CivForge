# Swarm open items — completion status (2026-06-15)

## Implemented (`current`)

| Item | Artifact |
|------|----------|
| Multi-agent UI | `frontend/index.html`, `backend/multi_agent_state.py` |
| Military / Economic / Cultural lanes | `core/mechanics_registry.py`, dashboard view tabs |
| Found City session | `GET /game/founding-session`, Found City tab |
| CivStudy reference panel | `civstudy_reference` in `/state` |
| MCP agent-play (6 tools) | `tools/mcp_server.py`, `civforge_cli.py mcp-serve` |
| Docker compose + healthcheck | `docker-compose.yml`, `tools/docker-smoke.sh` |
| Poller daemon | `tools/start-poller-daemon.sh` |
| 8082 telemetry | `telemetry_extra_from_state()` in `sim_api.py` |
| Game validation suite | `tools/validate-game.sh`, `tests/test_multi_agent_state.py` |
| Play documentation | `docs/GAME_PLAY_GUIDE_V1.md` |

## Review fixes applied

| Gap | Fix |
|-----|-----|
| Docker DB not persisted | Volume `civforge-db:/app/gravity_backend.db` |
| Duplicate negotiation IDs | `next_negotiation_id()` with `-1`, `-2` suffix |
| Pending offers dropped from `/state` | `negotiations_for_api()` — all pending + resolved tail |
| Victory 100% but milestone open | `sync_victory_milestones()` on tick + restore |
| MCP missing respond | `civforge_negotiate_respond` tool |

## Quick validation

```bash
bash tools/validate-game.sh --restart
open http://127.0.0.1:8080/dashboard
```

## Still out of scope

- Live civstudy corpus integration
- `:8081` JWT identity plane
- Git lane worktrees + draft PRs
- Railway/Render/Fly hosting (operator)
- wt planning pointer (OpenClaw packet)
- Win/lose end-screen beyond milestone bar
