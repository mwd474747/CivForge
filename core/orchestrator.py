"""GovernanceOrchestrator — The TurnManager equivalent for CivForge governance cycles.

advance_cycle does:
- Agent brains decide
- FunForge quality check on proposed work
- Governance gate
- (Optional) call into deploy tools or other executors
- Generate and store rich receipt
- Update persistent state (fun/quality, resources for the workstreams)

This is what the FastAPI /advance_turn and new governance endpoints drive.
"""

from typing import Dict, Any, List
from .agent_brain import AgentBrain
from .fun_forge import FunForge
from .governance import GovernanceGate, Receipt
from .swarm_join import (
    CONFLICT_RESOLUTION_MODE,
    FANOUT_MAX,
    JOIN_STRATEGY,
    detect_delegate_conflict,
    ordered_agent_ids,
)


class GovernanceOrchestrator:
    def __init__(self):
        self.turn = 1
        self.brains: Dict[str, AgentBrain] = {}
        self.gate = GovernanceGate(min_fun_for_execute=80.0)
        self.receipts: List[Dict[str, Any]] = []
        self.events: List[str] = []
        # Workstream "resources" (attention, verification budget, etc.)
        self.workstream_resources = {"prod": 12, "sci": 8, "verify": 6, "deploy_budget": 5}

    def register_agent(self, agent_id: str, name: str) -> AgentBrain:
        brain = AgentBrain(agent_id, name)
        self.brains[agent_id] = brain
        return brain

    def advance_cycle(self, player_actions: int = 0) -> Dict[str, Any]:
        """One full governed cycle. Replaces the old turn advance."""
        self.turn += 1

        # Tick "resources" (steady governance budget)
        for k in self.workstream_resources:
            self.workstream_resources[k] += 1 if k != "deploy_budget" else 0

        # Agent decisions — sequential join (harper → sebastian → grok), fanout capped
        decisions: Dict[str, str] = {}
        state = {"resources": self.workstream_resources}
        for aid in ordered_agent_ids(self.brains.keys()):
            brain = self.brains[aid]
            decision = brain.decide_action(state)
            decisions[aid] = decision
            brain.record_receipt({"turn": self.turn, "decision": decision})

        delegate_conflict = detect_delegate_conflict(decisions)

        # Propose a representative work item this cycle (often gravity-related)
        proposal = self.gate.propose(
            self.turn,
            "govern_gravity_work",
            {
                "player_actions": player_actions,
                "decisions": decisions,
                "delegate_conflict": delegate_conflict,
            }
        )

        # Score with FunForge (rigor of the cycle)
        fun_state = {
            "agency": min(1.0, player_actions / 3.0 + 0.5),
            "emergence": 0.9,
            "pacing": 0.85,
            "juice": 0.88
        }
        fun_score = FunForge.calculate_fun_metrics(fun_state)

        gate_result = self.gate.gate(proposal.id, fun_score, agent_comment=decisions.get("grok", ""))

        approved = bool(gate_result.get("approved")) and not delegate_conflict
        receipt = {
            "turn": self.turn,
            "status": "PASS" if approved else "NEEDS_REVIEW",
            "fun_score": fun_score,
            "comment": FunForge.comment(fun_score),
            "decisions": decisions,
            "proposal_id": proposal.id,
            "gate": gate_result,
            "resources": dict(self.workstream_resources),
            "join_strategy": JOIN_STRATEGY,
            "fanout_max": FANOUT_MAX,
            "delegate_conflict": delegate_conflict,
            "conflict_resolution_mode": CONFLICT_RESOLUTION_MODE if delegate_conflict else None,
        }
        self.receipts.append(receipt)

        event = f"Turn {self.turn}: Cycle advanced. Fun/Quality: {fun_score}. Gate: {gate_result.get('approved')}"
        self.events.append(event)

        return {
            "turn": self.turn,
            "receipt": receipt,
            "events": self.events[-3:],
            "fun_score": fun_score,
        }

    def log_external_receipt(self, receipt: Dict[str, Any]) -> None:
        """For when the gravity deploy tool or other external thing produces a receipt."""
        receipt["turn"] = self.turn
        self.receipts.append(receipt)
        self.events.append(f"External receipt logged for turn {self.turn}")
