"""Military / conflict / defeat review inventory + multi-round simulation block.

WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001 — Cursor executes review + sim; Grok PRIME stays planning
until linked to this execution receipt.
"""

from __future__ import annotations

import json
import random
import re
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from backend.game_actions import player_cycle_decision
from backend.game_reset import build_initial_game_state
from backend.game_session import session_phase
from backend.multi_agent_state import AGENT_IDS
from backend.turn_simulation import enrich_cycle_receipt, run_turn_simulation
from core.mechanics_registry import build_default_registry
from core.orchestrator import GovernanceOrchestrator
from core.swarm_join import FORGE_COORDINATOR_ID

WORK_PACK_ID = "WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001"

REVIEW_INVENTORY: Dict[str, Any] = {
    "military_legacy_chains": {
        "wired": True,
        "paths": [
            "core/mechanics_registry.py::_tick_military (legacy_points every 5 turns)",
            "backend/civstudy_mechanics_bridge.py::legacy-doctrine fork (+1 legacy)",
            "backend/civstudy_metadata.py::military_legacy_accelerator unlock",
        ],
        "note": "CivStudy 'Warrior promotion' maps to military strength drift + legacy_points, not a separate Warrior unit.",
    },
    "conflict_triggers": {
        "wired": True,
        "paths": [
            "backend/multi_agent_state.py::contested tile capture (turn % 3)",
            "core/swarm_join.py::detect_delegate_conflict (orchestrator deploy vs verify)",
            "backend/multi_agent_state.py::betrayal break events",
        ],
    },
    "defeat_cascades": {
        "wired": True,
        "reasons": ["fun_floor", "diplomatic_isolation", "betrayal_collapse", "stalled_progress"],
        "paths": [
            "backend/game_session.py::check_defeat_conditions",
            "backend/turn_simulation.py::maybe_emit_defeat_receipt",
        ],
        "note": "No explicit bankruptcy cascade — fun_floor and stalled_progress cover resource/pacing collapse.",
    },
    "diplomacy_betrayal": {
        "wired": True,
        "paths": [
            "backend/multi_agent_state.py::betrayal risk drift + BETRAYAL break",
            "backend/game_session.py::betrayal_watch policy (12% break/turn at risk ≥55)",
            "backend/multi_agent_state.py::envoy_network softening (drift cap + 7% break odds)",
        ],
    },
    "alliance_stability": {
        "wired": True,
        "paths": [
            "backend/game_session.py::alliance_soft_cap (2 default, 3 with alliance_cap_3)",
            "backend/multi_agent_state.py::respond_negotiation forms alliances",
            "backend/multi_agent_state.py::player alliance progress penalty on betrayal",
        ],
    },
    "agents": list(AGENT_IDS),
}

