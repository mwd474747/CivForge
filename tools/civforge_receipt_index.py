#!/usr/bin/env python3
"""Build a local latest receipt index for CivForge."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "receipts"
DB_PATH = ROOT / "gravity_backend.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def latest_receipt_files(limit: int = 12) -> List[Dict[str, Any]]:
    if not RECEIPTS.exists():
        return []
    files = sorted(RECEIPTS.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "path": str(path.relative_to(ROOT)),
            "size": path.stat().st_size,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        for path in files[:limit]
    ]


def sqlite_counts() -> Dict[str, Any]:
    if not DB_PATH.exists():
        return {"exists": False, "receipts": None, "state_snapshots": None}
    try:
        conn = sqlite3.connect(str(DB_PATH))
        receipts = conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
        snapshots = conn.execute("SELECT COUNT(*) FROM state_snapshots").fetchone()[0]
        latest = conn.execute("SELECT id, turn, action, status, created_at FROM receipts ORDER BY created_at DESC LIMIT 5").fetchall()
        conn.close()
        return {
            "exists": True,
            "receipts": receipts,
            "state_snapshots": snapshots,
            "latest": [
                {"id": row[0], "turn": row[1], "action": row[2], "status": row[3], "created_at": row[4]}
                for row in latest
            ],
        }
    except Exception as exc:
        return {"exists": True, "error": f"{type(exc).__name__}: {exc}"}


def build_report(write_files: bool = True) -> Dict[str, Any]:
    latest_files = latest_receipt_files()
    db = sqlite_counts()
    report = {
        "schema": "civforge.receipt_index.v1",
        "generated_at": utc_now(),
        "status": "pass" if latest_files else "warn",
        "summary": {
            "latest_file_count": len(latest_files),
            "sqlite_receipts": db.get("receipts"),
            "sqlite_state_snapshots": db.get("state_snapshots"),
        },
        "latest_files": latest_files,
        "sqlite": db,
    }
    if write_files:
        write_report(report)
    return report


def write_report(report: Dict[str, Any]) -> None:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    json_path = RECEIPTS / "civforge-receipt-index-latest.json"
    md_path = RECEIPTS / "civforge-receipt-index-latest.md"
    receipt_path = RECEIPTS / "civforge-receipt-index-receipt-latest.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# CivForge Receipt Index",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- status: `{report['status']}`",
        f"- sqlite_receipts: `{report['summary']['sqlite_receipts']}`",
        "",
        "## Latest Files",
    ]
    for item in report["latest_files"]:
        lines.append(f"- `{item['path']}` `{item['mtime']}` `{item['size']}` bytes")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {
        "schema": "civforge.receipt.v1",
        "generated_at": report["generated_at"],
        "action": "civforge_receipt_index",
        "status": report["status"],
        "artifact": str(json_path.relative_to(ROOT)),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report(write_files=True)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
