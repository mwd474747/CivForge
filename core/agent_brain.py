"""AgentBrain — Python port of the Godot Agent Brain Pattern.

Each 'civ' / workstream / sub-agent has:
- receipt_memory (list of past receipts for reflection)
- goal_stack (current priorities)
- decide_action(state) based on resources + memory + goals
- record_receipt + simple reflection (shift goals if fun/quality low)

Used by the FastAPI backend and orchestrator to make autonomous decisions
for gravity-mosaic work (research, verification, deploy proposals, etc.).
"""

from typing import Dict, Any, List


class AgentBrain:
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.receipt_memory: List[Dict[str, Any]] = []
        self.goal_stack: List[str] = ["research", "verify", "deploy", "govern"]
        self.current_goal: str = self.goal_stack[0]

    def record_receipt(self, receipt: Dict[str, Any]) -> None:
        self.receipt_memory.append(receipt)
        if len(self.receipt_memory) > 8:
            self.receipt_memory.pop(0)

        # Reflection: if quality/fun low, reprioritize away from risky actions
        fun = receipt.get("fun_score") or receipt.get("quality", 0)
        if fun and fun < 70:
            if "deploy" in self.goal_stack:
                self.goal_stack.remove("deploy")
                self.goal_stack.append("research")
            self.current_goal = self.goal_stack[0] if self.goal_stack else "govern"
        print(f"[AgentBrain] {self.name} recorded receipt. Current goal: {self.current_goal}")

    def decide_action(self, state: Dict[str, Any]) -> str:
        """Autonomous decision for the current governance cycle / work pack."""
        resources = state.get("resources", {})
        prod = resources.get("prod", 0) if isinstance(resources, dict) else 0
        sci = resources.get("sci", 0) if isinstance(resources, dict) else 0

        action = self.current_goal

        if prod < 4:
            action = "research"  # low prod → build knowledge / verify first
        elif sci < 6:
            action = "research"
        else:
            # Prefer from stack, but bias toward deploy when strong
            if "deploy" in self.goal_stack and prod > 8:
                action = "deploy"
            else:
                action = self.goal_stack[0] if self.goal_stack else "govern"

        # High recent quality → favor governance / careful deploy
        if self.receipt_memory:
            last = self.receipt_memory[-1]
            last_fun = last.get("fun_score") or last.get("quality", 0)
            if last_fun and last_fun > 85:
                action = "govern"

        self.current_goal = action
        return f"Decided: {action} (based on prod={prod}, sci={sci}, {len(self.receipt_memory)} receipts)"

    def get_current_goal(self) -> str:
        return f"{self.current_goal} (stack: {self.goal_stack})"
