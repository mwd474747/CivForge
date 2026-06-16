# Work Pack: Military Conflict Defeat Review + Sim 001

**ID:** `WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001`  
**Lane:** `lane/civ-game-mechanics` + `lane/simulation`  
**Owner:** Grok swarm (planning PRIME) → **Cursor** (execution)  
**Label:** `planning` until Cursor execution receipt linked

---

## Proposal envelope

```json
{
  "kind": "review_and_simulation_block",
  "title": "military conflict defeat review + multi-round simulation with current extensions",
  "payload": {
    "review_scope": [
      "military legacy chains",
      "conflict triggers",
      "defeat cascades",
      "diplomacy betrayal",
      "alliance stability"
    ],
    "simulation": {
      "rounds": 50,
      "agents": 5,
      "include": ["civstudy patterns", "current extensions", "multi-agent interactions"]
    }
  },
  "work_pack_id": "WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001"
}
```

---

## Cursor execution

| Artifact | Path |
|----------|------|
| Review + sim engine | `backend/military_conflict_defeat_review.py` |
| CLI | `tools/military_conflict_defeat_review_sim.py` |
| Tests | `tests/test_military_conflict_defeat_review_sim.py` |
| Execution receipt | `receipts/cursor-execution-wp-military-conflict-defeat-review-sim-001-*.md` |

```bash
cd ~/CivForge
python3 -m pytest tests/test_military_conflict_defeat_review_sim.py tests/ -q
python3 tools/military_conflict_defeat_review_sim.py --mode kernel --rounds 50
bash tools/validate-game.sh --read-only
```

---

## Grok PRIME closure

Link Cursor execution receipt only. Tag Grok receipt: **planning**. Tag Cursor receipt: **current**.
