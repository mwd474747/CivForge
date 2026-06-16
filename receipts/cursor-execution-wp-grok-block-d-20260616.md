# Cursor execution — Block D (JWT identity)

**Generated:** 2026-06-16  
**Lane:** Cursor execution  
**WP:** WP-GROK-JWT-IDENTITY-001

---

## Commands

```bash
cd ~/CivForge
python3 -m pytest tests/test_wp_grok_block_d_001.py -q
python3 -m pytest tests/ -q
```

## Result

- **147 pytest** pass (9 Block D tests)
- Mutators accept static `CIVFORGE_API_KEY` or govern JWT when `CIVFORGE_REQUIRE_AUTH=1`

## Files

| Path | Role |
|------|------|
| `backend/auth_identity.py` | Verify JWT via `:8081/verify` |
| `backend/sim_api.py` | Auth wiring + `/game/auth/status` |
| `tools/dawsos_auth_identity_client.py` | Identity plane CLI |
| `tools/civforge_cli.py` | `auth` subcommand → identity client |
| `tests/test_wp_grok_block_d_001.py` | Block D proof |

## Rollback

Revert Block D paths; unset `CIVFORGE_REQUIRE_AUTH`.
