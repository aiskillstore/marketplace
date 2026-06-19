#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def render_packet(payload: dict) -> str:
    lines = [
        f"# Release Packet: {payload['release_name']}",
        "",
        "## Scope",
        payload["scope_summary"],
        "",
        "## Risks",
    ]
    for risk in payload["risks"]:
        lines.append(f"- [{risk['severity'].upper()}] {risk['summary']}")
    lines.extend(
        [
            "",
            "## Migrations",
            payload["migrations"],
            "",
            "## Rollout",
        ]
    )
    for step in payload["rollout_steps"]:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Rollback",
        ]
    )
    for trigger in payload["rollback_triggers"]:
        lines.append(f"- {trigger}")
    lines.extend(
        [
            "",
            "## Stakeholder Communication",
        ]
    )
    for audience, message in payload["stakeholder_messages"].items():
        lines.append(f"- {audience}: {message}")
    lines.extend(
        [
            "",
            "## Final Decision",
            payload["decision"],
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_release_packet.py <input.json>")
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(render_packet(payload), end="")


if __name__ == "__main__":
    main()
