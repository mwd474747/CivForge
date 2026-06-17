# Cursor execution — WP-TOOLING-AWARENESS-PROPOSAL-001 (full closure)

**Generated:** 2026-06-17  
**Tag:** `current`

## Delivered (4/4 proposal items)

| Item | Path |
|------|------|
| Structured state MCP | `civforge_state_summary` in `tools/mcp_server.py`, `tools/mcp_state_summary.py` |
| Receipt snapshot CLI | `python3 tools/civforge_cli.py snapshot` → `GET /game/awareness/summary` |
| Mechanics status | `GET /game/mechanics/status` (existing) |
| Awareness dashboard | `frontend/index.html?grok_view=true` |

## Core module

- `backend/awareness_summary.py`
- `GET /game/awareness/summary` in `backend/sim_api.py`

## Tests

`tests/test_wp_tooling_awareness_proposal_001.py`

## Verify

```bash
python3 -m pytest tests/test_wp_tooling_awareness_proposal_001.py -q
curl -s http://127.0.0.1:8080/game/awareness/summary | python3 -m json.tool | head
python3 tools/civforge_cli.py snapshot | head
open 'http://127.0.0.1:8080/dashboard?grok_view=true'
```
