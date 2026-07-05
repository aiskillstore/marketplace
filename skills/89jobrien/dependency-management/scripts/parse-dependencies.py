#!/usr/bin/env python3
"""Dependency parser for dependency-management skill.
Parses package.json, requirements.txt, pyproject.toml, etc.
"""

import json
import re
import sys
from pathlib import Path


def parse_package_json(file_path: Path) -> dict:
    """Parse package.json file."""
    try:
        data = json.loads(file_path.read_text())
        dependencies = {}

        # Combine all dependency types
        for dep_type in [
            "dependencies",
            "devDependencies",
            "peerDependencies",
            "optionalDependencies",
        ]:
            if dep_type in data:
                dependencies.update(data[dep_type])

        return {
            "file": str(file_path),
            "type": "npm",
            "dependencies": dependencies,
            "package_name": data.get("name", "unknown"),
            "version": data.get("version", "unknown"),
        }
    except json.JSONDecodeError as e:
        return {
            "file": str(file_path),
            "error": f"JSON parse error: {e}",
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": f"Error: {e}",
        }


def parse_requirements_txt(file_path: Path) -> dict:
    """Parse requirements.txt file."""
    try:
        content = file_path.read_text()
        dependencies = {}

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse package==version or package>=version, etc.
            match = re.match(r"^([a-zA-Z0-9_-]+)([<>=!]+)?(.+)?$", line.split("#")[0].strip())
            if match:
                package = match.group(1)
                version = match.group(3) if match.group(3) else None
                dependencies[package] = version or "unknown"

        return {
            "file": str(file_path),
            "type": "pip",
            "dependencies": dependencies,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": f"Error: {e}",
        }


def parse_pyproject_toml(file_path: Path) -> dict:
    """Parse pyproject.toml file (basic parsing)."""
    try:
        content = file_path.read_text()
        dependencies = {}

        # Simple regex-based parsing for dependencies
        # This is basic - for full parsing, use tomli or tomllib
        in_dependencies = False
        for line in content.split("\n"):
            line = line.strip()
            if "dependencies" in line and "=" in line:
                in_dependencies = True
                continue
            if in_dependencies:
                if line.startswith("["):
                    break
                if line and not line.startswith("#"):
                    # Parse dependency line
                    match = re.match(r'^"([^"]+)"', line)
                    if match:
                        dep = match.group(1)
                        package = dep.split(">=")[0].split("==")[0].split("~=")[0]
                        dependencies[package] = dep

        return {
            "file": str(file_path),
            "type": "pyproject",
            "dependencies": dependencies,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": f"Error: {e}",
        }


def detect_and_parse(file_path: Path) -> dict:
    """Detect file type and parse accordingly."""
    file_name = file_path.name.lower()

    if file_name == "package.json":
        return parse_package_json(file_path)
    if file_name == "requirements.txt":
        return parse_requirements_txt(file_path)
    if file_name == "pyproject.toml":
        return parse_pyproject_toml(file_path)
    return {
        "file": str(file_path),
        "error": f"Unknown file type: {file_name}",
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_dependencies.py <dependency_file> [<dependency_file>...]")
        sys.exit(1)

    results = []
    for file_path_str in sys.argv[1:]:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}", file=sys.stderr)
            continue

        result = detect_and_parse(file_path)
        results.append(result)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
