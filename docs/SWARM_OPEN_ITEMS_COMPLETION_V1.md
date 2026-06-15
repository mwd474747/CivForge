# Swarm open items — completion status (2026-06-15)

## Implemented in this tree (`current`)

| Item | Artifact |
|------|----------|
| Multi-agent UI (tabs, map, negotiation, alliance, victory) | `frontend/index.html`, `backend/multi_agent_state.py` |
| Military / Economic / Cultural lanes | `core/mechanics_registry.py`, dashboard view tabs |
| MechanicsRegistry pluggable tick | wired in `advance_turn` |
| Found City session UI | `GET /game/founding-session`, dashboard Found City tab |
| CivStudy reference panel | `civstudy_reference` in `/state`, dashboard tab |
| MCP agent-play server | `tools/mcp_server.py`, `civforge_cli.py mcp-serve` |
| Docker compose + healthcheck | `docker-compose.yml`, `tools/docker-smoke.sh` |
| Poller daemon script | `tools/start-poller-daemon.sh` |
| Richer 8082 telemetry | `telemetry_extra_from_state()` in `sim_api.py` |
| Vercel static deploy | https://civforge.vercel.app |

## Quick validation

```bash
bash tools/start-kernel-8080.sh
open http://127.0.0.1:8080/dashboard
bash tools/turnkey-multi-ui-full.sh
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 tools/mcp_server.py
bash tools/start-poller-daemon.sh   # optional; needs runtime NEXUS_API_KEY
bash tools/docker-smoke.sh          # optional; uses port 8080
```

## Still out of scope (SEPARATION / lanes / operator)

- Live civstudy corpus integration (reference panel only)
- `:8081` JWT identity plane
- Git lane worktrees + draft PRs per `GIT_LANES_POLICY.md`
- Railway/Render/Fly hosting push (operator)
- wt planning pointer (OpenClaw packet)
- OpenClaw handoff v3 / release candidate artifacts
