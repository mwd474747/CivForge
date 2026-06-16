#!/usr/bin/env python3
"""WP-MILITARY-CONFLICT-DEFEAT-REVIEW-SIM-001 — review + 50-round simulation block.

Usage:
  python3 tools/military_conflict_defeat_review_sim.py --mode local
  python3 tools/military_conflict_defeat_review_sim.py --mode kernel --rounds 50
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.military_conflict_defeat_review import (  # noqa: E402
    run_kernel_simulation,
    run_local_simulation,
    write_sim_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Military/conflict/defeat review simulation block")
    parser.add_argument("--mode", choices=("local", "kernel"), default="kernel")
    parser.add_argument("--rounds", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--defeat-seed", action="store_true", help="Start from low-fun / broken-alliance state")
    parser.add_argument("--kernel", default="http://127.0.0.1:8080")
    parser.add_argument("--no-write", action="store_true", help="Skip writing receipts/* artifacts")
    args = parser.parse_args()

    if args.mode == "local":
        result = run_local_simulation(rounds=args.rounds, seed=args.seed, defeat_seed=args.defeat_seed)
    else:
        result = run_kernel_simulation(kernel_url=args.kernel, rounds=args.rounds)

    if not args.no_write:
        json_path, md_path = write_sim_artifacts(result, ROOT / "receipts")
        result["artifact_paths"] = {"json": str(json_path), "markdown": str(md_path)}
        print(f"Wrote {json_path.name} and {md_path.name}")

    print(json.dumps({
        "work_pack_id": result["work_pack_id"],
        "mode": result["mode"],
        "rounds_completed": result["rounds_completed"],
        "stopped_early": result["stopped_early"],
        "final_metrics": result["final_metrics"],
        "event_counts": result["event_counts"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
