# HANDOFF CONTEXT PACKAGE — CivForge (historical + lane v2 pointer)

> **Lane model (2026-06-15):** See `docs/EXECUTION_LANE_V2.md`. Grok swarm runs on **grok.com only** (no local terminal). **Cursor** executes all Mac Studio work. **OpenClaw** escalates for wt promotion only. Current handoff: `receipts/HANDOFF-GROK-SWARM-20260615.md`.

**Created**: 2026-06-13 (Mac Studio canonical state)  
**Purpose**: Self-contained snapshot so a Grok running in another workspace (or fresh session) can immediately resume exactly where this work left off, without re-deriving history, mechanics, or boundaries.  
**Source of truth for this package**: Local disk reads in the CivForge workspace + the separate projects. Always re-verify with literal `read_file`, `cat`, `wc -l`, `grep`, `git status` before acting.

**User's explicit last request that produced this package**: "give me a handoff context package for grok in another workspace to help finish this work" (after mechanics/rules discussion and "why are the previous tasks hung").

---

## 1. Canonical Workspace Locations (exact, do not guess)

- **CivForge** (the current governed workspace you are likely in or targeting):  
  `/Users/michaeldawson/CivForge`  
  Git: https://github.com/mwd474747/CivForge (branch: `main`, HEAD at time of handoff: `b2fd116` "test+extend: auth prototype...")

- **gravity-mosaic-knowledge-graph** (the *completely separate* project being governed):  
  `/Users/michaeldawson/gravity-mosaic-knowledge-graph`  
  Git: https://github.com/mwd474747/gravity-mosaic-knowledge-graph (independent remote + history).  
  Contents: `index.html`, `models/biefeld_brown_thrust.py` (with `EQUATIONS`), `models/precision_porting.py`, README/ROADMAP. Pristine, no CivForge source inside.  
  **NEVER edit or git from here except via the strict bridge below. Local disk = single source of truth for pushes.**

  Key files: `backend/auth_api.py` (FastAPI :8081, real PyJWT, SQLite identities/tokens, receipt-style logging, auto-seed from `~/.openclaw/identity`), `core/identity_patterns.py` (IdentityReceiptStore, AgentAuthBrain, AuthQualityScorer — FunForge-inspired), `tools/auth_cli.py`, `tests/test_auth_flows.py` (4/4 passing), `docs/INTEROPERABILITY.md`, `AGENTS.md`, `run_prototype.sh`.  
  Thin CivForge client only: `CivForge/tools/dawsos_auth_client.py` (HTTP calls only; no code merge).  
  **Clone + enable bridge in CivForge**: `tools/auth-prototype/{clone.sh, start.sh, README.md}` (see "Cloning and Enabling..." section below).

- **Related dawsOS roots** (for context/interop seeds, patterns):  
  `~/.openclaw/dawsos-workspace-wt` (main dawsOS workspace)  
  `~/Documents/GitHub/dawsos-grok`

**Rule**: These are three (or more) distinct projects. CivForge governs; the others are independent targets. Cross-contamination is forbidden.

---

## 2. Strict Separation Contracts (enforce verbatim)

See full [SEPARATION.md](/Users/michaeldawson/CivForge/SEPARATION.md) and [docs/REPO_HYGIENE.md](/Users/michaeldawson/CivForge/docs/REPO_HYGIENE.md).

Key non-negotiables:
- Gravity-mosaic source lives **only** at its own path. CivForge may **never** `open()`, `write()`, copy, or `cd` + mutate it directly.
- The **sole allowed bridge** is `tools/deploy-gravity-mosaic/deploy.sh` (inside CivForge). It always `cd`s to the gravity dir, runs exhaustive literal verification (`wc -l`, golden anchor `grep`, Python model + `EQUATIONS`/`to_artifact` tests, bad-legacy count == 0 for critical terms), then exact `git add`/`commit`/`push` of full content only. Post-push: hard-refresh https://mwd474747.github.io/gravity-mosaic-knowledge-graph/.
- Auth prototype is **100% separate**. Only the thin HTTP client (`tools/dawsos_auth_client.py`) and demo dependency (`/governance/protected_advance` using `requests` to :8081) exist in CivForge. No backend/auth code copied in.
- Borrowable patterns live in `docs/patterns/borrowable-governance-patterns.md` (separation template, receipt-first loop, FunForge, literal deploy bridge, FastAPI kernel, etc.). Copy/adapt the *patterns*, never the trees.
- Daily hygiene (before any push or major work): `git status --short`, clean runtime from commits (`.gitignore` covers `*.db`, logs/, `__pycache__`, ephemeral receipts, `.DS_Store`), find/grep audits for leakage, update SEPARATION/IMPLEMENTATION_STATUS/ROADMAP when boundaries change. See `docs/REPO_HYGIENE.md`.
- Receipts for everything. No meta/summaries in governed commits (gravity pushes especially).

