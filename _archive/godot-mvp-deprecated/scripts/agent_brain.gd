extends Node

# AgentBrain - Per-civ "Godot Agent Brain Pattern" from ORCHESTRATION_PATTERNS.md
# Embedded receipt memory + goal stack for autonomous decisions.
# Used by civs in the MVP for AI + player tracking. Ties into FunForge, receipts, governance.

var civ_id: int = -1
var civ_name: String = ""
var receipt_memory: Array = []  # List of past receipts (turn, fun, actions, decisions)
var goal_stack: Array = []  # Current goals (e.g., "expand", "research", "diplo")
var current_goal: String = "idle"

func init_for_civ(id: int, name: String):
	civ_id = id
	civ_name = name
	goal_stack = ["expand", "research", "diplo"]  # Default priorities
	current_goal = goal_stack[0]
	receipt_memory = []
	print("[AgentBrain] Initialized for ", civ_name, " (ID:", civ_id, ") with goal stack: ", goal_stack)

func record_receipt(receipt: Dictionary):
	receipt_memory.append(receipt)
	if receipt_memory.size() > 5:  # Keep recent memory
		receipt_memory.pop_front()
	# Simple reflection: adjust goals based on past fun
	if receipt.has("fun") and receipt["fun"] < 70:
		if "expand" in goal_stack:
			goal_stack.erase("expand")
			goal_stack.push_back("research")  # Shift to research if low fun
		current_goal = goal_stack[0] if goal_stack.size() > 0 else "idle"
	print("[AgentBrain] ", civ_name, " recorded receipt. Current goal: ", current_goal)

func decide_action(civ_data: Dictionary) -> String:
	# Autonomous decision based on state + memory + goals
	var action = current_goal
	if civ_data["resources"][1] < 3:  # Low prod -> prioritize expand
		action = "expand"
	elif civ_data["resources"][2] < 5:  # Low sci -> research
		action = "research"
	else:
		action = goal_stack[randi() % goal_stack.size()] if goal_stack.size() > 0 else "idle"
	
	# Simulate "Grok" influence via memory
	if receipt_memory.size() > 0 and receipt_memory[-1].has("fun") and receipt_memory[-1]["fun"] > 85:
		action = "diplo"  # High fun -> diplomacy
	
	current_goal = action
	return "Decided: " + action + " (based on resources + " + str(receipt_memory.size()) + " receipts)"
	
func get_current_goal() -> String:
	return current_goal + " (stack: " + str(goal_stack) + ")"
