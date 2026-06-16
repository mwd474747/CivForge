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

## MCP tools (12)

| Tool | Action |
|------|--------|
| `civforge_status` | `GET /state` |
| `civforge_advance_turn` | `POST /advance_turn` |
| `civforge_reset_game` | `POST /game/reset` |
| `civforge_found_city` | `POST /found_city` |
| `civforge_negotiate` | `POST /game/negotiate` |
| `civforge_negotiate_respond` | `POST /game/negotiate/respond` |
| `civforge_what_if` | `POST /simulation/what_if` |
| `civforge_governance_propose` | `POST /governance/propose` |
| `civforge_governance_gate` | `POST /governance/gate` |
| `civforge_select_district` | `POST /game/district/select` |
| `civforge_unlock_policy` | `POST /game/policy/unlock` |
| `civforge_claim_tile` | `POST /game/map/claim` |
| `civforge_send_envoy` | `POST /game/diplomacy/send_envoy` |

## Player actions

| Action | Endpoint | Cost |
|--------|----------|------|
| Select district | `POST /game/district/select` | 3 influence |
| Unlock policy | `POST /game/policy/unlock` | 5/8/12 by tier |
| Claim map tile | `POST /game/map/claim` | 4 influence (adjacent neutral/contested) |
| Catalog | `GET /game/actions` | — |

Dashboard **Player Actions** panel + clickable claimable map tiles (dashed outline).

## Session outcomes

- **Victory epilogue** — advance blocked; use Reset Game.
- **Defeat** — fun floor, diplomatic isolation, betrayal collapse, or stalled progress; `defeat-outcome-*.md` receipt.

## Victory

- **Joint progress** increments each governance turn (1–3) and on accepted negotiations (+8).
- CivStudy cultural chains and policy `festival_receipts` can add bonus progress.
- Milestones unlock at 25% (map), 60% (quorum), 100% (joint victory).
- At 100%, `outcome: "victory"` is set; dashboard shows overlay; a one-time `victory-outcome-*.md` receipt is written.
- Use **Reset Game** (dashboard) or `POST /game/reset` / MCP `civforge_reset_game` to start a fresh session.
- Governance cycle receipts include a `victory_progress` snapshot each turn.

## Mechanics extensions

Register tick modules per `docs/MECHANICS_TICK_CONTRACT_V1.md`. CivStudy bridge modules: district, discovery, cultural, **policy_tree**.

## Nexus integration (8082)

```bash
export NEXUS_API_KEY="$(python3 -c "import json;print(json.load(open('$HOME/.openclaw/runtime/nexus-satellite-api-keys.json'))['civforge-kernel']['apiKey'])")"
export NEXUS_URL=http://127.0.0.1:8082
python3 tools/nexus_command_poller.py --once
```

Optional daemon: `bash tools/start-poller-daemon.sh`

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

## Known limits (non-engine)

- `:8081` JWT identity plane not wired (Nexus satellite key / optional `CIVFORGE_REQUIRE_AUTH` only).
- Live civstudy corpus not integrated (reference panel only).
- Full PlayerAgent brain in orchestrator (lightweight player receipt line only).
