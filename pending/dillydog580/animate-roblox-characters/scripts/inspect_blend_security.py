#!/usr/bin/env python3
"""Inspect an untrusted .blend inside a persistent GUI session.

Open the file with Blender's auto-execution disabled, connect Blender MCP, and
call ``inspect_current_file()``. Do not launch a disposable background Blender
process for this inspection. This script never registers or executes embedded
text blocks.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


NETWORK_RE = re.compile(r"\b(requests|urllib|socket|http\.client|ftplib)\b|https?://", re.I)
PROCESS_RE = re.compile(r"\b(subprocess|os\.system|os\.popen|pty|multiprocessing)\b", re.I)
DYNAMIC_RE = re.compile(r"\b(exec|eval|compile)\s*\(", re.I)
FILESYSTEM_RE = re.compile(r"\b(open|Path\s*\([^)]*\)\.(?:write|unlink)|shutil\.)", re.I)
HOME_RE = re.compile(
    "(?:/" + "Users" + "/|/" + "home" + "/|[A-Za-z]:\\\\" + "Users" + "\\\\)"
)


def inspect_source_capabilities(source: str) -> dict[str, bool]:
    """Find aliased imports/calls; parse failures remain suspicious."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {
            "network": False,
            "process": False,
            "dynamic_code": False,
            "filesystem": False,
            "analysis_failed": True,
        }

    aliases: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    def resolve(node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return aliases.get(node.id, node.id)
        if isinstance(node, ast.Call):
            return resolve(node.func)
        if isinstance(node, ast.Attribute):
            parent = resolve(node.value)
            return f"{parent}.{node.attr}" if parent else None
        return None

    calls = {
        name
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and (name := resolve(node.func)) is not None
    }
    imports = set(aliases.values())
    return {
        "network": any(
            name.startswith(("requests", "urllib", "socket", "http.client", "ftplib"))
            for name in imports | calls
        ),
        "process": any(
            name in {"os.system", "os.popen"}
            or name.startswith(("subprocess", "multiprocessing", "pty"))
            for name in imports | calls
        ),
        "dynamic_code": any(
            name
            in {
                "eval",
                "exec",
                "compile",
                "__import__",
                "builtins.eval",
                "builtins.exec",
                "builtins.compile",
                "builtins.__import__",
            }
            for name in calls
        ),
        "filesystem": any(
            name in {"open", "builtins.open"}
            or name.startswith(("shutil.", "pathlib.Path."))
            or name
            in {
                "os.remove",
                "os.open",
                "os.unlink",
                "os.rename",
                "os.replace",
                "os.mkdir",
                "os.makedirs",
                "os.chmod",
                "os.rmdir",
                "os.removedirs",
                "Path.write_text",
                "Path.write_bytes",
                "Path.unlink",
                "Path.rename",
                "Path.replace",
            }
            or name.endswith(
                (
                    ".Path.write_text",
                    ".Path.write_bytes",
                    ".Path.unlink",
                    ".Path.rename",
                    ".Path.replace",
                )
            )
            for name in calls
        ),
        "analysis_failed": False,
    }


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def custom_properties(value: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in value.keys():
        if key == "_RNA_UI":
            continue
        item = value.get(key)
        if isinstance(item, (str, int, float, bool)) or item is None:
            result[str(key)] = item
        else:
            result[str(key)] = f"<{type(item).__name__}>"
    return result


def inspect_text(text: Any, dump_directory: Path | None) -> dict[str, Any]:
    source = text.as_string()
    encoded = source.encode("utf-8", errors="replace")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.name)
    dumped = None
    if dump_directory is not None:
        dump_directory.mkdir(parents=True, exist_ok=True)
        target = dump_directory / safe_name
        if target.suffix.lower() != ".py":
            target = target.with_suffix(target.suffix + ".py")
        target.write_bytes(encoded)
        dumped = str(target)
    ast_flags = inspect_source_capabilities(source)
    return {
        "name": text.name,
        "bytes": len(encoded),
        "sha256": sha256_bytes(encoded),
        "dumped_to": dumped,
        "flags": {
            "network": bool(NETWORK_RE.search(source)) or ast_flags["network"],
            "process": bool(PROCESS_RE.search(source)) or ast_flags["process"],
            "dynamic_code": bool(DYNAMIC_RE.search(source)) or ast_flags["dynamic_code"],
            "filesystem": bool(FILESYSTEM_RE.search(source)) or ast_flags["filesystem"],
            "home_path": bool(HOME_RE.search(source)),
            "analysis_failed": ast_flags["analysis_failed"],
        },
    }


def inspect_current_file(dump_directory: Path | None = None) -> dict[str, Any]:
    import bpy  # type: ignore

    armatures = []
    for obj in bpy.data.objects:
        if obj.type != "ARMATURE":
            continue
        armatures.append(
            {
                "name": obj.name,
                "bones": [bone.name for bone in obj.data.bones],
                "pose_bones": [bone.name for bone in obj.pose.bones],
                "custom_properties": custom_properties(obj),
            }
        )

    drivers = []
    for datablock in list(bpy.data.objects) + list(bpy.data.shape_keys):
        animation_data = getattr(datablock, "animation_data", None)
        for fcurve in getattr(animation_data, "drivers", ()) if animation_data else ():
            drivers.append(
                {
                    "owner": getattr(datablock, "name", repr(datablock)),
                    "data_path": fcurve.data_path,
                    "expression": fcurve.driver.expression,
                    "variables": [variable.name for variable in fcurve.driver.variables],
                }
            )

    external_paths = []
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath:
            external_paths.append({"kind": "image", "name": image.name, "path": image.filepath})
    for library in bpy.data.libraries:
        external_paths.append({"kind": "library", "name": library.name, "path": library.filepath})
    for movie in bpy.data.movieclips:
        if movie.filepath:
            external_paths.append({"kind": "movieclip", "name": movie.name, "path": movie.filepath})
    for font in bpy.data.fonts:
        if font.filepath:
            external_paths.append({"kind": "font", "name": font.name, "path": font.filepath})

    handlers = {}
    for name in dir(bpy.app.handlers):
        collection = getattr(bpy.app.handlers, name)
        if not isinstance(collection, list) or not collection:
            continue
        handlers[name] = [
            f"{getattr(item, '__module__', '')}.{getattr(item, '__qualname__', getattr(item, '__name__', repr(item)))}"
            for item in collection
        ]

    filepath = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    return {
        "ok": True,
        "blender_version": list(bpy.app.version),
        "autoexec_fail": bool(getattr(bpy.app, "autoexec_fail", False)),
        "autoexec_fail_message": getattr(bpy.app, "autoexec_fail_message", ""),
        "blend": str(filepath) if filepath else None,
        "blend_sha256": sha256_bytes(filepath.read_bytes()) if filepath and filepath.is_file() else None,
        "counts": {
            "objects": len(bpy.data.objects),
            "armatures": len(armatures),
            "texts": len(bpy.data.texts),
            "drivers": len(drivers),
            "external_paths": len(external_paths),
        },
        "armatures": armatures,
        "texts": [inspect_text(text, dump_directory) for text in bpy.data.texts],
        "drivers": drivers,
        "external_paths": external_paths,
        "handlers": handlers,
        "scene_custom_properties": custom_properties(bpy.context.scene),
        "object_names": sorted(obj.name for obj in bpy.data.objects),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump-texts", type=Path)
    parser.add_argument("--output", type=Path)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    payload = json.dumps(inspect_current_file(args.dump_texts), indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