**Current verified state (handoff snapshot)**: Audits clean, no source leakage, git clean on CivForge (`b2fd116`), gravity pristine, auth-proto locally committed and separate.

---

## 3. Current Implemented State (Mac Studio canonical, post-realign)

**Locked after aggressive refactor** (user directive: "remove the MVP in favour of the earlier FastAPI version and realign the repo and code fully ; aggressively refactor so the initial intent is implemented"; "gravity mosaic and civforge are two different projects"; "ensure the repos and workspaces are clean").

- **Backend**: FastAPI `backend/sim_api.py` on `http://localhost:8080` (uvicorn sim_api:app --reload --host 0.0.0.0 --port 8080). Preserves exact surface from user's pasted Codespaces block (`GET /state`, `POST /found_city` with investment check + detailed receipt containing turn/status/fun_score/claim, `POST /advance_turn`, `/integrate/civforge`) + governance extensions.
- **Core governance kernel** (pure Python, no Godot):
  - `core/orchestrator.py:GovernanceOrchestrator` — `advance_cycle(player_actions=0)` (see mechanics below).
  - `core/fun_forge.py:FunForge` — `calculate_fun_metrics`, `should_auto_reject(<80)`, `comment`.
  - `core/governance.py:GovernanceGate` — `propose` + `gate(proposal_id, fun_score)` (threshold 80.0 → PASS/NEEDS_REVIEW).
  - `core/agent_brain.py:AgentBrain` — per-workstream `receipt_memory`, `goal_stack`, `decide_action(state)`, `record_receipt` + reflection on low fun.
  - `core/receipts.py:ReceiptStore` — always writes human-readable `receipts/*.md`; optional SQLite (`gravity_backend.db`) for state_snapshots + receipts that survive restarts. `append`, `save_state`/`load_state`, `recent`.
