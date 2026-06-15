# Work Pack: OpenClaw CivForge Governance 001

**ID:** `WP-OPENCLAW-CIVFORGE-GOV-001`  
**Proposal IDs:** `CF-GOV-POSTURE-001` … `CF-EXPOSURE-GUARD-005`  
**Owner:** OpenClaw applied locally; Cursor committed + turnkey  
**Label:** `current` for CivForge kernel posture (not wt promotion)  
**Receipt:** `receipts/openclaw-civforge-governance-hardening-20260615-1450.md`

---

## Verdict

**Valid** — bounded CivForge-local governance hardening; respects boundary contract (no wt writes, no workflow dispatch, propose-only Nexus path).

---

## Proposal → implementation

| ID | OpenClaw recommendation | Status | Artifact |
|----|-------------------------|--------|----------|
| CF-GOV-POSTURE-001 | CivForge-native posture builder | **Done** | `tools/civforge_governance_posture.py` |
| CF-CONTRACT-PARITY-002 | Docs/routes/MCP/Nexus parity lint | **Done** | `tools/civforge_contract_parity.py` |
| CF-GOV-RECEIPTS-003 | Persistent proposal/gate + restore | **Done** | `backend/sim_api.py`, `core/governance.py` |
| CF-POLLER-POSTURE-004 | Poller daemon + launcher hardening | **Done** | `tools/civforge_poller_posture.py`, `start-poller-daemon.sh` |
| CF-EXPOSURE-GUARD-005 | Optional public-mode token guard | **Done** | `CIVFORGE_PUBLIC_MODE=1` in `sim_api.py` |

---

## Turnkey (Cursor)

```bash
cd ~/CivForge
git pull origin main
bash tools/turnkey-governance-posture.sh          # read-only (default)
bash tools/turnkey-governance-posture.sh --with-gameplay   # advances turns
```

Bundled in `tools/turnkey-gaps-all.sh` (posture before gameplay advances).

---

## Deferred (not in this packet)

| Item | Reason |
|------|--------|
| `sim_api.py` modular split | Contract-preserving extraction — separate WP |
| Simulation replay seeds | Needs design — separate WP |
| Auth `:8081` JWT full wire | Boundary backlog — `dawsos-auth-prototype` sister |

---

## Validation

- `tests/test_civforge_governance_tools.py` — 13 pass (incl. governance tools)
- Posture latest JSON artifacts — `pass`
- `validate-game.sh --read-only` — no turn advance for reviews

---

## Closure

**Done** @ CivForge `main` (governance hardening + swarm-class commits).  
OpenClaw wt duties remain escalation-only per `docs/OPENCLAW_ESCALATION_PACKET_V1.md`.
