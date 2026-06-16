"""CivStudy reference corpus cards — read-only flavor depth (WP-GROK-AUTHENTIC-AUDIT-003)."""

from __future__ import annotations

from typing import Any, Dict, List


def default_corpus_cards() -> List[Dict[str, Any]]:
    """Twelve CivStudy corpus cards for dashboard reference and agent-play tone."""
    return [
        {
            "id": "district-campus",
            "kind": "district",
            "name": "Campus",
            "flavor": "Scholars chart the stars and unlock breakthroughs for the realm.",
            "yields": {"sci": 2, "influence": 1},
            "adjacency_hint": "Mountains sharpen research; jungles slow construction.",
        },
        {
            "id": "district-holy-site",
            "kind": "district",
            "name": "Holy Site",
            "flavor": "Faith spreads through pilgrims and sacred rites.",
            "yields": {"influence": 2, "verify_budget": 1},
            "adjacency_hint": "Forests and mountains amplify devotion.",
        },
        {
            "id": "district-commercial-hub",
            "kind": "district",
            "name": "Commercial Hub",
            "flavor": "Merchants weave trade routes that enrich the treasury.",
            "yields": {"prod": 2, "influence": 1},
            "adjacency_hint": "River Trade Bonus when placed along waterways.",
        },
        {
            "id": "district-encampment",
            "kind": "district",
            "name": "Encampment",
            "flavor": "Veterans drill recruits and garrison the frontier.",
            "yields": {"prod": 1, "military_strength": 2},
            "adjacency_hint": "Mountain Fortress synergy on high ground.",
        },
        {
            "id": "district-theater-square",
            "kind": "district",
            "name": "Theater Square",
            "flavor": "Bards and architects celebrate the glory of your people.",
            "yields": {"influence": 2, "cultural_chains": 1},
            "adjacency_hint": "Wonders and districts amplify cultural output.",
        },
        {
            "id": "district-industrial-zone",
            "kind": "district",
            "name": "Industrial Zone",
            "flavor": "Forges and workshops drive production for wonders and armies.",
            "yields": {"prod": 3},
            "adjacency_hint": "Quarry and mine tiles boost yield.",
        },
        {
            "id": "wonder-pyramids",
            "kind": "wonder",
            "name": "Pyramids",
            "flavor": "A monument to eternity — production legacy for generations.",
            "effect": "Permanent +15% build speed empire-wide; legacy points +2 on completion.",
            "influence_cost": 14,
        },
        {
            "id": "wonder-great-wall",
            "kind": "wonder",
            "name": "Great Wall",
            "flavor": "Stone sentinels guard the border against raiders.",
            "effect": "Border tiles gain +4 defense; betrayal risk on frontier alliances −10%.",
            "influence_cost": 12,
        },
        {
            "id": "wonder-oracle",
            "kind": "wonder",
            "name": "Oracle",
            "flavor": "Priests divine the will of the gods and inspire the masses.",
            "effect": "Cultural event chains start one turn earlier; influence spread +3.",
            "influence_cost": 10,
        },
        {
            "id": "policy-classical-governments",
            "kind": "policy",
            "name": "Classical Governments",
            "flavor": "Four paths of rule shape how your empire grows.",
            "policies": [
                {"id": "tradition", "effect": "Heritage bonus — cultural milestones arrive sooner."},
                {"id": "liberty", "effect": "Free citizens — extra influence from settled tiles."},
                {"id": "oligarchy", "effect": "Merchant princes — trade route yields +10%."},
                {"id": "republic", "effect": "Senate quorum — negotiation success +5% with city-states."},
            ],
        },
        {
            "id": "unit-promotion-warrior-knight",
            "kind": "unit_line",
            "name": "Warrior → Swordsman → Knight",
            "flavor": "The line of battle evolves from levy spears to armored knights.",
            "promotions": [
                {"from": "Warrior", "to": "Swordsman", "requires": "Iron Working"},
                {"from": "Swordsman", "to": "Knight", "requires": "Chivalry"},
            ],
        },
        {
            "id": "strategic-corridors",
            "kind": "strategic",
            "name": "Victory Paths & Trade Corridors",
            "flavor": "Empires rise through culture, science, steel, and caravans.",
            "victory_paths": [
                {"id": "cultural_prestige", "name": "Cultural Prestige", "goal": "Dominate rival minds through festivals and wonders."},
                {"id": "science_dominance", "name": "Science Dominance", "goal": "Lead the world in discovery and innovation."},
                {"id": "military_conquest", "name": "Military Conquest", "goal": "Subdue rival city-states and hold the map."},
            ],
            "trade_route": {
                "name": "Caravan Formation",
                "flavor": "Link two cities across rivers or plains for adjacency yield.",
                "bonus": "River Trade Bonus: +1 sci and +1 prod when route crosses water.",
            },
            "cultural_chain": {
                "name": "Legacy Festival Chain",
                "flavor": "A three-stage celebration that leaves a permanent legacy modifier.",
                "stages": ["Gather artisans", "Grand procession", "Eternal chronicle (+2 legacy)"],
            },
        },
    ]


def default_adjacency_bonuses() -> List[Dict[str, Any]]:
    """Adjacency synergy flavor for map and CivStudy reference."""
    return [
        {
            "id": "river_trade_bonus",
            "name": "River Trade Bonus",
            "flavor": "Settlements along rivers gain +1 trade yield and faster caravan formation.",
        },
        {
            "id": "mountain_fortress",
            "name": "Mountain Fortress",
            "flavor": "Encampments on high ground gain +2 defense and slower betrayal drift.",
        },
        {
            "id": "coastal_harbor",
            "name": "Coastal Harbor",
            "flavor": "Commercial hubs beside coast tiles unlock overseas trade routes.",
        },
    ]