- **Persistence**: Active (SQLite + disk receipts). On startup, backend restores last "game_state" snapshot if present. ~8 receipts/*.md + 20kB db at handoff.
- **Optional auth integration** (demo complete, end-to-end tested): `tools/dawsos_auth_client.py` (register-device, token, verify against :8081). `sim_api.py` has `require_govern_token` dependency + `/governance/protected_advance` (requires valid "govern" scope token from the separate prototype). Prototype itself has full flows (device/agent register, /token, /verify, JWT, seeds from ~/.openclaw, receipt logging, tests passing).
- **Drivers**:
  - `tools/civforge_cli.py` (status, advance, found, propose, gate, recommend, advisor, mcp-stub).
  - `bridge/civforge_http_bridge.py` (get_state, advance_cycle, propose_work, gate_proposal, get_gravity_recommendation — HTTP to :8080; used by Cursor local executor).
  - `tools/gravity_advisor.py` — safe_recommend_deploy (advisory only; explicitly refuses to touch gravity; points to deploy.sh).
- **Gravity deploy (sacred)**: `tools/deploy-gravity-mosaic/deploy.sh` + README (hardcoded paths noted as production caveat; literal verifs + git).
- **Godot MVP**: Removed from active tree (2026-06-16 hygiene). FastAPI + `core/` only; no Godot references in active code.
- **Docs & planning** (coherent post-auth extension): `SEPARATION.md` (canonical), `IMPLEMENTATION_STATUS.md` (locked canon), `ROADMAP.md` (Phases 0/1 complete; Phase 2 production items), `docs/REPO_HYGIENE.md`, `docs/patterns/borrowable-governance-patterns.md`, `ORCHESTRATION_PATTERNS.md`, `AGENTS.md`, `planning/production_deployment_assessment.md` (WP-PRODUCTION-ACCESS-ASSESSMENT-001 locked), `planning/extension_roadmap_v2.md`.
- **.gitignore**: Covers local state (no .db, logs, pyc, runtime receipt dumps in commits).
- **Live at handoff snapshot**: CivForge backend typically on 8080 (one process confirmed listening). Auth proto 8081 started on-demand for tests (not always running). Many duplicate long-running background verification/e2e scripts from the "execute optional steps" phase (harmless but noisy — see "Previous tasks hung" below).

**Git hygiene at handoff**: Clean on CivForge main after pushes including auth integration + docs coherence. Receipts and db are intentional (gitignore protects runtime copies).

---

## 4. Core Mechanics — The "Game" / Governance Rules (precise functions + ticks)

This is **not** a traditional 4X Godot game. The delivered value is a **receipt-first governed orchestration workspace** for safe, low-waste, auditable work on the separate gravity-mosaic project (and future targets). "Civ" / "city" / "territory" / "fun_score" / "resources" are internal metaphors for workstreams, attention budgets, quality, and founded governed items.

### Primary Tick: `core/orchestrator.py:35` — `GovernanceOrchestrator.advance_cycle(player_actions: int = 0)`

```python
def advance_cycle(self, player_actions: int = 0) -> Dict[str, Any]:
    self.turn += 1

    # Tick "resources" (steady governance budget)
    for k in self.workstream_resources:
        self.workstream_resources[k] += 1 if k != "deploy_budget" else 0

    # Agent decisions (main Grok + sub-agents)
    decisions = {}
    for aid, brain in self.brains.items():
        state = {"resources": self.workstream_resources}
        decision = brain.decide_action(state)
        decisions[aid] = decision
        brain.record_receipt({"turn": self.turn, "decision": decision})

    # Propose a representative work item this cycle (often gravity-related)
    proposal = self.gate.propose(self.turn, "govern_gravity_work", {"player_actions": player_actions, "decisions": decisions})

    # Score with FunForge (rigor of the cycle)
    fun_state = {"agency": min(1.0, player_actions / 3.0 + 0.5), "emergence": 0.9, "pacing": 0.85, "juice": 0.88}
    fun_score = FunForge.calculate_fun_metrics(fun_state)

    gate_result = self.gate.gate(proposal.id, fun_score, agent_comment=decisions.get("grok", ""))

    # Build rich receipt
    receipt = {
        "turn": self.turn,
        "status": "PASS" if gate_result.get("approved") else "NEEDS_REVIEW",
        "fun_score": fun_score,
        "comment": FunForge.comment(fun_score),
        "decisions": decisions,
        "proposal_id": proposal.id,
        "gate": gate_result,
        "resources": dict(self.workstream_resources),
    }
    self.receipts.append(receipt)
    # ... event + return with receipt, events, fun_score
```

Wired from:
- `backend/sim_api.py:149` `POST /advance_turn` (calls orchestrator, ticks player resources, appends to ReceiptStore + saves state snapshot).
- `sim_api.py:155` also drives `/found_city` (investment check on prod, detailed receipt with claim/fun_delta, work_packs).
- Governance endpoints: `/governance/propose`, `/governance/gate` (FunForge call inside), `/governance/gravity_deploy_recommendation` (advisory only), `/governance/protected_advance` (demo auth gate).

### FunForge Quality Gate (`core/fun_forge.py`)
- `calculate_fun_metrics(state)` → 0-100 from agency/emergence/pacing/juice (flexible keys).
- Threshold in `GovernanceGate.__init__(min_fun_for_execute=80.0)`.
- `should_auto_reject(score < 80)`, `comment(score)` (high-quality language for receipts).
- Called on every cycle + proposals. Low score → NEEDS_REVIEW or refactor trigger.

### AgentBrain (`core/agent_brain.py`)
- `decide_action(state)`: rule-based on prod/sci/resources + receipt_memory history + reflection (if recent fun <70, deprioritize "deploy").
- `record_receipt` + simple goal_stack rotation.
- Registered on backend startup: "grok" (main), "harper", "sebastian".

### Persistence & Receipts (`core/receipts.py`)
- `ReceiptStore(base_dir=receipts/, db_path=gravity_backend.db)`: `append(receipt, filename_hint)` always writes timestamped .md + INSERT to SQLite (receipts table + state_snapshots).
- `save_state`/`load_state("game_state")` — backend restores on startup.
- All major actions (found_city, advance_turn, propose, gate, gravity recs, external deploys) produce receipts.

### State Shape (preserved from original paste, semantics realigned)
`/state` returns current_turn, player (resources including "prod"/"verify_budget", territories=active work items, cities=founded packs, fun_score), ai_civs (sub-agents), recent_events, receipts, work_packs, note pointing to gravity deploy tool.

### Winning / Progress Criteria (current design)
- High cumulative fun/quality scores across receipts.
- Successful gated proposals that lead to verified deploys (via the literal bridge).
- Growing audit trail (receipts/ + DB) + clean separation.
- "Founding" work packs / governing multiple streams without waste.
- (Future) richer end conditions if simulation layer is added.

**Old Godot 4X mechanics** (TurnManager, DynamicsEngine, tile yields, work graphs, events, end conditions, full UI) were in the archived MVP. See "Extension path" below.

---

## 5. How to Run / Test / Drive (copy-paste ready)

**Start CivForge backend** (primary):
```bash
cd /Users/michaeldawson/CivForge
python3 -m pip install fastapi uvicorn pydantic requests --quiet 2>&1 | tail -1
python3 -m uvicorn backend.sim_api:app --reload --host 0.0.0.0 --port 8080
```
Test: `curl -s http://localhost:8080/state | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["current_turn"], d["fun_score"])'`

**Start separate auth prototype** (for protected flows / dawsOS interop):
```bash
python3 -m uvicorn backend.auth_api:app --port 8081
```
Health: `curl http://localhost:8081/health`

**CLI driver** (terminal-first, user's preferred style):
```bash
cd /Users/michaeldawson/CivForge
python3 tools/civforge_cli.py status
python3 tools/civforge_cli.py advance
python3 tools/civforge_cli.py found "New gravity node research"
python3 tools/civforge_cli.py recommend   # advisory only
python3 tools/civforge_cli.py run-deploy  # prints the strict deploy.sh command
```

**Auth prototype end-to-end (via CivForge client, optional)**:
```bash
cd /Users/michaeldawson/CivForge
python3 tools/dawsos_auth_client.py register-device civforge-handoff-test pk-handoff
# Then obtain identity_id + token (see scripts in prior e2e runs or manual):
# python3 -c '...' using subprocess calls to token with scope "govern"
curl -s -H "Authorization: Bearer $TOK" -X POST http://localhost:8080/governance/protected_advance
# Without token → 401/403 as expected
```

**Gravity deploy (the only way)**:
```bash
cd /Users/michaeldawson/CivForge
./tools/deploy-gravity-mosaic/deploy.sh
```
(After governance receipts + human review of literal state in the gravity dir. Follows all wc/grep/Python tests.)

**Grok/swarm bridge**:
```bash
cd /Users/michaeldawson/CivForge
python3 bridge/civforge_http_bridge.py   # or tools/civforge_cli.py
```

**Full hygiene / verification before any push**:
- `git status --short`
- `ls receipts/ | wc -l` + spot-check latest .md
- Confirm no cross-leakage: `find . -path '*/gravity-mosaic*' -o -path '*dawsos-auth*' | grep -v deploy | grep -v tools/dawsos_auth_client || echo "clean"`
- Read SEPARATION.md + this handoff before editing.

