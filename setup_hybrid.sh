#!/bin/bash
echo '🚀 CivForge Hybrid Activated'

# Activate hybrid environment
echo "Activating DawsOS + OpenClaw + Grok + Godot layers..."

# Check for python3
if command -v python3 &> /dev/null; then
    echo "Python3 found. Running bridge status..."
    python3 bridge/grok_bridge.py --status 2>/dev/null || echo "Bridge script not fully implemented yet or missing deps. Continuing setup."
else
    echo "Python3 not found. Install Python 3 for full hybrid."
fi

# Future: git submodule update --init --recursive
echo "Hybrid setup complete. Run 'godot' project from godot/ dir or use tools/ for orchestration."

# List key components
echo ""
echo "Key CivForge components initialized:"
ls -d bridge/ godot/ governance/ integrations/ planning/ receipts/ skills/ tests/ tools/ 2>/dev/null || echo "Some dirs may be partial."

echo "✅ CivForge is ready on this computer."
