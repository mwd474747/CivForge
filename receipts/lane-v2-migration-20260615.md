# Lane v2 migration receipt

**Date:** 2026-06-15  
**Action:** execution_lane_v2_alignment  
**Status:** SUCCESS  
**Label:** `current` for CivForge governance docs

## Summary

Aligned CivForge to three-lane model per Mike directive:

| Lane | Runtime | Role |
|------|---------|------|
| Grok swarm | grok.com | Planning / WP / PRIME criteria |
| Cursor | Cursor IDE | All Mac Studio local execution |
| OpenClaw | wt | Escalation only |

## Removed (local Grok terminal footprint)

- `CivForge/.grok/config.toml` — deleted
- `bridge/grok_macstudio_bridge.py` — replaced by `bridge/civforge_http_bridge.py`
- `prompts/other_grok_context_update.md` — replaced by `prompts/grok_swarm_handoff_seed.md`
- `skills/grok_intelligence_skill.py` — replaced by `skills/civforge_execution_skill.py`
- AGENTS.md local Grok terminal / ForgeMaster executor sections — rewritten

## Added

- `docs/EXECUTION_LANE_V2.md`
- `docs/OPENCLAW_ESCALATION_PACKET_V1.md`
- `tools/turnkey-cursor-local.sh`
- `prompts/grok_swarm_handoff_seed.md`
- `agents/role_registry.json` v2.0

## OpenClaw WP-001

Closed. Routine CivForge ops → Cursor. Escalate via `OPENCLAW_ESCALATION_PACKET_V1.md`.

## Grok swarm next

Copy `prompts/grok_swarm_handoff_seed.md` into grok.com project. Do not install local Grok terminal on Mac Studio for CivForge.
