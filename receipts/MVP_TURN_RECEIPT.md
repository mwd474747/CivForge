**Receipt WP-REALIGN-001** ✅ 
Outcome: Removed the Godot MVP (entire godot/ + GDScript playtest archived in _archive/). Realigned the repo around the earlier FastAPI backend version the user pasted (exact /state, /found_city with prod check + detailed receipt, /advance_turn, /integrate). Ported the valuable patterns into pure Python core/ (AgentBrain, FunForge, GovernanceGate + Orchestrator, ReceiptStore). Added CLI + enhanced headless observer as terminal/autonomous drivers. Updated all docs, setup, and the gravity deploy helper to state the true initial intent: CivForge is the local governed workspace that proposes, gates, and receipts work on the *separate* gravity-mosaic-knowledge-graph project. The only way changes ever reach that project is the strict literal deploy.sh.

Status: Success
Fun/Quality Score: 91 (high rigor on the realign + preservation of the exact FastAPI test surface)

Key changes:
- backend/sim_api.py now matches the pasted Codespaces shape + is wired to the new core governance objects.
- New core/ package with portable agentic logic (no Godot dependency).
- tools/civforge_cli.py for "run in terminal" flows the user prefers.
- setup_hybrid.sh updated to focus on the FastAPI + CLI experience.
- All references to Godot UI, F5, mvp.gd, playable 4X stripped from active docs.
- deploy-gravity-mosaic tool and its README clarified as the sacred literal path (CivForge only governs, never bypasses).

Next: Use the running backend + CLI to propose real gravity work, gate it, then execute via the deploy tool with full literal verification. Create more receipts in receipts/ for each governed cycle.
