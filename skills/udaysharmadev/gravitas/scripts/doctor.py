#!/usr/bin/env python3
"""Report portable GRAVITAS Core and known Native plugin discovery state."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_plugin_names(home: Path) -> set[str]:
    names: set[str] = set()
    for manifest in (
        home / ".gemini/config/import_manifest.json",
        home / ".gemini/antigravity-cli/import_manifest.json",
    ):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        names.update(item.get("name") for item in data.get("imports", []) if isinstance(item, dict) and isinstance(item.get("name"), str))
    return names


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    home = Path.home()
    native_candidates = [
        home / ".gemini/config/plugins/gravitas-native",
        home / ".gemini/antigravity-cli/plugins/gravitas-native",
        # Pre-bundle GRAVITAS installations used this root plugin name.
        home / ".gemini/config/plugins/gravitas",
        home / ".gemini/antigravity-cli/plugins/gravitas",
    ]
    native = next((path for path in native_candidates if path.is_dir()), None)
    imported = imported_plugin_names(home)
    result = {
        "gravitas_core_detected": (skill_root / "SKILL.md").is_file(),
        "core_path": str(skill_root),
        "canonical_skill_sha256": sha256(skill_root / "SKILL.md"),
        "antigravity_cli_detected": shutil.which("agy") is not None,
        "gravitas_native_detected": native is not None,
        "native_plugin_path": str(native) if native else None,
        "native_plugin_enabled": bool(native and native.name in imported),
        "native_hooks_available": bool(native and (native / "hooks.json").is_file()),
    }
    print(json.dumps(result, indent=2))
    return 0 if result["gravitas_core_detected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
