# dawsos-auth-prototype Helper (CivForge side)

**Important**: The dawsos-auth-prototype and CivForge are two completely separate projects.

This directory provides the **bridge and enablement tooling** inside CivForge for the independent auth/identity prototype at:

https://github.com/mwd474747/dawsos-auth-prototype

CivForge can use the prototype for optional governance authentication (e.g. "govern" scoped tokens before calling protected actions such as `/governance/protected_advance`).

The actual auth server code, database, JWT logic, and tests live **only** in the separate prototype repository. CivForge contains:
- A thin HTTP client (`tools/dawsos_auth_client.py`)
- This helper (clone + start instructions + convenience)
- Demo wiring in `backend/sim_api.py` (the `require_govern_token` dependency)

**Never copy auth backend code into CivForge.** Use via HTTP only (port 8081 by convention).

## Purpose
- Make it trivial (and governed) to obtain a local clone of the auth prototype.
- Provide reliable "enable" steps so the auth function works with CivForge governance (token issuance → protected calls).
- Follow the same literal verification + receipt-first spirit used for gravity-mosaic deploys.
- Support handoff to other workspaces (see HANDOFF_CONTEXT.md).

## Canonical Locations
- Auth prototype source (separate): `/Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype`
- Git remote: `https://github.com/mwd474747/dawsos-auth-prototype.git`
- Runs on: `http://localhost:8081`
- CivForge client: `python tools/dawsos_auth_client.py ...`
- Protected CivForge endpoint: `POST /governance/protected_advance` (requires valid Bearer token with "govern" scope)

## Quick Start — Clone + Enable the Auth Function

From CivForge root:

```bash
cd /Users/michaeldawson/CivForge

# 1. Ensure you have a local clone (creates or updates at the canonical path)
./tools/auth-prototype/clone.sh

# 2. Start the auth prototype (separate process)
./tools/auth-prototype/start.sh
```

In another terminal (or background):

```bash
# Test it is alive
curl http://localhost:8081/health

# Use the CivForge thin client to exercise the auth function
python tools/dawsos_auth_client.py register-device my-mac pk-123
python tools/dawsos_auth_client.py token <identity-id-from-above> govern
# Then use the returned token with CivForge
```

Example protected call (after obtaining a "govern" token):

```bash
TOKEN=eyJ...your.token.here...
curl -H "Authorization: Bearer $TOKEN" -X POST http://localhost:8080/governance/protected_advance
```

Without a valid token the endpoint returns 401/403 (as designed).

## What "Enable This Function" Means
Once the separate prototype is running on 8081 and you can successfully obtain tokens via the client:
- CivForge's optional auth-gated governance becomes usable.
- You can protect sensitive actions (advances, deploys, proposals) behind identity + scope checks.
- The pattern is borrowable for other dawsOS components (device identity, agent capabilities, receipt-backed tokens).
- All auth actions in the prototype produce their own receipt-style logs.

The integration in CivForge is deliberately minimal (HTTP only) to preserve strict separation.

## Script Details

### clone.sh
- Checks whether the canonical directory exists.
- If missing: performs `git clone` of the public repo.
- If present: does a `git pull` (or status) + literal verification (ls, wc, key string greps).
- Prints exact next steps.
- Does **not** mutate anything inside the auth prototype beyond a pull.

### start.sh
- Changes to the canonical auth prototype directory.
- Ensures Python deps are present (fastapi, uvicorn, pyjwt, pydantic).
- Launches (or prints the exact command for) `uvicorn backend.auth_api:app --port 8081`.
- References the prototype's own `run_prototype.sh` when possible.

You can also run the prototype directly:

```bash
cd /Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype
./run_prototype.sh
# or
python3 -m uvicorn backend.auth_api:app --reload --host 0.0.0.0 --port 8081
```

## Literal Verification Expectations (user process rules)
Before running clone.sh or start.sh, or before any change that affects the bridge:
- Run `git status`, `ls`, `wc -l` on key files in both CivForge and the auth prototype dir.
- Grep for separation language and golden features.
- Confirm no source leakage between the two projects.

The scripts themselves perform basic checks and echo the commands they will run.

## Updating the Prototype
- Changes to auth logic happen in the separate `/Users/michaeldawson/Documents/GitHub/dawsos-auth-prototype` repo.
- After changes there: commit + push following the same literal full-content rules used for gravity-mosaic.
- Then, from CivForge, you can re-run `./tools/auth-prototype/clone.sh` (it will pull) or manually pull in the prototype dir.
- Log a governance receipt in CivForge for the update (use `python tools/civforge_cli.py propose-deploy` + advance, or just append a receipt).

## CLI Integration
The main `python tools/civforge_cli.py` supports basic auth flows via the thin client.

You can also call the client directly for register / token / verify.

See `tools/dawsos_auth_client.py --help` style usage or run it with subcommands.

## For Handoff / Other Workspaces
See the main [HANDOFF_CONTEXT.md](../../HANDOFF_CONTEXT.md) (section on "Cloning and Enabling the dawsos-auth-prototype").

Adjust the canonical path variables if your machine layout differs. The scripts contain the Mac Studio defaults but are documented for portability.

## Related Files (CivForge)
- `tools/dawsos_auth_client.py` — thin client (register-device, token, verify)
- `backend/sim_api.py` — contains the `require_govern_token` dependency and `/governance/protected_advance` demo (bottom of file)
- `receipts/` — any auth-prototype related governance receipts
- `docs/patterns/borrowable-governance-patterns.md` — generalized separation + auth interop notes

## Production / Hardening Notes
- The current JWT secret is a prototype placeholder (`prototype-secret-change-in-prod`).
- No persistent cross-machine identity yet (uses local SQLite + optional `~/.openclaw/identity` seed).
- For real use: move the auth prototype behind proper secrets, rate limiting, and possibly its own governance (CivForge can propose work on it via the bridge pattern).

This helper keeps CivForge as the governance layer while the auth prototype remains an independent, cloneable, testable service.

Run the clone + start scripts, obtain a token, and the auth function for CivForge governance is enabled.