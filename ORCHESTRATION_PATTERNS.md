# CivForge Autonomous Agent Orchestration v1.0

## Core Patterns
- **Master Work Pack Executor**: Single entry for any objective
- **Godot Agent Brain Pattern**: Each NPC/Faction has embedded receipt memory + goal stack
- **Swarm Coordination**: Grok spawns specialist agents per subsystem (Economy, Diplomacy, Tech Tree, Combat, etc.)
- **Continuous Integration Loop**: Auto test scenes, balance sim runs, push fixes
- **Autonomous Operation Mode**: Game can run headless with Grok steering via bridge for full playtesting and development

**Immediate Implementation Priority**:
1. Core agent brain GDScript
2. Turn-based simulation runner with receipts
3. Visual HUD for agent decisions
4. Test suite bootstrap
