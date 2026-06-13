"""FunForge — Quality / Engagement scorer for work outputs (Python port).

Originally from the Godot agents/fun_forge.gd.
Calculates a "fun_score" (0-100) from agency, emergence, pacing, juice (here: rigor, coverage,
verification strength, clarity of receipt).

Auto-reject guidance: scores < 80 should trigger refactor or more verification before
allowing a gravity-mosaic deploy or major work pack to proceed.
"""

from typing import Dict, Any


class FunForge:
    @staticmethod
    def calculate_fun_metrics(state: Dict[str, Any]) -> float:
        """
        state keys (flexible):
          agency: how much real choice / proposal power the human/agent had
          emergence: interlocking systems (research -> verify -> literal deploy -> receipt)
          pacing: steady progress without waste
          juice: clarity, surprise/insight, strong receipts, visible verification
        """
        agency = float(state.get("agency", 0.8))
        emergence = float(state.get("emergence", 0.85))
        pacing = float(state.get("pacing", 0.8))
        juice = float(state.get("juice", 0.9))

        score = (agency + emergence + pacing + juice) / 4.0 * 100.0
        return round(min(100.0, max(0.0, score)), 1)

    @staticmethod
    def should_auto_reject(score: float) -> bool:
        return score < 80.0

    @staticmethod
    def comment(score: float) -> str:
        if score < 70:
            return "Auto-reject: insufficient rigor or verification. Trigger refactor."
        if score < 80:
            return "Low quality: add more literal checks / receipts before proceeding."
        if score < 90:
            return "Acceptable. Consider extra verification pass."
        return "High quality work. Good for deploy."
