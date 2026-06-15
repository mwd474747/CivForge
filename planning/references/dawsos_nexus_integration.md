# Reference: dawsos-nexus integration (CivForge)

**Source:** `~/Documents/GitHub/dawsos-nexus` — local Mac Studio Mission Control (`:8082`)  
**Legacy:** Upstream was `mwd474747/nexus_ctrl` (Replit). Runtime name is **dawsos-nexus** only.

## Role

Telemetry + command-intent sister for CivForge. Not identity, not CivForge execution truth.

| Nexus capability | CivForge mapping |
|------------------|------------------|
| Heartbeats + customMetrics | FunForge, turn, resources, multi-agent summary |
| Command queue | Poller → `/governance/propose` + gate |
| Fleet / audit mirrors | wt read-only builders |
| Dashboard patterns | Inspiration for CivForge dashboard (landed) |

## Same pattern as other satellites

`civforge-kernel`, `openclaw-cron-host`, `openclaw-cron-review`, `dawsos-api` — all register in wt registry + Nexus with push/pull telemetry per connector class.

## Identity (current canon)

- **Nexus:** machine/satellite API key only
- **CivForge product auth:** `dawsos-auth-prototype` `:8081` via `tools/dawsos_auth_client.py`
- Deferred: any plan to merge auth into Nexus (historical receipt only)

## Governed integration checklist

1. Row accurate in wt `governed-connectors-registry` → `civforge_kernel`
2. Satellite key at `~/.openclaw/runtime/nexus-satellite-api-keys.json`
3. Poller daemon: `tools/start-poller-daemon.sh`
4. Posture: `python3 tools/civforge_poller_posture.py`

See `docs/dawsos_nexus_reference.md`, `docs/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md`.
