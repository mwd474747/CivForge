"""Read-only CivStudy reference metadata (no live corpus — SEPARATION.md)."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.civstudy_corpus_cards import default_adjacency_bonuses, default_corpus_cards


def default_districts() -> List[Dict[str, Any]]:
    return [
        {
            "id": "governance-quarter",
            "name": "Governance Quarter",
            "specialization": "receipt_audit",
            "yield_bonus": {"verify_budget": 1, "influence": 1},
            "note": "Boosts verification and cross-faction receipts",
        },
        {
            "id": "systems-forge",
            "name": "Systems Forge",
            "specialization": "production_guild",
            "yield_bonus": {"prod": 2, "sci": 1},
            "note": "Harper-aligned production and integration lane",
        },
        {
            "id": "diplomatic-embassy",
            "name": "Diplomatic Embassy",
            "specialization": "negotiation_hub",
            "yield_bonus": {"influence": 2},
            "note": "Aris-aligned negotiation throughput",
        },
        {
            "id": "research-campus",
            "name": "Research Campus",
            "specialization": "discovery_lab",
            "yield_bonus": {"sci": 2},
            "note": "Lysander-aligned science and fork unlocks",
        },
    ]


def default_policy_tree() -> Dict[str, Any]:
    return {
        "branches": [
            {
                "id": "diplomacy",
                "name": "Diplomacy",
                "policies": [
                    {"id": "open_negotiation", "tier": 1, "effect": "Extra negotiation slot per 4 turns"},
                    {"id": "alliance_cap_3", "tier": 2, "effect": "Raise active alliance soft cap"},
                    {
                        "id": "envoy_network",
                        "tier": 2,
                        "effect": "Diplomatic outpost network: softer betrayal drift, lower break risk",
                        "influence_cost": 12,
                    },
                    {
                        "id": "shared_intel",
                        "tier": 2,
                        "effect": "Shared intel network: +25% negotiation success when active",
                        "influence_cost": 10,
                    },
                    {"id": "betrayal_watch", "tier": 3, "effect": "Surface betrayal risk in HUD"},
                ],
            },
            {
                "id": "economy",
                "name": "Economy",
                "policies": [
                    {"id": "institution_charter", "tier": 1, "effect": "+1 economic institution every 4 turns"},
                    {"id": "trade_route_map", "tier": 2, "effect": "Unlock sci-trade yield bonus"},
                    {"id": "yield_surge", "tier": 3, "effect": "+5% lane yield bonus"},
                ],
            },
            {
                "id": "culture",
                "name": "Culture",
                "policies": [
                    {"id": "symposium_chain", "tier": 1, "effect": "Start cultural event chains earlier"},
                    {"id": "influence_spread", "tier": 2, "effect": "+2 influence spread per 6 turns"},
                    {"id": "festival_receipts", "tier": 3, "effect": "Cultural milestones boost victory +2"},
                ],
            },
        ]
    }


def default_discovery_forks() -> List[Dict[str, Any]]:
    return [
        {
            "id": "sci-trade-route",
            "name": "Sci-Trade Route",
            "prereq": {"sci": 8, "prod": 6},
            "unlocks": "economic_institution_boost",
            "branch": "economy",
        },
        {
            "id": "receipt-quorum",
            "name": "Receipt Quorum",
            "prereq": {"verify_budget": 7},
            "unlocks": "governance_quorum_milestone_hint",
            "branch": "diplomacy",
        },
        {
            "id": "legacy-doctrine",
            "name": "Legacy Doctrine",
            "prereq": {"military_strength": 45},
            "unlocks": "military_legacy_accelerator",
            "branch": "military",
        },
        {
            "id": "cross-faction-symposium",
            "name": "Cross-Faction Symposium",
            "prereq": {"influence_spread": 15},
            "unlocks": "cultural_event_chain_bonus",
            "branch": "culture",
        },
    ]


def default_cultural_event_chains() -> List[Dict[str, Any]]:
    return [
        {
            "id": "festival-of-receipts",
            "name": "Festival of Receipts",
            "stages": ["gather_proofs", "audit_quorum", "celebrate_milestone"],
            "influence_reward": 3,
            "victory_bonus": 2,
        },
        {
            "id": "symposium-of-systems",
            "name": "Symposium of Systems",
            "stages": ["harper_keynote", "integration_demo", "shared_map_blessing"],
            "influence_reward": 4,
            "victory_bonus": 3,
        },
        {
            "id": "archivist-pilgrimage",
            "name": "Archivist Pilgrimage",
            "stages": ["corpus_map", "citation_audit", "reference_panel_unlock"],
            "influence_reward": 2,
            "sci_reward": 2,
        },
    ]


def civstudy_reference_panel() -> Dict[str, Any]:
    """Read-only civstudy pattern hints for dashboard and agent-play."""
    return {
        "status": "read_only_reference",
        "repo": "mwd474747/civstudy",
        "note": "Metadata reference lane — patterns from CIVSTUDY-TERMINAL-GIT-REVIEW. Not live corpus — SEPARATION.md.",
        "agents": [
            {"role": "Research Lead", "focus": "scope, corpus map, success criteria"},
            {"role": "Archivist", "focus": "provenance, references.json, citation audit"},
            {"role": "Editor", "focus": "structure, cross-links, coherence"},
            {"role": "Web Developer", "focus": "registry routes, Recharts viz, dark glass UI"},
        ],
        "borrowed_patterns": [
            "Card-based admin HUD + budget bars",
            "Discrete task runners with loading feedback",
            "Empire Council session records (receipt chronicles)",
            "Governor entity management metaphors",
        ],
        "corpus_cards": default_corpus_cards(),
        "adjacency_bonuses": default_adjacency_bonuses(),
        "districts": default_districts(),
        "policy_tree": default_policy_tree(),
        "discovery_forks": default_discovery_forks(),
        "cultural_event_chains": default_cultural_event_chains(),
    }
