# Work Pack: OpenClaw CivForge Ops 001

**ID:** `WP-OPENCLAW-CIVFORGE-OPS-001`  
**Lane:** `lane/infra-required` + wt bridge  
**Owner:** OpenClaw / Mike (authority)  
**Label:** `approval-gated`  
**CivForge HEAD at authoring:** post `cc80db3` turnkey gap closure

---

## Objective

Sustained Nexus `:8082` + poller + wt mirror + receipt refresh on this Mac Studio — without conflating CivForge execution truth with dawsOS promotion.

---

## Prerequisites

- `~/CivForge` on `main` with turnkey scripts landed
- Mac Studio network local to `:8080` / `:8082`

---

## Steps

### A. CivForge kernel (verify only if Cursor already started)

```bash
cd ~/CivForge
bash tools/start-kernel-8080.sh
curl -sf http://127.0.0.1:8080/state | python3 -m json.tool | head -20
```

### B. dawsos-nexus

1. Start `dawsos-nexus` on `127.0.0.1:8082` (LaunchAgent or project start script).
2. `curl -sf http://127.0.0.1:8082/api/health`
3. Register `civforge-kernel` if missing; ensure key at `~/.openclaw/runtime/nexus-satellite-api-keys.json`.

### C. Poller

```bash
cd ~/CivForge
bash tools/turnkey-openclaw-ops.sh --once
bash tools/start-poller-daemon.sh   # sustained
```

### D. wt mirror

Execute **`docs/OPENCLAW_WT_APPLY_PACKET_V1.md`** in wt.

### E. wt receipts

Refresh minimum partner-lane packet; cite `generated_at` in operator chat.

### F. Vercel (if UI changed)

```bash
cd ~/CivForge && vercel --prod
```

---

## Verification

| Check | Command |
|-------|---------|
| Kernel | `bash tools/validate-game.sh` |
| OpenClaw ops | `bash tools/turnkey-openclaw-ops.sh` |
| wt mirror | `test -f wt/engine-src/active/docs/planning/CIVFORGE_DAWSOS_BOUNDARY_CONTRACT_V1.md` |

---

## Forbidden

- Direct `/advance_turn` from Nexus poll without propose path
- CivForge receipt → dawsOS promotion claim
- LaunchAgent edits from Cursor without explicit approval

---

## Closure

Append wt receipt paths + `receipts/openclaw-ops-run-*.md` with `status: SUCCESS` and probe literals.

**RIME:** `prototype-only` until wt blocking receipts green.
