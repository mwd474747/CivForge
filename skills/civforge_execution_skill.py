"""
CivForge execution skill metadata (lane v2).

Grok swarm: grok.com planning only.
Cursor: local executor on Mac Studio.
"""

SKILL = {
    "name": "civforge_execution",
    "version": "2.0",
    "lanes": {
        "grok_swarm": {"runtime": "grok.com", "executes": False},
        "cursor": {"runtime": "cursor_ide", "executes": True},
        "openclaw": {"runtime": "wt", "executes": "escalation_only"},
    },
    "drivers": {
        "cli": "tools/civforge_cli.py",
        "bridge": "bridge/civforge_http_bridge.py",
        "turnkey": "tools/turnkey-cursor-local.sh",
        "handoff": "prompts/grok_swarm_handoff_seed.md",
    },
    "rules": [
        "Read docs/EXECUTION_LANE_V2.md first",
        "Grok swarm does not run local terminal",
        "Cursor writes cursor-execution receipts with git HEAD",
        "OpenClaw only for wt escalation (OPENCLAW_ESCALATION_PACKET_V1.md)",
        "Gravity only via tools/deploy-gravity-mosaic/deploy.sh",
        "Never civforge_cli.py status | grep vercel",
    ],
}
