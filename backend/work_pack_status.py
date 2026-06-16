"""Work-pack registry reader for /state truth plane (anti-drift)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "config" / "work_pack_registry.yaml"


def _load_registry() -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return _load_registry_minimal()
    if not _REGISTRY_PATH.is_file():
        return {}
    data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _load_registry_minimal() -> Dict[str, Any]:
    """Fallback when PyYAML is not installed — enough for tests and basic /state."""
    if not _REGISTRY_PATH.is_file():
        return {}
    anchor_head = None
    pytest_total = None
    packs: Dict[str, Dict[str, str]] = {}
    in_work_packs = False
    current_id: Optional[str] = None
    for line in _REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("head:"):
            anchor_head = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("pytest_total:"):
            pytest_total = int(stripped.split(":", 1)[1].strip())
        elif stripped == "work_packs:":
            in_work_packs = True
            continue
        if not in_work_packs:
            continue
        if stripped.endswith(":") and not stripped.startswith("-") and " " not in stripped.rstrip(":"):
            current_id = stripped[:-1]
            packs[current_id] = {}
        elif current_id and stripped.startswith("lifecycle:"):
            packs[current_id]["lifecycle"] = stripped.split(":", 1)[1].strip()
    return {
        "anchor": {"head": anchor_head, "pytest_total": pytest_total},
        "work_packs": packs,
    }


def work_pack_status_summary() -> Dict[str, Any]:
    """Compact registry summary for /state and agent bootstrap."""
    reg = _load_registry()
    anchor = reg.get("anchor", {})
    packs: Dict[str, Any] = reg.get("work_packs", {})
    by_lifecycle: Dict[str, List[str]] = {}
    for wp_id, meta in packs.items():
        if not isinstance(meta, dict):
            continue
        life = str(meta.get("lifecycle", "unknown"))
        by_lifecycle.setdefault(life, []).append(wp_id)
    blocks = reg.get("blocks", {})
    return {
        "registry_path": str(_REGISTRY_PATH.relative_to(_REGISTRY_PATH.parent.parent)),
        "anchor_head": anchor.get("head"),
        "pytest_total_expected": anchor.get("pytest_total"),
        "truth_docs": reg.get("truth_docs", {}),
        "blocks": {
            k: {"status": v.get("status"), "closure_receipt": v.get("closure_receipt")}
            for k, v in blocks.items()
            if isinstance(v, dict)
        },
        "lifecycle_counts": {k: len(v) for k, v in by_lifecycle.items()},
        "next_planning": [
            wp_id
            for wp_id, meta in packs.items()
            if isinstance(meta, dict) and meta.get("lifecycle") == "planning"
        ],
        "closed_block_a": blocks.get("block_a", {}).get("status") == "closed",
        "closed_block_b": blocks.get("block_b", {}).get("status") == "closed",
        "closed_block_c": blocks.get("block_c", {}).get("status") == "closed",
        "closed_block_d": blocks.get("block_d", {}).get("status") == "closed",
        "grok_handoff_pack": reg.get("truth_docs", {}).get("grok_handoff_pack"),
    }
