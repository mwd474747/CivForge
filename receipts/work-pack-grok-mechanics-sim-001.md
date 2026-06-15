# Work Pack: Grok Mechanics + CivStudy Sim 001

**ID:** `WP-GROK-MECHANICS-SIM-001`
**Lane:** `lane/civ-game-mechanics` + `lane/simulation`
**Owner:** Grok swarm (grok.com planning) → **Cursor** (execution)
**Label:** `prototype-only` until `validate-game.sh` + swarm receipt
**Supersedes:** false WP-025 metadata-only claims — simulation hooks now in tree

---

## Objective

Wire CivStudy read-only metadata into live mechanics ticks; extend MCP + validation; produce honest PRIME receipt with literal probes.

---

## Landed in tree (Cursor scaffold)

| Component | Path |
|-----------|------|
| CivStudy sim bridge | `backend/civstudy_mechanics_bridge.py` |
| Registry hooks | `core/mechanics_registry.py` → `civstudy_*` ticks |
| `/state` field | `civstudy_sim` summary |
| MCP governance | `civforge_governance_propose`, `civforge_governance_gate` |
| Tests | `tests/test_civstudy_mechanics_bridge.py` |
| Turnkey | `tools/turnkey-grok-play.sh`, `tools/turnkey-gaps-all.sh` |

---

## Grok execution steps

```bash
cd ~/CivForge
git pull origin main
bash tools/start-kernel-8080.sh
bash tools/turnkey-grok-play.sh --advances 5
```

### Extend (governed — propose on 8080 first)

1. Add policy_tree unlock effects (tier gates on district pulse)
2. Negotiation backlog sweep via `civforge_negotiate_respond` MCP loop
3. `:8081` JWT for `protected_advance` (infra lane)
4. Git lane worktrees per `docs/GIT_LANES_POLICY.md`

---

## Verification (mandatory)

```bash
python3 -m pytest tests/test_civstudy_mechanics_bridge.py tests/test_civstudy_metadata.py -q
bash tools/validate-game.sh
git rev-parse --short HEAD
```

### Receipt must include

- HEAD hash (exists on `main`)
- `fun_score` from live `/state` (not invented)
- `civstudy_sim.unlocked_forks` after advances
- Explicit `stale` tag on any pre-turnkey claims

---

## Forbidden patterns

- `civforge_cli.py status | grep vercel`
- Fake commit IDs (e.g. `v3w7y9z`)
- “No UI” / “build dashboard” when `GET /dashboard` returns 426-line HTML

---

## Closure

New receipt: `receipts/swarm-mechanics-sim-001-closure-YYYYMMDD.md` referencing this work pack.

**RIME:** `prototype-only` → `current` after literal verify + HEAD match.
