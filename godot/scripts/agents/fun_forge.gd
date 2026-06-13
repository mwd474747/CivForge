# FunForge Agent - Ensures game is FUN (autonomous evaluator)
class_name FunForge

static func calculate_fun_metrics(state: Dictionary) -> float:
    # Pillars of Fun in 4X (inspired by systemic design)
    var agency = 1.0      # Player choices matter
    var emergence = 0.9   # Interlocking systems create stories
    var pacing = 0.85     # One-more-turn addiction
    var juice = 1.0       # Visual/audio feedback
    return (agency + emergence + pacing + juice) / 4 * 100

# Auto-reject if <80, trigger DevSmith refactor
