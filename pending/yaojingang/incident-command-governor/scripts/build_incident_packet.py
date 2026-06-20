#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_incident_packet.py <input.json>")

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    lines = [
        "# Incident Command Packet",
        "",
        f"## Summary\n{payload['incident_summary']}",
        "",
        "## Timeline",
    ]
    lines.extend([f"- {entry}" for entry in payload["timeline"]])
    lines.extend(
        [
            "",
            f"## Impact Scope\n{payload['affected_scope']}",
            "",
            "## Severity Signals",
        ]
    )
    lines.extend([f"- {entry}" for entry in payload["severity_signals"]])
    lines.extend(
        [
            "",
            "## Owners",
        ]
    )
    lines.extend([f"- {entry}" for entry in payload["owners"]])
    lines.extend(
        [
            "",
            "## Stakeholders",
        ]
    )
    lines.extend([f"- {entry}" for entry in payload["stakeholders"]])
    print("\n".join(lines))


if __name__ == "__main__":
    main()
