"""Governance — Receipt-first gates and proposal handling.

Proposal → Gate check (via FunForge quality + agent input) → Execute (e.g. gravity deploy tool) → Detailed Receipt.

This is the heart of the realigned CivForge: the FastAPI + core provides the persistent
governed workspace. The actual gravity-mosaic changes always happen on the separate project
via the strict deploy tool (literal full reads, wc/grep verifs, no meta).
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class Receipt:
    id: str
    turn: int
    action: str
    status: str = "PROPOSED"
    fun_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GovernanceGate:
    def __init__(self, min_fun_for_execute: float = 80.0):
        self.min_fun_for_execute = min_fun_for_execute
        self.proposals: List[Receipt] = []

    def load_proposals(self, proposals: List[Dict[str, Any]]) -> None:
        """Restore proposal state from persisted snapshots.

        ReceiptStore owns durable storage. The gate keeps only the active in-memory
        working set, so startup has to rehydrate it before `/governance/gate`
        can truthfully evaluate proposals created before a restart.
        """
        restored: List[Receipt] = []
        for item in proposals:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            restored.append(
                Receipt(
                    id=str(item["id"]),
                    turn=int(item.get("turn", 0) or 0),
                    action=str(item.get("action", "unknown")),
                    status=str(item.get("status", "PROPOSED")),
                    fun_score=float(item.get("fun_score", 0) or 0),
                    details=dict(item.get("details") or {}),
                    timestamp=str(item.get("timestamp") or datetime.utcnow().isoformat()),
                )
            )
        self.proposals = restored

    def propose(self, turn: int, action: str, details: Dict[str, Any]) -> Receipt:
        receipt = Receipt(
            id=str(uuid.uuid4())[:8],
            turn=turn,
            action=action,
            status="PROPOSED",
            details=details,
        )
        self.proposals.append(receipt)
        return receipt

    def gate(self, proposal_id: str, fun_score: float, agent_comment: str = "") -> Dict[str, Any]:
        for p in self.proposals:
            if p.id == proposal_id:
                p.fun_score = fun_score
                if fun_score >= self.min_fun_for_execute:
                    p.status = "GATED_APPROVED"
                    return {"approved": True, "receipt": p.to_dict(), "comment": agent_comment or "Quality sufficient."}
                else:
                    p.status = "GATED_REJECTED"
                    return {"approved": False, "receipt": p.to_dict(), "comment": agent_comment or "Below threshold. Add verification."}
        return {"error": "Proposal not found"}

    def log_execution_receipt(self, proposal_id: str, execution_details: Dict[str, Any]) -> Receipt:
        for p in self.proposals:
            if p.id == proposal_id:
                p.status = "EXECUTED"
                p.details.update(execution_details)
                return p
        # fallback new receipt
        return Receipt(id=proposal_id, turn=0, action="execution", details=execution_details)
