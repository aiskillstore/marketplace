#!/usr/bin/env python3
"""Create a new Universal Audit artifact directory without overwriting prior evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Universal Audit artifact directory.")
    parser.add_argument("--audit-id", required=True, help="Audit identifier, for example AUD-PRODUCT-20260807-001")
    parser.add_argument("--output", required=True, type=Path, help="New artifact directory path")
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing path: {output}")

    template_path = Path(__file__).resolve().parents[1] / "assets" / "audit-manifest-template.json"
    template = template_path.read_text(encoding="utf-8")
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = template.replace("{{audit_id}}", args.audit_id).replace("{{created_at}}", created_at)

    output.mkdir(parents=True)
    manifest_path = output / "audit-manifest.json"
    manifest_path.write_text(manifest + "\n", encoding="utf-8")
    print(f"Created {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
