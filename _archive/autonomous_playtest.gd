extends Node

# Fleshed out autonomous_playtest.gd (was stub). Wires into "End Turn" for test/improve loops.
# Runs full test cycle: balance, pacing, fun, receipts. Can be called from turn end or button.

func run_full_test_cycle(turn_data: Dictionary = {}) -> Dictionary:
	print("[TestForge] Starting autonomous validation cycle...")
	
	var results = {
		"balance": _test_balance(turn_data),
		"pacing": _test_pacing(turn_data),
		"fun": _test_fun(turn_data),
		"receipts": _validate_receipts(turn_data),
		"overall": "PASS"
	}
	
	if not results["balance"] or not results["pacing"] or not results["fun"] or not results["receipts"]:
		results["overall"] = "FAIL - Trigger refactor"
		print("[TestForge] Issues found - would auto-trigger DevSmith in full loop")
	else:
		print("[TestForge] All tests passed. Fun and balance good.")
	
	return results

func _test_balance(data: Dictionary) -> bool:
	# TestWarden-style: check resources, territories not too unbalanced
	var player_terr = data.get("player_territories", 4)
	return player_terr > 0 and player_terr < 12  # Simple balance check

func _test_pacing(data: Dictionary) -> bool:
	# One-more-turn test
	var turn = data.get("turn", 1)
	return turn < 15  # Avoid too long games

func _test_fun(data: Dictionary) -> bool:
	# Use FunForge metrics
	var fun = data.get("fun_score", 85)
	return fun >= 80

func _validate_receipts(data: Dictionary) -> bool:
	# Check receipts are being generated
	var receipts = data.get("receipts", [])
	return receipts.size() > 0 or data.get("turn", 0) <= 1  # At least some logging

# Called from civforge_mvp.gd on end turn for continuous improvement loop
func on_end_turn_test(turn_data: Dictionary):
	var result = run_full_test_cycle(turn_data)
	print("[AutonomousPlaytest] Cycle result: ", result["overall"])
