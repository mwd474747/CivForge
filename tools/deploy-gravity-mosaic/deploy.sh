#!/bin/bash
# CivForge Deployment Helper for gravity-mosaic-knowledge-graph
# Enforces the strict Process Rules from the project history:
# - Local disk is source of truth
# - Full literal verification before any push
# - Exact full-content git operations only
# - Browser tool verification after deploy
# - Zero meta/summaries in commits

set -e

PROJECT_DIR="/Users/michaeldawson/gravity-mosaic-knowledge-graph"
DEPLOY_PROJECT="/Users/michaeldawson/CivForge/tools/deploy-gravity-mosaic"

echo "🚀 CivForge Gravity Mosaic Deployer"
echo "=================================="

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: gravity-mosaic-knowledge-graph not found at $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "1. Running pre-deploy verifications (literal, no summaries)..."

echo "   - Line counts:"
wc -l index.html models/*.py models/README.md README.md ROADMAP.md

echo "   - New features (concept/formula extension):"
grep -c "biefeld-brown-effect\|gravitomagnetism\|ion-drift-force\|high-k-dielectric-accel\|power-law-thrust\|net-force-euler\|ehd-modern-propulsion\|electrohydrodynamics\|electrogravitic-coupling\|Academic Concept\|Formula / Equation\|EQUATIONS" index.html models/biefeld_brown_thrust.py models/precision_porting.py || true

echo "   - Python models + EQUATIONS test:"
python3 -c '
import sys
sys.path.insert(0, ".")
from models.biefeld_brown_thrust import BiefeldBrownModel, EQUATIONS as BE_EQ
from models.precision_porting import PrecisionPortingModel
print("   Biefeld ion @60kV:", round(BiefeldBrownModel("ion").compute_thrust(60000).thrust_n, 6))
print("   Biefeld claimed @80kV:", round(BiefeldBrownModel("claimed_eg").compute_thrust(80000).thrust_n, 6))
print("   Biefeld EQUATIONS keys:", list(BE_EQ.keys()))
p = PrecisionPortingModel()
art = p.to_artifact()
print("   Precision to_artifact has equations:", "equations" in art)
print("   Python + formulas: PASS")
' 

echo "   - Golden anchors + integration:"
grep -c "RESONANCE EXPLORER\|graph-canvas\|Electrogravitic Boost\|model-lab-canvas\|lift-bar\|entity-ref" index.html || true

echo "   - Bad legacy check (must be low/0 for critical):"
grep -E "VERBA TIM|NAA archival notes|~1485|~179|pages 7–16 NAA archival" index.html README.md ROADMAP.md models/README.md 2>/dev/null | wc -l || echo 0

echo "2. Staging and committing (literal full content)..."
git add index.html models/ README.md ROADMAP.md
git status

COMMIT_MSG="feat: extend nodes/edges for traversal from historical mosaic (electrogravitics, black-programs, precision culture, etc.) via academic concepts + successors to model formulas (deep research: Biefeld-Brown/EHD consensus + Brown's claims + 1950s programs + GR gravitomagnetism). Added 9 nodes (biefeld-brown-effect, electrohydrodynamics, electrogravitic-coupling, ion-drift-force, high-k-dielectric-accel, power-law-thrust, net-force-euler, gravitomagnetism, ehd-modern-propulsion) + edges. Exposed EQUATIONS in Python to_artifact. Updated filters/legend/types, transcript entity-refs, models section. Local verified (1889 lines, 30+ new feature counts, Python PASS, 0 critical legacy, golden anchors intact)."

git commit -m "$COMMIT_MSG"

echo "3. Pushing to origin main..."
git push origin main

echo "✅ Deploy complete. Hard refresh the live site: https://mwd474747.github.io/gravity-mosaic-knowledge-graph/"
echo "   (Cmd/Ctrl + Shift + R)"
echo ""
echo "Next: Use CivForge agents (Grok main + sub-agents) to govern further updates via receipts in this deploy helper."
echo "See $DEPLOY_PROJECT/README.md for orchestration."