**Stop servers**: `pkill -f 'uvicorn.*sim_api'` and `pkill -f 'uvicorn.*auth_api'`.


Now that the prototype repo exists on GitHub, use the dedicated CivForge bridge to create the local clone and turn on auth.

From CivForge root (after literal review of this handoff + tools/auth-prototype/README.md):

```bash
cd /Users/michaeldawson/CivForge

# Create or update the local clone at the canonical separate location
./tools/auth-prototype/clone.sh

# Enable the auth function (starts the separate prototype on 8081)
./tools/auth-prototype/start.sh     # run in background / another terminal
```

Verification after start:

```bash
curl http://localhost:8081/health

# Full flow using the integrated CLI (thin client to the separate prototype)
python tools/civforge_cli.py auth register-device handoff-test pk-handoff
# (note the identity_id from output)

python tools/civforge_cli.py auth token <identity_id> govern
# (copy the token)

# Now protected CivForge governance works
curl -H "Authorization: Bearer $TOKEN" -X POST http://localhost:8080/governance/protected_advance
```

Without a valid "govern" token the protected endpoint returns 401/403.

The new bridge lives at `tools/auth-prototype/` (README.md + clone.sh + start.sh). It follows the same separation + literal verification philosophy as `tools/deploy-gravity-mosaic/`.

