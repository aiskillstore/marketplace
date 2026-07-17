#!/usr/bin/env python3
"""Reject crash-prone background Blender jobs and describe the active session."""

from __future__ import annotations

import json
import platform
from typing import Any, Sequence


def classify_session(
    version: Sequence[int],
    background: bool,
    operating_system: str,
    machine: str,
) -> dict[str, Any]:
    """Classify a Blender session without importing bpy (useful for tests)."""
    normalized_version = tuple(int(part) for part in version[:3])
    errors: list[str] = []
    warnings: list[str] = []

    if background:
        errors.append(
            "Background Blender sessions are prohibited for animation, review rendering, and export. "
            "Use one persistent interactive Blender GUI connected through Blender MCP. Native render "
            "worker failures during process teardown cannot be caught or repaired by Python."
        )

    system = operating_system.lower()
    architecture = machine.lower()
    if system == "darwin" and architecture in {"arm64", "aarch64"} and normalized_version[:2] == (5, 1):
        warnings.append(
            "This Blender/platform combination has produced a native image-thread shutdown crash in an "
            "observed automation session. Keep Blender open for the whole task; if instability continues, "
            "use the current Blender 4.5 LTS patch release."
        )

    return {
        "ok": not errors,
        "mode": "background" if background else "persistent-gui",
        "blender_version": list(normalized_version),
        "platform": {"system": operating_system, "machine": machine},
        "errors": errors,
        "warnings": warnings,
    }


def inspect_session() -> dict[str, Any]:
    """Inspect the current Blender process. Call through Blender MCP before mutation."""
    try:
        import bpy  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "mode": "not-in-blender",
            "blender_version": None,
            "platform": {"system": platform.system(), "machine": platform.machine()},
            "errors": ["Run session_guard.inspect_session() inside the open Blender GUI through Blender MCP."],
            "warnings": [],
        }
    return classify_session(
        bpy.app.version,
        bool(bpy.app.background),
        platform.system(),
        platform.machine(),
    )


def main() -> int:
    result = inspect_session()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
