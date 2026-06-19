#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    proc = subprocess.run(
        [sys.executable, "scripts/build_confusion_matrix.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    summary = payload["summary"]
    ok = (
        proc.returncode == 0
        and summary["accuracy"] == 1.0
        and summary["misroute_count"] == 0
        and summary["ambiguous_case_count"] == 0
        and payload["route_stats"]["no_route"]["recall"] == 1.0
    )
    report = {
        "ok": ok,
        "summary": summary,
        "route_stats": payload["route_stats"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
