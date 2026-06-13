extends Control

# CivForge MVP - Playable 4X Vertical Slice (Enhanced with agent loops, receipts, economy, etc.)
# Turn-based autonomous simulation with player actions, AI civs, receipts, FunForge scoring.
# Built to demonstrate core loop for the Intelligent Civilization Simulator.
# Self-contained UI creation for robustness (works even with minimal .tscn).
# Now includes: Wired stubs, per-civ AgentBrain with goal stack + receipts, simple economy (resource tiles),
# basic diplomacy events, Agent Decision label in UI, governance gate toggle, expanded test loop.

@onready var turn_label: Label = $HUD/TopBar/TurnLabel
@onready var fun_label: Label = $HUD/TopBar/FunLabel
@onready var fun_bar: ProgressBar = $HUD/TopBar/FunBar
@onready var resources_panel: VBoxContainer = $HUD/LeftPanel/Resources
@onready var map_grid: GridContainer = $HUD/CenterPanel/MapGrid
@onready var log_label: RichTextLabel = $HUD/RightPanel/EventLog
@onready var actions_container: HBoxContainer = $HUD/BottomBar/Actions
@onready var end_turn_btn: Button = $HUD/BottomBar/EndTurnBtn
@onready var summary_panel: Panel = $HUD/SummaryPanel
@onready var summary_label: Label = $HUD/SummaryPanel/SummaryLabel
@onready var agent_decision_label: Label = $HUD/TopBar/AgentDecisionLabel  # New for agent visibility
@onready var governance_toggle: CheckButton = $HUD/BottomBar/GovernanceToggle  # New governance gate

# Game Data - 3 Civs (0=Player, 1=AI Scholars, 2=AI Warlords)
var civs: Array = []
var map_owners: Array = []  # 16 territories, values 0,1,2
var map_resources: Array = []  # Simple economy: base yield per tile (food/prod/sci)
var current_turn: int = 1
var max_turns: int = 10
var player_actions_this_turn: int = 0
var game_log: Array = []
var is_game_over: bool = false
var governance_enabled: bool = true  # Toggle for governance gate

# Simple resources per civ: [Food, Prod, Sci, Influence]
const RESOURCE_NAMES = ["Food", "Prod", "Sci", "Influence"]
const PLAYER_COLOR = Color(0.3, 0.6, 1.0)
const AI1_COLOR = Color(0.3, 0.9, 0.4)  # Scholars
const AI2_COLOR = Color(0.9, 0.3, 0.3)  # Warlords

# Preloaded agent libs (from existing CivForge scripts)
var FunForgeLib = preload("res://scripts/agents/fun_forge.gd")
var DynamicsLib = preload("res://scripts/gameplay/dynamics_engine.gd")
var TurnManagerLib = preload("res://scripts/gameplay/turn_manager.gd")
var AgentBrain = preload("res://scripts/agent_brain.gd")  # New

var turn_manager: Node
var agent_brains: Array = []  # Per-civ brains with goal stacks + receipts

func _ready():
	randomize()
	_init_civs()
	_init_map()
	_setup_ui()
	_create_map_visuals()
	
	# Instance existing TurnManager for compatibility with original scripts
	turn_manager = TurnManagerLib.new()
	add_child(turn_manager)
	
	# Create per-civ AgentBrains (new: embedded receipt memory + goal stack)
	for i in range(civs.size()):
		var brain = AgentBrain.new()
		brain.init_for_civ(civs[i]["id"], civs[i]["name"])
		add_child(brain)
		agent_brains.append(brain)
	
	_log_event("[CivForge] MVP Simulation Initialized. 4X core loop active with AgentBrains + Receipts.", Color.WHITE)
	_log_event("Player Empire (Blue) vs AI Scholars (Green) vs AI Warlords (Red).", Color.LIGHT_GRAY)
	_update_all_ui()
	
	# Auto-start first turn feel
	_log_event("Turn 1: Your capital claims surrounding lands. Use actions below! (Governance gate enabled)", Color.CYAN)

