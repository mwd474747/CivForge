#!/bin/bash
# Deprecated alias — use tools/turnkey-cursor-local.sh (lane v2).
echo "NOTE: turnkey-grok-play.sh is deprecated. Use: bash tools/turnkey-cursor-local.sh"
exec bash "$(dirname "$0")/turnkey-cursor-local.sh" "$@"