EVENT_PATTERNS: Dict[str, re.Pattern[str]] = {
    "betrayal": re.compile(r"BETRAYAL|betrayal risk elevated", re.I),
    "map_conflict": re.compile(r"now held by", re.I),
    "military_legacy": re.compile(r"Military legacy point", re.I),
    "defeat": re.compile(r"Defeat —", re.I),
    "milestone": re.compile(r"Milestone unlocked", re.I),
    "negotiation": re.compile(r"opened negotiation|Negotiation .* accepted", re.I),
    "delegate_conflict": re.compile(r"delegate_conflict", re.I),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extract_metrics(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Snapshot military / conflict / defeat fields for /state parity."""
    vp = game_state.get("victory_progress", {})
    mil = game_state.get("mechanics_lanes", {}).get("military", {})
    alliances = game_state.get("alliances", [])
    broken = sum(1 for a in alliances if a.get("status") == "broken")
    active = sum(1 for a in alliances if a.get("status") in ("active", "provisional"))
    max_risk = max((a.get("betrayal_risk", 0) for a in alliances), default=0)
    contested = sum(1 for t in game_state.get("map_tiles", []) if t.get("owner") == "contested")
    return {
        "turn": game_state.get("turn"),
        "session_phase": session_phase(game_state),
        "fun_score": game_state.get("player", {}).get("fun_score"),
        "military_strength": mil.get("strength"),
        "military_legacy_points": mil.get("legacy_points"),
        "military_garrisons": mil.get("garrisons"),
        "alliances_active": active,
        "alliances_broken": broken,
        "max_betrayal_risk": max_risk,
        "contested_tiles": contested,
        "joint_progress": vp.get("joint_progress"),
        "outcome": vp.get("outcome"),
        "defeat_reason": vp.get("defeat_reason"),
        "milestones_done": sum(1 for m in vp.get("milestones", []) if m.get("done")),
        "unlocked_policies": list(
            game_state.get("civstudy_sim", {}).get("policy_tree", {}).get("unlocked", [])
        ),
        "unlocked_forks": list(game_state.get("civstudy_sim", {}).get("unlocked_forks", [])),
    }


def classify_events(events: List[str]) -> Dict[str, int]:
    counts = {key: 0 for key in EVENT_PATTERNS}
    for event in events:
        for key, pattern in EVENT_PATTERNS.items():
            if pattern.search(event):
                counts[key] += 1
    return counts


def _new_orchestrator() -> GovernanceOrchestrator:
    orch = GovernanceOrchestrator()
    orch.register_agent("harper", "Harper (Systems)")
    orch.register_agent("sebastian", "Sebastian (Governance)")
    orch.register_agent(FORGE_COORDINATOR_ID, "Forge Coordinator")
    return orch


def _advance_one_cycle(
    game_state: Dict[str, Any],
    orchestrator: GovernanceOrchestrator,
    registry: Any,
) -> Tuple[bool, List[str]]:
    """One governance cycle (mirrors advance_turn game sim, no disk I/O)."""
    if session_phase(game_state) != "active":
        return False, []

    result = orchestrator.advance_cycle(player_actions=1)
    player_line = player_cycle_decision(game_state, 1)
    result["receipt"].setdefault("decisions", {})["player"] = player_line

    game_state["turn"] = result["turn"]
    game_state["player"]["fun_score"] = result["fun_score"]
    for key in ["food", "prod", "sci", "influence", "verify_budget"]:
        if key in game_state["player"]["resources"]:
            game_state["player"]["resources"][key] += 1

    receipt = enrich_cycle_receipt(result["receipt"], game_state)
    new_events = list(result.get("events", []))
    new_events.extend(run_turn_simulation(game_state, registry, receipt.get("decisions", {})))
    game_state.setdefault("events", []).extend(new_events)
    if result["receipt"].get("delegate_conflict"):
        game_state["events"].append(
            f"Turn {game_state['turn']}: Orchestrator delegate_conflict detected."
        )
    return True, new_events


def run_local_simulation(
    *,
    rounds: int = 50,
    seed: Optional[int] = 42,
    defeat_seed: bool = False,
) -> Dict[str, Any]:
    """In-process multi-round block with 5 agents (deterministic when seed set)."""
    if seed is not None:
        random.seed(seed)

    game_state = build_initial_game_state()
    if defeat_seed:
        from backend.game_reset import apply_defeat_cascade_seed

        apply_defeat_cascade_seed(game_state)
    orchestrator = _new_orchestrator()
    registry = build_default_registry()
    round_log: List[Dict[str, Any]] = []
    all_new_events: List[str] = []
    stopped_early = False
    stop_reason: Optional[str] = None

    for rnd in range(1, rounds + 1):
        ok, events = _advance_one_cycle(game_state, orchestrator, registry)
        if not ok:
            stopped_early = True
            stop_reason = session_phase(game_state)
            break
        all_new_events.extend(events)
        if rnd in (1, 10, 25, 50) or rnd == rounds:
            round_log.append({"round": rnd, "metrics": extract_metrics(game_state)})

    if not stopped_early and round_log and round_log[-1]["round"] != rounds:
        round_log.append({"round": game_state["turn"], "metrics": extract_metrics(game_state)})

    return {
        "work_pack_id": WORK_PACK_ID,
        "mode": "local",
        "generated_at": utc_now(),
        "rounds_requested": rounds,
        "rounds_completed": game_state.get("turn", 1) - 1,
        "stopped_early": stopped_early,
        "stop_reason": stop_reason,
        "review_inventory": REVIEW_INVENTORY,
        "event_counts": classify_events(all_new_events),
        "sample_events": all_new_events[-12:],
        "round_snapshots": round_log,
        "final_metrics": extract_metrics(game_state),
        "agents": list(AGENT_IDS),
    }


def _kernel_post(base: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        f"{base.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _kernel_get(base: str, path: str) -> Dict[str, Any]:
    with urllib.request.urlopen(f"{base.rstrip('/')}{path}", timeout=15) as resp:
        return json.loads(resp.read())


def run_kernel_simulation(
    *,
    kernel_url: str = "http://127.0.0.1:8080",
    rounds: int = 50,
) -> Dict[str, Any]:
    """Live :8080 block — reset, advance, poll /state."""
    _kernel_post(kernel_url, "/game/reset", {})
    round_log: List[Dict[str, Any]] = []
    stopped_early = False
    stop_reason: Optional[str] = None
    completed = 0
    delegate_conflicts = 0

    for rnd in range(1, rounds + 1):
        try:
            adv = _kernel_post(kernel_url, "/advance_turn", {})
        except urllib.error.HTTPError as exc:
            if exc.code == 409:
                stopped_early = True
                stop_reason = exc.read().decode(errors="replace")[:200]
                break
            raise
        completed = rnd
        receipt = adv.get("receipt") or {}
        if receipt.get("delegate_conflict"):
            delegate_conflicts += 1
        if rnd in (1, 10, 25, 50):
            state = _kernel_get(kernel_url, "/state")
            round_log.append({
                "round": rnd,
                "metrics": extract_metrics_from_api_state(state),
            })

    final_state = _kernel_get(kernel_url, "/state")
    recent = final_state.get("recent_events") or []

    return {
        "work_pack_id": WORK_PACK_ID,
        "mode": "kernel",
        "kernel_url": kernel_url,
        "generated_at": utc_now(),
        "rounds_requested": rounds,
        "rounds_completed": completed,
        "stopped_early": stopped_early,
        "stop_reason": stop_reason,
        "delegate_conflicts": delegate_conflicts,
        "review_inventory": REVIEW_INVENTORY,
        "event_counts": classify_events(recent),
        "sample_events": recent[-12:],
        "round_snapshots": round_log,
        "final_metrics": extract_metrics_from_api_state(final_state),
        "agents": list(AGENT_IDS),
    }


def run_kernel_defeat_simulation(
    *,
    kernel_url: str = "http://127.0.0.1:8080",
    max_rounds: int = 15,
) -> Dict[str, Any]:
    """Kernel defeat-cascade seed + advance until defeat epilogue (WP-GROK-SIM-DEFEAT-CASCADE-002)."""
    from pathlib import Path

    receipts_before = set((Path(__file__).resolve().parent.parent / "receipts").glob("defeat-outcome-*.md"))
    _kernel_post(kernel_url, "/game/reset", {"seed_profile": "defeat_cascade"})
    state = _kernel_get(kernel_url, "/state")
    if state.get("session_phase") == "defeat":
        completed = 0
        stopped_early = True
        stop_reason = "defeat_on_seed"
    else:
        completed = 0
        stopped_early = False
        stop_reason = None

        for rnd in range(1, max_rounds + 1):
            try:
                _kernel_post(kernel_url, "/advance_turn", {})
            except urllib.error.HTTPError as exc:
                if exc.code == 409:
                    stopped_early = True
                    stop_reason = exc.read().decode(errors="replace")[:200]
                    break
                raise
            completed = rnd
            state = _kernel_get(kernel_url, "/state")
            if state.get("session_phase") == "defeat":
                stopped_early = True
                stop_reason = "defeat"
                break

    final_state = _kernel_get(kernel_url, "/state")
    receipts_after = set((Path(__file__).resolve().parent.parent / "receipts").glob("defeat-outcome-*.md"))
    new_receipts = sorted(str(p.name) for p in receipts_after - receipts_before)

    return {
        "work_pack_id": "WP-GROK-SIM-DEFEAT-CASCADE-002",
        "mode": "kernel_defeat",
        "kernel_url": kernel_url,
        "generated_at": utc_now(),
        "rounds_completed": completed,
        "stopped_early": stopped_early,
        "stop_reason": stop_reason,
        "defeat_outcome_receipts": new_receipts,
        "final_metrics": extract_metrics_from_api_state(final_state),
        "sample_events": (final_state.get("recent_events") or [])[-8:],
    }


def extract_metrics_from_api_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Map GET /state response to review metrics."""
    gs = {
        "turn": state.get("current_turn", state.get("turn")),
        "player": state.get("player", {}),
        "mechanics_lanes": state.get("mechanics_lanes", {}),
        "alliances": state.get("alliances", []),
        "map_tiles": state.get("map_tiles", []),
        "victory_progress": state.get("victory_progress", {}),
        "civstudy_sim": state.get("civstudy_sim", {}),
    }
    gs["session_phase"] = state.get("session_phase")
    metrics = extract_metrics(gs)
    metrics["session_phase"] = state.get("session_phase", metrics.get("session_phase"))
    return metrics


def write_sim_artifacts(result: Dict[str, Any], receipts_dir: Any) -> Tuple[Any, Any]:
    """Write JSON + markdown summary under receipts/."""
    from pathlib import Path

    root = Path(receipts_dir)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    json_path = root / f"military-conflict-defeat-sim-{stamp}.json"
    md_path = root / f"military-conflict-defeat-sim-{stamp}.md"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    fm = result.get("final_metrics", {})
    ec = result.get("event_counts", {})
    lines = [
        f"# Military / Conflict / Defeat Simulation — {WORK_PACK_ID}",
        "",
        f"**Generated:** {result.get('generated_at')}",
        f"**Mode:** {result.get('mode')}",
        f"**Rounds:** {result.get('rounds_completed')}/{result.get('rounds_requested')}",
        "",
        "## Final metrics",
        "",
        f"- session_phase: **{fm.get('session_phase')}**",
        f"- military: strength {fm.get('military_strength')}, legacy {fm.get('military_legacy_points')}",
        f"- alliances: {fm.get('alliances_active')} active, {fm.get('alliances_broken')} broken, max risk {fm.get('max_betrayal_risk')}%",
        f"- victory: progress {fm.get('joint_progress')}, outcome {fm.get('outcome')}, defeat_reason {fm.get('defeat_reason')}",
        "",
        "## Event counts (sample window)",
        "",
    ]
    for k, v in sorted(ec.items()):
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Sample events", ""])
    for ev in result.get("sample_events", []):
        lines.append(f"- {ev}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
