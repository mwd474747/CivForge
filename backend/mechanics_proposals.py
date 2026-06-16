"""Governed mechanics proposal lane — Grok swarm proposes, FunForge gates, kernel applies runtime patches.

Simulation-only tools (advance_turn, what_if) tick existing modules. This lane lets agents
propose mechanic parameter changes and metadata overrides that apply to live game_state
after FunForge approval. Code-level tick modules still require Cursor execution (code_change kind).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core import FunForge

MIN_FUN_FOR_APPLY = 78.0

# Runtime-applicable kinds (no git deploy)
RUNTIME_KINDS = frozenset({
    "lane_param",
    "district_yield_override",
    "tick_cadence_override",
    "param_override",
})

# Planning-only kinds (Grok authors WP → Cursor implements)
PLANNING_KINDS = frozenset({
    "code_change",
    "policy_definition",
    "fork_definition",
    "tick_module",
})

VALID_KINDS = RUNTIME_KINDS | PLANNING_KINDS


def default_mechanics_overrides() -> Dict[str, Any]:
    return {
        "lane_params": {},
        "district_yields": {},
        "cultural_cadence": None,
        "session_params": {},
    }


def ensure_mechanics_state(game_state: Dict[str, Any]) -> Dict[str, Any]:
    proposals = game_state.setdefault("mechanics_proposals", [])
    if not isinstance(proposals, list):
        game_state["mechanics_proposals"] = []
    overrides = game_state.setdefault("mechanics_overrides", default_mechanics_overrides())
    for key, default in default_mechanics_overrides().items():
        overrides.setdefault(key, default if not isinstance(default, dict) else {})
    return overrides


def proposals_summary(game_state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_mechanics_state(game_state)
    items = game_state.get("mechanics_proposals", [])
    by_status: Dict[str, int] = {}
    for item in items:
        status = str(item.get("status", "PROPOSED"))
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "total": len(items),
        "by_status": by_status,
        "pending_runtime": sum(
            1 for i in items
            if i.get("status") == "GATED_APPROVED" and i.get("kind") in RUNTIME_KINDS
        ),
        "recent": items[-6:],
    }


def _validate_payload(kind: str, payload: Dict[str, Any]) -> Optional[str]:
    if kind == "lane_param":
        if not payload.get("lane"):
            return "lane_param requires lane"
        if not isinstance(payload.get("params"), dict) or not payload["params"]:
            return "lane_param requires non-empty params dict"
    elif kind == "district_yield_override":
        if not payload.get("district_id"):
            return "district_yield_override requires district_id"
        if not isinstance(payload.get("yield_bonus"), dict):
            return "district_yield_override requires yield_bonus dict"
    elif kind == "tick_cadence_override":
        cadence = payload.get("cultural_cadence")
        if not isinstance(cadence, int) or cadence < 2 or cadence > 12:
            return "tick_cadence_override requires cultural_cadence int 2-12"
    elif kind == "param_override":
        allowed = {
            "trade_route_sci_bonus",
            "receipt_quorum_progress_bonus",
            "receipt_quorum_verify_min",
            "defeat_fun_floor",
            "alliance_soft_cap_default",
        }
        keys = set(payload.keys())
        if not keys or not keys <= allowed:
            return f"param_override keys must be subset of {sorted(allowed)}"
    elif kind == "policy_definition":
        for field in ("id", "branch_id", "tier", "effect"):
            if not payload.get(field):
                return f"policy_definition requires {field}"
    elif kind == "fork_definition":
        for field in ("id", "name", "prereq"):
            if field not in payload:
                return f"fork_definition requires {field}"
    elif kind == "tick_module":
        if not payload.get("module_name") or not payload.get("description"):
            return "tick_module requires module_name and description"
    elif kind == "code_change":
        if not payload.get("description"):
            return "code_change requires description"
    return None


def propose_mechanics(
    game_state: Dict[str, Any],
    *,
    kind: str,
    title: str,
    payload: Dict[str, Any],
    author: str = "grok_swarm",
    work_pack_id: str = "",
    rationale: str = "",
) -> Dict[str, Any]:
    """Create a mechanics proposal (Grok swarm planning → kernel gate → apply)."""
    ensure_mechanics_state(game_state)
    kind = kind.strip()
    if kind not in VALID_KINDS:
        return {"error": f"unknown kind {kind!r}; valid: {sorted(VALID_KINDS)}"}
    if not title.strip():
        return {"error": "title required"}

    err = _validate_payload(kind, payload or {})
    if err:
        return {"error": err}

    proposal_id = str(uuid.uuid4())[:8]
    turn = game_state.get("turn", 1)
    proposal = {
        "id": proposal_id,
        "kind": kind,
        "title": title.strip(),
        "payload": dict(payload or {}),
        "author": author,
        "work_pack_id": work_pack_id or None,
        "rationale": rationale or None,
        "turn": turn,
        "status": "PROPOSED",
        "fun_score": 0.0,
        "implementation_lane": "cursor" if kind in PLANNING_KINDS else "kernel_runtime",
        "created_at": datetime.utcnow().isoformat(),
    }
    game_state["mechanics_proposals"].append(proposal)
    game_state.setdefault("events", []).append(
        f"Turn {turn}: Mechanics proposal '{title}' ({kind}) from {author}."
    )
    return {
        "proposal": proposal,
        "message": "Proposal created. Call /game/mechanics/gate then /game/mechanics/apply for runtime kinds.",
        "next": _next_step_for_kind(kind),
    }


def _next_step_for_kind(kind: str) -> str:
    if kind in RUNTIME_KINDS:
        return "gate → apply"
    return "gate → export to Cursor WP (no kernel auto-apply)"


def gate_mechanics(
    game_state: Dict[str, Any],
    proposal_id: str,
    fun_score_override: Optional[float] = None,
) -> Dict[str, Any]:
    """FunForge quality gate for a mechanics proposal."""
    ensure_mechanics_state(game_state)
    proposal = _find_proposal(game_state, proposal_id)
    if not proposal:
        return {"error": "proposal not found"}

    if proposal["status"] not in ("PROPOSED", "GATED_REJECTED"):
        return {"error": f"proposal already {proposal['status']}"}

    fun = fun_score_override
    if fun is None:
        emergence = 0.88 if proposal["kind"] in RUNTIME_KINDS else 0.82
        fun = FunForge.calculate_fun_metrics({
            "agency": 0.9,
            "emergence": emergence,
            "pacing": 0.84,
            "juice": 0.86,
        })

    proposal["fun_score"] = fun
    if fun >= MIN_FUN_FOR_APPLY:
        proposal["status"] = "GATED_APPROVED"
        comment = FunForge.comment(fun)
        return {
            "approved": True,
            "fun_score": fun,
            "comment": comment,
            "proposal": proposal,
            "next": _next_step_for_kind(proposal["kind"]),
        }

    proposal["status"] = "GATED_REJECTED"
    return {
        "approved": False,
        "fun_score": fun,
        "comment": "Below FunForge threshold — refine proposal or add verification.",
        "proposal": proposal,
    }


def apply_mechanics(game_state: Dict[str, Any], proposal_id: str) -> Dict[str, Any]:
    """Apply a gated-approved runtime mechanics proposal to live overrides."""
    ensure_mechanics_state(game_state)
    proposal = _find_proposal(game_state, proposal_id)
    if not proposal:
        return {"error": "proposal not found"}
    if proposal["status"] != "GATED_APPROVED":
        return {"error": f"proposal must be GATED_APPROVED, got {proposal['status']}"}
    if proposal["kind"] in PLANNING_KINDS:
        return {
            "error": "planning-only kind — export to Cursor work pack; no kernel auto-apply",
            "proposal": proposal,
            "cursor_hint": f"Implement via WP referencing proposal {proposal_id}",
        }
    if proposal["status"] == "APPLIED":
        return {"error": "already applied", "proposal": proposal}

    applied, detail = _apply_runtime_patch(game_state, proposal)
    if applied:
        proposal["status"] = "APPLIED"
        proposal["applied_at"] = datetime.utcnow().isoformat()
        turn = game_state.get("turn", 1)
        game_state.setdefault("events", []).append(
            f"Turn {turn}: Applied mechanics proposal '{proposal['title']}' — {detail}."
        )
        return {"applied": True, "detail": detail, "proposal": proposal, "overrides": game_state["mechanics_overrides"]}
    return {"error": detail, "proposal": proposal}


def list_mechanics_proposals(
    game_state: Dict[str, Any],
    *,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_mechanics_state(game_state)
    items = list(game_state.get("mechanics_proposals", []))
    if status:
        items = [i for i in items if i.get("status") == status]
    return {
        "proposals": items,
        "summary": proposals_summary(game_state),
        "runtime_kinds": sorted(RUNTIME_KINDS),
        "planning_kinds": sorted(PLANNING_KINDS),
    }


def _find_proposal(game_state: Dict[str, Any], proposal_id: str) -> Optional[Dict[str, Any]]:
    for item in game_state.get("mechanics_proposals", []):
        if item.get("id") == proposal_id:
            return item
    return None


def _apply_runtime_patch(game_state: Dict[str, Any], proposal: Dict[str, Any]) -> Tuple[bool, str]:
    kind = proposal["kind"]
    payload = proposal.get("payload", {})
    overrides = ensure_mechanics_state(game_state)

    if kind == "lane_param":
        lane = payload["lane"]
        params = payload["params"]
        lane_params = overrides.setdefault("lane_params", {})
        lane_params.setdefault(lane, {}).update(params)
        lanes = game_state.setdefault("mechanics_lanes", {})
        lanes.setdefault(lane, {}).update(params)
        return True, f"lane {lane} ← {params}"

    if kind == "district_yield_override":
        did = payload["district_id"]
        bonus = payload["yield_bonus"]
        overrides.setdefault("district_yields", {})[did] = dict(bonus)
        return True, f"district {did} yield ← {bonus}"

    if kind == "tick_cadence_override":
        cadence = int(payload["cultural_cadence"])
        overrides["cultural_cadence"] = cadence
        return True, f"cultural cadence ← {cadence}"

    if kind == "param_override":
        overrides.setdefault("session_params", {}).update(payload)
        return True, f"session params ← {payload}"

    return False, f"unsupported runtime kind {kind}"


def session_param(game_state: Dict[str, Any], key: str, default: Any) -> Any:
    """Read session-level param override (applied proposals)."""
    overrides = game_state.get("mechanics_overrides", {})
    params = overrides.get("session_params", {})
    return params.get(key, default)


def district_yield_bonus(game_state: Dict[str, Any], district_id: str, base: Dict[str, int]) -> Dict[str, int]:
    """Merge base district yields with governed overrides."""
    overrides = game_state.get("mechanics_overrides", {}).get("district_yields", {})
    patch = overrides.get(district_id)
    if not patch:
        return base
    merged = dict(base)
    merged.update(patch)
    return merged
