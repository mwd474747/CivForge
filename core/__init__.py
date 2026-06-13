"""CivForge Core — Python implementation of the core agentic governance patterns.

This replaces the Godot MVP layer. The valuable patterns (AgentBrain with receipt memory + goal stack,
FunForge quality scoring, receipt-first governance, orchestration cycles) now live here as the
foundation for the FastAPI workspace that governs the separate gravity-mosaic project (and future work).

All changes to gravity-mosaic must still go through the strict tools/deploy-gravity-mosaic/deploy.sh
with literal disk verification. This core + backend provides the persistent state, agent decisions,
governance gates, and receipts for that process.
"""

from .agent_brain import AgentBrain
from .fun_forge import FunForge
from .governance import GovernanceGate, Receipt
from .orchestrator import GovernanceOrchestrator
from .receipts import ReceiptStore

__all__ = [
    "AgentBrain",
    "FunForge",
    "GovernanceGate",
    "Receipt",
    "GovernanceOrchestrator",
    "ReceiptStore",
]
