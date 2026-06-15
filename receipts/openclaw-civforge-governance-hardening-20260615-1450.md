# OpenClaw CivForge Governance Hardening - 2026-06-15 14:50 EDT

## Scope

- Applied CivForge-local dawsOS-style governance hardening after Mike's explicit approval.
- Kept dawsOS wt as read-only and did not write `reports/ops`.
- No Vercel deploy, external messaging, push, PR, or C2/main movement.

## Source Changes

- Added persistent proposal/gate restoration and receipt-backed proposal/gate events in `backend/sim_api.py` and `core/governance.py`.
- Added optional `CIVFORGE_PUBLIC_MODE=1` token guard for mutating routes while preserving permissive local default.
- Added POST support for `/integrate/civforge` so HTTP bridge work-pack intake matches the route contract.
- Added local posture builders:
  - `tools/civforge_governance_posture.py`
  - `tools/civforge_poller_posture.py`
  - `tools/civforge_receipt_index.py`
- Extended existing contract parity lint and docs/tool validation.
- Hardened `tools/start-kernel-8080.sh` and `tools/start-poller-daemon.sh` with detached `screen` persistence where available.
- Updated CLI/MCP poller token handling without printing keys.

## Validation

- `python3 -m py_compile backend/sim_api.py core/governance.py core/receipts.py tools/civforge_contract_parity.py tools/civforge_governance_posture.py tools/civforge_poller_posture.py tools/civforge_receipt_index.py tools/nexus_command_poller.py tools/mcp_server.py tools/civforge_cli.py`
- `python3 -m pytest tests/test_multi_agent_state.py tests/test_civstudy_metadata.py tests/test_civstudy_mechanics_bridge.py tests/test_civforge_governance_tools.py -q` -> `13 passed`
- `bash tools/validate-game.sh` -> passed; advanced live kernel to turn `74`
- `git diff --check` -> passed
- Live proposal/gate persistence probe created proposal `3591c2c9`; SQLite persisted proposal and gate rows, and snapshot retained the proposal/work-pack status.

## Current Posture Artifacts

- `receipts/civforge-governance-posture-latest.json`: `pass`
- `receipts/civforge-contract-parity-latest.json`: `pass`
- `receipts/civforge-poller-posture-latest.json`: `pass`
- `receipts/civforge-receipt-index-latest.json`: `pass`

## Runtime

- CivForge kernel is running in detached screen session `civforge-kernel-8080`, PID file `/tmp/civforge-8080.pid`.
- CivForge poller remains running in detached screen session `civforge-poller`, PID file `/tmp/civforge-poller.pid`.
- Nexus `:8082` health passed during posture generation.

## Git

- HEAD moved during execution to `c6821cf` from the Cursor lane.
- Source changes are left uncommitted in the working tree because current lane docs assign CivForge commits/pushes to Cursor and OpenClaw is escalation-only for this repo.
