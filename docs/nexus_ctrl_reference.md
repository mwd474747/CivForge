# Nexus Ctrl (dawsos-nexus) Reference for CivForge (boundary-aligned)

Per updated plan (Claw minimum + hard walls):
- Nexus 8082 = observability (push telemetry: customMetrics including funforge_score/proposal_count, agentState) + command queue.
- CivForge registers as governance_kernel (nexus_satellite) — see wt governed-connectors-registry.v1.json (type, allowed_actions=["sync_config"], probe=http://127.0.0.1:8080/state, telemetry=push).
- Commands: proposals only (local /governance/propose + FunForge gate). No direct execution, no state side-effects on ingest.
- Identity separate: dawsos-auth-prototype 8081 (jwt plane). Nexus machine auth only (x-nexus-api-key / operator for heartbeats/poll).
- No wt execution spine (no workflow_dispatch, no reports/ops receipts). No control proxy metricsUrl (poller ingress only).
- Soft bridge: telemetry fire-and-forget; read-only fleet mirrors in wt.

Register with satellite key (not operator) when provisioning from Claw side. Poller (tools/nexus_command_poller.py) is the consumption path.

See SEPARATION.md (planes section), AGENTS.md, and the alignment receipt in civ-game-backend-nexus-impl-continuation-20260614.md.
