#!/usr/bin/env python3
"""Check creative-photo prerequisites without installing or changing anything."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    checks = {"python_3_10_or_newer": sys.version_info >= (3, 10), "pillow": False,
        "littlecms": False, "bundled_photo": (Path(__file__).resolve().parents[1] / "examples/inputs/portrait.png").is_file()}
    if importlib.util.find_spec("PIL"):
        try:
            from PIL import ImageCms
            ImageCms.createProfile("sRGB")
            checks["pillow"] = checks["littlecms"] = True
        except (ImportError, OSError):
            pass
    report = {"ok": all(checks.values()), "python": sys.version.split()[0], "checks": checks}
    if not report["ok"]:
        report["help"] = "Use Python 3.10+; install requirements with: python -m pip install -r requirements.txt. Keep the full Skill folder including examples/."
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