func _init_civs():
	civs = [
		{ "id": 0, "name": "Player Empire", "color": PLAYER_COLOR, "resources": [12, 8, 5, 4], "territories": 4, "score": 0, "cities": 1 },
		{ "id": 1, "name": "AI Scholars", "color": AI1_COLOR, "resources": [10, 6, 9, 3], "territories": 3, "score": 0, "cities": 1 },
		{ "id": 2, "name": "AI Warlords", "color": AI2_COLOR, "resources": [8, 11, 4, 2], "territories": 3, "score": 0, "cities": 1 }
	]

func _init_map():
	map_owners = []
	map_resources = []
	for i in range(16):
		if i in [5,6,9,10]:  # 2x2 center for player
			map_owners.append(0)
			map_resources.append(2)  # High yield
		elif i in [0,1,4]:   # Top-left for AI1
			map_owners.append(1)
			map_resources.append(2)
		elif i in [11,14,15]: # Bottom-right for AI2
			map_owners.append(2)
			map_resources.append(2)
		else:
			map_owners.append(-1)  # Neutral
			map_resources.append(1)  # Base yield

func _setup_ui():
	if not end_turn_btn:
		_create_full_ui()  # Self-contained fallback
	
	# Connect main buttons
	if end_turn_btn:
		end_turn_btn.pressed.connect(_on_end_turn_pressed)
	
	# Connect action buttons (from scene or created)
	_connect_action_buttons()
	
	# Governance toggle
	if governance_toggle:
		governance_toggle.button_pressed = governance_enabled
		governance_toggle.toggled.connect(func(on): governance_enabled = on)

func _connect_action_buttons():
	# Assume scene has buttons named ExpandBtn, ResearchBtn, DiploBtn under actions
	# Or use dynamic if fallback
	var actions = actions_container if actions_container else null
	if actions:
		for child in actions.get_children():
			if child is Button:
				if "Expand" in child.text:
					child.pressed.connect(func(): _player_action(0))
				elif "Research" in child.text:
					child.pressed.connect(func(): _player_action(1))
				elif "Diplomacy" in child.text or "Diplo" in child.text:
					child.pressed.connect(func(): _player_action(2))

