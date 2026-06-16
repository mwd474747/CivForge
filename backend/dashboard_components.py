"""Dashboard component registry — tab/panel extensibility metadata."""

from __future__ import annotations

from typing import Any, Dict, List

DEFAULT_COMPONENTS: List[Dict[str, Any]] = [
    {"id": "overview", "kind": "tab", "label": "Overview", "view": "overview"},
    {"id": "military", "kind": "tab", "label": "Military", "view": "military"},
    {"id": "economic", "kind": "tab", "label": "Economic", "view": "economic"},
    {"id": "cultural", "kind": "tab", "label": "Cultural", "view": "cultural"},
    {"id": "founding", "kind": "tab", "label": "Found City", "view": "founding"},
    {"id": "civstudy", "kind": "tab", "label": "CivStudy Ref", "view": "civstudy"},
    {"id": "mechanics", "kind": "tab", "label": "Council Proposals", "view": "mechanics"},
    {"id": "agent_control", "kind": "panel", "label": "Agent Control", "view": "overview", "anchor": "agent-control-panel"},
    {"id": "competition", "kind": "panel", "label": "Competition Mode", "view": "overview", "anchor": "competition-panel"},
    {"id": "spectator", "kind": "panel", "label": "Spectator Log", "view": "overview", "anchor": "spectator-log"},
]


class DashboardComponentRegistry:
    def __init__(self) -> None:
        self._components: Dict[str, Dict[str, Any]] = {
            c["id"]: dict(c) for c in DEFAULT_COMPONENTS
        }

    def register(self, component: Dict[str, Any]) -> None:
        self._components[component["id"]] = component

    def all_components(self) -> List[Dict[str, Any]]:
        return list(self._components.values())

    def tabs(self) -> List[Dict[str, Any]]:
        return [c for c in self._components.values() if c.get("kind") == "tab"]

    def panels(self) -> List[Dict[str, Any]]:
        return [c for c in self._components.values() if c.get("kind") == "panel"]


def get_dashboard_registry() -> DashboardComponentRegistry:
    return DashboardComponentRegistry()
