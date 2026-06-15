# CivForge game play guide v1

**Status:** `current` — matches commit `227da70`+ patches (multi-agent layer, mechanics lanes, MCP).

## Start the game

```bash
cd ~/CivForge
bash tools/start-kernel-8080.sh
open http://127.0.0.1:8080/dashboard
```

Kernel persists state in `gravity_backend.db` (SQLite) and `receipts/`.

## Dashboard

| View | What you do |
|------|-------------|
| **Overview** | Agent tabs, 5×5 map, send/accept negotiations, alliance tracker, victory bar |
| **Military / Economic / Cultural** | Lane stats tick each `advance_turn` |
| **Found City** | Start a governed work pack (`POST /found_city`) |
| **CivStudy Ref** | Read-only pattern hints (no live corpus) |

**Remote (Vercel):** https://civforge.vercel.app — use setup panel or `?api_base=https://<tunnel>` to reach your Mac Studio kernel over HTTPS.

## CLI

```bash
python3 tools/civforge_cli.py status
python3 tools/civforge_cli.py advance
python3 tools/civforge_cli.py mcp-serve   # stdio MCP for agent players
```

## MCP tools (8)

| Tool | Action |
|------|--------|
| `civforge_status` | `GET /state` |
| `civforge_advance_turn` | `POST /advance_turn` |
| `civforge_found_city` | `POST /found_city` |
| `civforge_negotiate` | `POST /game/negotiate` |
| `civforge_negotiate_respond` | `POST /game/negotiate/respond` |
| `civforge_what_if` | `POST /simulation/what_if` |
| `civforge_governance_propose` | `POST /governance/propose` |
| `civforge_governance_gate` | `POST /governance/gate` |

## Victory

- **Joint progress** increments each governance turn (1–3) and on accepted negotiations (+8).
- Milestones unlock at 25% (map), 60% (quorum), 100% (joint victory).
- At 100%, all four milestones including **Joint victory** are marked done.

## Nexus integration (8082)

```bash
export NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$HOME/.openclaw/runtime/nexus-satellite-api-keys.json'))['civforge-kernel']['apiKey'])")"
export NEXUS_URL=http://127.0.0.1:8082
python3 tools/nexus_command_poller.py --once
```

Optional daemon: `bash tools/start-poller-daemon.sh`

Governance posture:

```bash
python3 tools/civforge_contract_parity.py
python3 tools/civforge_poller_posture.py
python3 tools/civforge_receipt_index.py
python3 tools/civforge_governance_posture.py
```

## Validation

```bash
bash tools/validate-game.sh --restart   # full pass: pytest + API + turnkey
bash tools/docker-smoke.sh              # needs Docker; stops host :8080 first
```

## Docker

```bash
docker compose up -d civforge-kernel
```

SQLite volume: `civforge-db` → `/app/gravity_backend.db` (matches kernel `DB_PATH`).

## Known limits

- No win/lose screen beyond milestone bar (extensions via governed work packs).
- `:8081` JWT identity plane not wired.
- Live civstudy corpus not integrated (reference panel only).