func _create_full_ui():
	# Full self-contained UI (as before, but enhanced with agent_decision_label and governance_toggle)
	var root = self
	root.custom_minimum_size = Vector2(960, 640)
	
	var vbox = VBoxContainer.new()
	vbox.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(vbox)
	
	# Top bar (enhanced with Agent Decision)
	var top = HBoxContainer.new()
	turn_label = Label.new()
	turn_label.add_theme_font_size_override("font_size", 18)
	fun_label = Label.new()
	fun_label.add_theme_font_size_override("font_size", 16)
	fun_bar = ProgressBar.new()
	fun_bar.custom_minimum_size = Vector2(200, 20)
	agent_decision_label = Label.new()
	agent_decision_label.text = "Agent: Idle"
	agent_decision_label.add_theme_font_size_override("font_size", 14)
	top.add_child(turn_label)
	top.add_child(fun_label)
	top.add_child(fun_bar)
	top.add_child(agent_decision_label)
	vbox.add_child(top)
	
	# Main HBox
	var main_h = HBoxContainer.new()
	vbox.add_child(main_h)
	
	# Left: Resources
	resources_container = VBoxContainer.new()
	resources_container.custom_minimum_size = Vector2(180, 0)
	var res_title = Label.new()
	res_title.text = "RESOURCES"
	resources_container.add_child(res_title)
	for i in 4:
		var h = HBoxContainer.new()
		var l = Label.new()
		l.name = "Res" + str(i)
		l.text = RESOURCE_NAMES[i] + ": 0 (+0)"
		h.add_child(l)
		resources_container.add_child(h)
	main_h.add_child(resources_container)
	
	# Center: Map
	var map_panel = VBoxContainer.new()
	map_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var map_title = Label.new()
	map_title.text = "WORLD MAP (Click neutral to Expand)"
	map_panel.add_child(map_title)
	map_grid = GridContainer.new()
	map_grid.columns = 4
	for i in 16:
		var cell = ColorRect.new()
		cell.custom_minimum_size = Vector2(80, 80)
		cell.name = "Tile" + str(i)
		var lbl = Label.new()
		lbl.name = "TileLabel"
		lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		lbl.add_theme_font_size_override("font_size", 11)
		cell.add_child(lbl)
		cell.gui_input.connect(_on_tile_gui_input.bind(i))
		map_grid.add_child(cell)
	map_panel.add_child(map_grid)
	main_h.add_child(map_panel)
	
	# Right: Log
	var log_panel = VBoxContainer.new()
	log_panel.custom_minimum_size = Vector2(260, 0)
	var log_title = Label.new()
	log_title.text = "EVENT LOG / RECEIPTS"
	log_panel.add_child(log_title)
	log_label = RichTextLabel.new()
	log_label.custom_minimum_size = Vector2(240, 400)
	log_label.bbcode_enabled = true
	log_label.scroll_following = true
	log_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	log_panel.add_child(log_label)
	main_h.add_child(log_panel)
	
	# Bottom: Actions + Governance
	var bottom = HBoxContainer.new()
	var expand_btn = Button.new()
	expand_btn.text = "Expand (+Territory)"
	expand_btn.pressed.connect(func(): _player_action(0))
	var research_btn = Button.new()
	research_btn.text = "Research (+Sci)"
	research_btn.pressed.connect(func(): _player_action(1))
	var diplo_btn = Button.new()
	diplo_btn.text = "Diplomacy"
	diplo_btn.pressed.connect(func(): _player_action(2))
	end_turn_btn = Button.new()
	end_turn_btn.text = "END TURN"
	end_turn_btn.pressed.connect(_on_end_turn_pressed)
	governance_toggle = CheckButton.new()
	governance_toggle.text = "Governance Gate"
	governance_toggle.button_pressed = governance_enabled
	governance_toggle.toggled.connect(func(on): governance_enabled = on)
	bottom.add_child(expand_btn)
	bottom.add_child(research_btn)
	bottom.add_child(diplo_btn)
	bottom.add_child(end_turn_btn)
	bottom.add_child(governance_toggle)
	vbox.add_child(bottom)
	
	# Summary
	summary_panel = Panel.new()
	summary_panel.visible = false
	summary_label = Label.new()
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	summary_panel.add_child(summary_label)
	vbox.add_child(summary_panel)

func _player_action(action_type: int):
	if is_game_over: return
	var civ = civs[0]
	var cost = 3
	if civ["resources"][1] < cost:
		_log_event("Not enough Production to act!", Color.ORANGE)
		return
	
	if governance_enabled and action_type == 0 and civ["territories"] > 6:  # Governance gate example
		_log_event("[Governance] Action requires approval - simulating receipt gate (PASS for demo)", Color.YELLOW)
	
	civs[0]["resources"][1] -= cost
	player_actions_this_turn += 1
	
	match action_type:
		0: # Expand
			_claim_territory(0)
			civs[0]["territories"] += 1
			_log_event("You expanded your empire! +1 territory.", Color.GREEN)
		1: # Research
			civs[0]["resources"][2] += 4
			_log_event("Research investment pays off. +Science.", Color.CYAN)
		2: # Diplomacy
			var target = 1 if randf() > 0.5 else 2
			civs[target]["resources"][3] += 2
			civs[0]["resources"][3] += 3
			_log_event("Diplomatic success with " + civs[target]["name"] + "!", Color.YELLOW)
	
	# Update agent brain for player (simple)
	if agent_brains.size() > 0:
		agent_brains[0].record_receipt({"action": action_type, "turn": current_turn})
		agent_decision_label.text = "Agent (Player): " + agent_brains[0].get_current_goal()
	
	_update_all_ui()