See also:
- `tools/dawsos_auth_client.py` (direct client)
- `backend/sim_api.py` (the require_govern_token dependency + protected_advance)
- `tools/auth-prototype/README.md` (full docs)
- Updated `tools/civforge_cli.py auth ...` subcommands

This completes the "create the local clone and steps to enable this function" request. The auth function is now first-class and documented for any workspace using the handoff package.

**Background task noise**: There may be many long-running duplicate e2e verification scripts from the "execute the optional steps" phase (task IDs like call-3220..., call-71be... etc.). They are safe (mostly curl + python client calls that eventually complete or were backgrounded). Use `pkill -f 'uvicorn|python3.*dawsos_auth_client'` or the scheduler/kill tools if output is cluttered. Old Godot --headless tasks were terminated earlier.

---

## 6. Pending Work + Immediate Next Steps (prioritized)

**#1 Right now (blocking clean handoff for auth prototype)**:
- Then, **in the separate auth-prototype directory**, after full literal disk review (cat key files, `git status`, `wc -l`, follow the same "push and deploy" process the user enforces everywhere):
  ```bash
  git status
  git add .
  # (review the diff/commit message literally)
  git commit -m "..."  # if needed
  git push -u origin main
  ```
- Update CivForge docs/receipts once pushed (with receipt).
- This was the explicit "optional steps" completion item left pending.

**#2 Why previous tasks "hung" (for successor awareness)**:
- Root cause: Bulk "execute all the above" + "complete as much as possible for MVP game" phases launched many `background: true` terminal commands for Godot 4 install (curl/unzip/PATH), Godot --headless --check-only verifications, PYCLEAN duplicate removal, scene/main.tscn creation, and duplicate symbol fixes.
- The famous "Parser Error: Function '_simulate_civs_wired' has the same name..." (and similar) occurred because bulk edits added full implementations while other scene-attached scripts already defined/calls the same names; no pre-edit symbol collision scan.
- Later pivot ("remove the MVP... aggressively refactor") + archive passes sent SIGTERM (signal 15) to the long-running background Godot tasks. They became irrelevant post-pivot to FastAPI + core/. Cleanup confirmed via ps/grep/scheduler_list (none active for Godot after archive). All resolved without violating separation.
- Lesson encoded in docs: pre-edit audits, literal verification, avoid bulk without checks, terminate orphans promptly.

**#3 Optional simulation layer extension** (from earlier removed Godot 4X mechanics):
- Port concepts (work graph / tile yields, DynamicsEngine events, richer AI turns, end conditions) as an **optional** mode/layer in `core/simulation/` (or similar).
- It must **feed the existing orchestrator/receipts/gate/FunForge** (e.g., simulation produces state deltas that become proposals or influence fun_score/agency).
- **Never** blur separation or mutate gravity-mosaic directly.
- Confirm with user before implementing (user asked "how could the earlier removed mechanics be extended into this current design?").

**Phase 2/3 (from ROADMAP + production assessment, locked)**:
- Docker + docker-compose (abstraction for hard-coded paths in deploy.sh first).
- Hosting (Railway/Render/etc.), auth hardening, scheduling.
- Starter gamified dashboard / Command Center (HTMX/Streamlit re-using workstream metaphor) on top of 8080 kernel.
- MCP wrapper exposure (with policy/auth), observability, backups.
- Public API/SDKs; gravity-mosaic as visible product; multi-project governance.
- See `planning/production_deployment_assessment.md` (gaps: hard-coded paths, local-first, no public exposure yet) and `planning/extension_roadmap_v2.md`.

