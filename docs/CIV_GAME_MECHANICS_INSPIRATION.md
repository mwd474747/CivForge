# Civ Game Mechanics Inspiration Notes (from pre-pivot history, for reference only)

**Important**: This is abstract conceptual notes only. No code, no Godot, no pre-pivot revival. All new implementation must be pure Python, simple base, infinitely extendible via the governed proposal → FunForge gate → pluggable module loop. See locked planning docs and core/ for the actual kernel.

## Concepts that informed the need for a Simulation Layer (now REQUIRED)
- Emergent / interlocking dynamics (resources affecting multiple systems, feedback loops creating narrative events).
- Turn-based resolution with state changes that can cascade (economy, diplomacy, "hero rises" style moments).
- Test/validation loops for balance, pacing, fun/quality, and receipts (to trigger refactor or improvement proposals).

These ideas map directly to the locked requirement for a "simulation layer for game mechanics (simple, pure-Python, infinitely extendible dynamics/yields/events/end-conditions feeding the orchestrator/receipts/gate)".

## Patterns already successfully extracted (do not re-extract)
- AgentBrain with receipt memory + goal stack + decide_action + reflection → core/agent_brain.py
- FunForge quality scoring (agency/emergence/pacing/juice) → core/fun_forge.py
- Turn/cycle management + receipts → core/orchestrator.py + ReceiptStore

## How to use these notes going forward
When implementing the simulation layer or extending mechanics (as a governed work pack in lane/civ-game-mechanics or similar):
1. Propose the specific new mechanic or module.
2. Score with FunForge (does it increase interesting emergence, good pacing for play, discovery/juice?).
3. If gated, implement cleanly in Python as a pluggable extension.
4. Log as receipt.

Do not copy or revive any GDScript, scenes, or old 4X structure. The goal is a simple core that compounds through agent/human proposals under governance.

See:
- planning/extension_roadmap_v2.md and production_deployment_assessment.md (required simulation layer)
- receipts/mechanics-extension-sim-*.md (example governed proposal for this)
- AGENTS.md (GameMechanicDesigner role)
- docs/GIT_LANES_POLICY.md

This note exists only to capture "why these concepts were valuable" without polluting the current clean state.
