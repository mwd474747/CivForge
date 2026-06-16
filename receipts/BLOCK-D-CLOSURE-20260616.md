# Block D closure — `:8081` JWT identity on mutators

**Date:** 2026-06-16  
**Tag:** `current` after commit + push  
**Authority:** Cursor execution lane

---

## Scope

| Item | Landed |
|------|--------|
| JWT verify via auth-prototype `:8081` | `backend/auth_identity.py` |
| Mutator auth when `CIVFORGE_REQUIRE_AUTH=1` | Updated `require_public_mode_token` in `sim_api.py` |
| Protected advance prefers `:8081` JWT | Updated `require_govern_token` |
| Identity CLI | `tools/dawsos_auth_identity_client.py` |
| Kernel status route | `GET /game/auth/status` |
| civforge_cli auth | Delegates to identity client |

---

## Proof

```bash
python3 -m pytest tests/test_wp_grok_block_d_001.py -q
python3 -m pytest tests/ -q   # 147 total
```

---

## Non-goals

- Merging auth-prototype code into CivForge
- Replacing Nexus `:8082` machine satellite
- Production JWT secret rotation (operator concern)