func _claim_territory(owner_id: int):
	for i in map_owners.size():
		if map_owners[i] == -1:
			map_owners[i] = owner_id
			map_resources[i] = 2  # Boost yield
			break

func _on_end_turn_pressed():
	if is_game_over: return
	_end_turn()

func _end_turn():
	_simulate_ai_turns()
	_resolve_dynamics()
	_tick_resources()
	
	# Call original turn manager for receipt compatibility + wire stubs
	if turn_manager and turn_manager.has_method("advance_turn"):
		turn_manager.simulate_civs = _simulate_civs_wired  # Wire the stub
		turn_manager.ensure_fun_score = _ensure_fun_score_wired
		turn_manager.advance_turn({"player_actions": player_actions_this_turn})
	
	# Fun calculation (use FunForge + agent brains)
	var state = {
		"agency": float(player_actions_this_turn) / 3.0,
		"emergence": randf_range(0.7, 1.0),
		"pacing": clamp(float(current_turn) / 5.0, 0.5, 1.0),
		"juice": 0.9
	}
	var fun_score = FunForgeLib.calculate_fun_metrics(state)
	civs[0]["score"] = fun_score
	
	# Update agent brains with receipts
	for i in range(agent_brains.size()):
		var brain = agent_brains[i]
		brain.record_receipt({"turn": current_turn, "fun": fun_score, "actions": player_actions_this_turn})
		if i > 0:  # AI agents decide
			var decision = brain.decide_action(civs[i])
			_log_event("[Agent " + civs[i]["name"] + "]: " + decision, civs[i]["color"])
	
	_log_event("[Receipt] Turn %d complete. Fun: %.0f | Actions: %d" % [current_turn, fun_score, player_actions_this_turn], Color.LIGHT_BLUE)
	
	current_turn += 1
	player_actions_this_turn = 0
	agent_decision_label.text = "Agent: Turn advanced"
	
	_update_all_ui()
	_check_end_game()

# Wired versions of stubs (called from turn_manager)
func _simulate_civs_wired():
	# Now actually does economy + expansion (was pass)
	for i in range(civs.size()):
		var civ = civs[i]
		var base = civ["territories"] * 0.5
		civ["resources"][0] += int(base)  # Food from territories
		if randf() > 0.6 and civ["id"] != 0:
			civ["territories"] = min(civ["territories"] + 1, 12)
			_claim_territory(civ["id"])
			_log_event(civ["name"] + " expanded via agent decision.", civ["color"])

func _ensure_fun_score_wired():
	# Now actually calls FunForge and updates
	var state = {"agency": 0.8, "emergence": 0.9, "pacing": 0.85, "juice": 0.9}
	var score = FunForgeLib.calculate_fun_metrics(state)
	if score < 80:
		_log_event("[FunForge] Score low (" + str(score) + ") - would trigger refactor in full system", Color.RED)
	else:
		_log_event("[FunForge] Score good: " + str(score), Color.GREEN)

func _simulate_ai_turns():
	for i in range(1, civs.size()):
		var civ = civs[i]
		var action = randi() % 3
		match action:
			0: # Expand
				civ["territories"] = min(civ["territories"] + 1, 12)
				_claim_territory(civ["id"])
				_log_event(civ["name"] + " expanded.", civ["color"])
			1: # Research
				civ["resources"][2] += 3
				_log_event(civ["name"] + " researched.", civ["color"])
			2: # "War" or diplo
				civ["resources"][1] += 2
				_log_event(civ["name"] + " focused on production.", civ["color"])

func _resolve_dynamics():
	if randf() > 0.6:
		var civ_idx = randi() % civs.size()
		var civ = civs[civ_idx]
		var event = ["Good Harvest", "Border Tension", "Tech Breakthrough", "Trade Boom", "Unrest"].pick_random()
		match event:
			"Good Harvest":
				civ["resources"][0] += 5
			"Border Tension":
				civ["resources"][1] -= 2
				if civ_idx > 0: civs[0]["resources"][3] += 1
			"Tech Breakthrough":
				civ["resources"][2] += 4
			"Trade Boom":
				civ["resources"][3] += 3
			"Unrest":
				civ["resources"][0] -= 3
		_log_event("[Dynamics] " + event + " for " + civ["name"] + "!", Color.MAGENTA)
	
	if DynamicsLib:
		DynamicsLib.new().resolve_action(civs[randi() % civs.size()]["name"], "turn_event", {})