**Other recurring**:
- Keep docs coherent on every change (SEPARATION, IMPLEMENTATION_STATUS, patterns, hygiene).
- Use receipt-first for all proposals/gates/deploys.
- When governing gravity work: propose/gate in CivForge → human reviews literal state in gravity dir → run deploy.sh → log external receipt back.

---

## 7. Known History / Pitfalls to Avoid

- **Godot pivot**: User chose FastAPI + core/ over the MVP. Pre-pivot code removed from active tree; history in git only.
- **Duplicate bug root cause + governance lesson**: Bulk execution without static/symbol scans before edits. Now mitigated by hygiene docs, pre-edit greps, and the governance gate itself.
- **Strict literal push rule**: User repeatedly requires full disk reads (`read_file` or terminal equivalents) + wc/grep verification + user-executed git for gravity (and now auth proto). Never bypass. The deploy.sh embodies it.
- **Background tasks**: Long-running ones from early "run in terminal" + background:true + pivot era. Clean them; prefer short/foreground or explicit monitoring.
- **Separation violations**: Easy to accidentally reference old paths or copy code. Always start from SEPARATION.md + this handoff. Audits (find/grep) before pushes.
- **Auth prototype**: Deliberately isolated for testing dawsOS-wide patterns. CivForge governs it optionally via HTTP/bridge, not by hosting or merging.
- **Production caveats** (from locked assessment): deploy.sh paths are local-only today; add config before remote use. SQLite is start of persistence.

---

## 8. Successor Instructions (what to do first)

1. Load this file + read the canonical SEPARATION.md, IMPLEMENTATION_STATUS.md, docs/patterns/borrowable-governance-patterns.md, and the core/*.py files verbatim on arrival.
2. `cd /Users/michaeldawson/CivForge && git status && git log --oneline -3` (re-verify snapshot).
3. Start the 8080 backend and confirm `/state` + one `advance` cycle works (and receipts are written).
4. (If auth flows needed) Start 8081 prototype + run client e2e (register → token with "govern" → protected_advance success; no-token failure).
5. Address the auth-prototype GitHub remote creation + literal push as the immediate pending item.
6. Ask the user for the next work pack / priority (simulation layer? Docker baseline? Specific gravity governance cycle? Dashboard? Hardening auth proto seeds/crypto?).
7. Before any code change or push on any project: literal disk read + hygiene checks + respect bridges only.
8. Produce receipts for your own actions. Update IMPLEMENTATION_STATUS / ROADMAP / this handoff when state meaningfully advances.
9. If the other workspace has different tools (e.g., different MCPs or no terminal execution), adapt via the bridge/CLI patterns or ask user for explicit instructions.

This package + the on-disk files (especially receipts/ for audit + the running 8080 kernel) are sufficient to continue without loss of context.

---

## 9. Key Files to Read Verbatim on Arrival (prioritized)

- `SEPARATION.md`
- `IMPLEMENTATION_STATUS.md`
- `core/orchestrator.py` (full advance_cycle)
- `core/fun_forge.py`, `core/governance.py`, `core/agent_brain.py`, `core/receipts.py`
- `backend/sim_api.py` (state shape + endpoints + auth demo at bottom)
- `tools/deploy-gravity-mosaic/deploy.sh` + its README (the rules)
- `tools/dawsos_auth_client.py`
- `docs/REPO_HYGIENE.md` + `docs/patterns/borrowable-governance-patterns.md`
- `ROADMAP.md` + `planning/production_deployment_assessment.md`
- Latest files in `receipts/`
- (In auth-proto dir) `backend/auth_api.py`, `docs/INTEROPERABILITY.md`, `tests/test_auth_flows.py`

**End of handoff package**. The work is in a clean, separated, receipted, testable state with explicit next action (auth proto remote push) and clear extension paths. Resume by confirming the auth push with the user and re-running the literal verification + git steps they require.

---

*Package generated faithfully from local disk state, prior conversation summary, exact code, docs, and user directives. No summaries substituted for primary source reads.*