func _tick_resources():
	for civ in civs:
		var base = civ["territories"] * 1.2
		for i in 4:
			civ["resources"][i] += int(base * (0.9 + (i * 0.1)))
			civ["resources"][i] = max(0, civ["resources"][i])
		civ["score"] += civ["territories"] * 0.5

func _update_all_ui():
	if is_game_over: return
	if turn_label: turn_label.text = "Turn %d / %d" % [current_turn, max_turns]
	var fun = civs[0]["score"]
	if fun_label: fun_label.text = "Fun Score: %.0f" % fun
	if fun_bar: fun_bar.value = clamp(fun, 0, 100)
	
	# Resources
	if resources_container:
		var children = resources_container.get_children()
		for i in range(4):
			if i + 1 < children.size() and children[i+1] is HBoxContainer:
				var lbl = children[i+1].get_child(0) as Label
				if lbl:
					var val = civs[0]["resources"][i]
					var delta = "+%d" % int(civs[0]["territories"] * (1.1 if i==0 else 0.9 if i==1 else 0.7 if i==2 else 0.5))
					lbl.text = "%s: %d (%s)" % [RESOURCE_NAMES[i], val, delta]
	
	# Map
	if map_grid:
		for i in 16:
			if i < map_grid.get_child_count():
				var cell = map_grid.get_child(i) as ColorRect
				if cell:
					var owner = map_owners[i]
					var color = Color(0.4, 0.4, 0.4)
					var text = "?"
					if owner == 0: color = PLAYER_COLOR; text = "P"
					elif owner == 1: color = AI1_COLOR; text = "S"
					elif owner == 2: color = AI2_COLOR; text = "W"
					cell.color = color
					var lbl = cell.get_node("TileLabel") as Label
					if lbl:
						var pop = 1 + (i % 3) + (map_resources[i] if i < map_resources.size() else 0)
						lbl.text = "%s%d" % [text, pop]
	
	# Agent decision (simple from first brain)
	if agent_decision_label and agent_brains.size() > 0:
		agent_decision_label.text = "Agent: " + agent_brains[0].get_current_goal()

func _log_event(text: String, color: Color = Color.WHITE):
	game_log.append(text)
	if log_label:
		log_label.append_text("[color=#%s]%s[/color]\n" % [color.to_html(false), text])

func _check_end_game():
	if current_turn > max_turns or civs[0]["territories"] >= 10:
		is_game_over = true
		var final_fun = civs[0]["score"]
		var msg = "MVP COMPLETE!\n\nTurns: %d\nFinal Fun: %.0f\nTerritories: %d\n\nThanks for the CivForge prototype.\nCore 4X + AgentBrains + Receipts + FunForge + Governance demonstrated.\nSee CivForge docs for next phases (swarm, full 4X, headless)." % [current_turn-1, final_fun, civs[0]["territories"]]
		if summary_label: summary_label.text = msg
		if summary_panel: summary_panel.visible = true
		if end_turn_btn: end_turn_btn.disabled = true
		_log_event("=== GAME OVER - Receipt Generated ===", Color.GOLD)

func _on_tile_gui_input(event: InputEvent, idx: int):
	if is_game_over: return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if map_owners[idx] != -1: return
		if civs[0]["resources"][1] >= 2:
			civs[0]["resources"][1] -= 2
			map_owners[idx] = 0
			map_resources[idx] = 2
			civs[0]["territories"] += 1
			player_actions_this_turn += 1
			_log_event("You claimed new territory!", Color.GREEN)
			_update_all_ui()
		else:
			_log_event("Need more Production to expand.", Color.ORANGE)

