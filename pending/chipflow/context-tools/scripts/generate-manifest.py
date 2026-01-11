#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Generate project manifest for Claude Code reorientation.
Handles polyglot projects with multiple build systems (e.g., Python + Rust via maturin,
Python/Node + C++ via CMake/Ninja).
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


def run_cmd(cmd: list[str], cwd: Path | None = None) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return ""


@dataclass
class BuildSystem:
    """Represents a single build system/toolchain in the project."""
    name: str
    language: str
    manager: str
    configFile: str
    commands: dict = field(default_factory=dict)
    role: str = "primary"  # primary, extension, native, build-tool
    description: str = ""


def detect_build_systems(root: Path) -> list[BuildSystem]:
    """Detect all build systems in a polyglot project."""
    systems = []

    # Python ecosystems
    if (root / "pyproject.toml").exists():
        content = (root / "pyproject.toml").read_text()

        if "[project]" in content or "[tool.poetry]" in content:
            manager = "uv"
            if "[tool.pdm]" in content:
                manager = "pdm"
            elif "[tool.poetry]" in content:
                manager = "poetry"

            py_system = BuildSystem(
                name="python",
                language="python",
                manager=manager,
                configFile="pyproject.toml",
                role="primary",
                description="Python application/library"
            )
            py_system.commands = get_python_commands(root, manager)
            systems.append(py_system)

        if "maturin" in content or "[tool.maturin]" in content:
            systems.append(BuildSystem(
                name="maturin",
                language="rust",
                manager="maturin",
                configFile="pyproject.toml",
                role="extension",
                description="Rust extension for Python (via maturin)",
                commands={
                    "build": "maturin build",
                    "develop": "maturin develop",
                    "build-release": "maturin build --release",
                }
            ))

        if "pyo3" in content:
            if not any(s.name == "maturin" for s in systems):
                systems.append(BuildSystem(
                    name="pyo3",
                    language="rust",
                    manager="pyo3",
                    configFile="pyproject.toml",
                    role="extension",
                    description="Rust extension for Python (via PyO3)",
                ))

        if "cibuildwheel" in content:
            systems.append(BuildSystem(
                name="cibuildwheel",
                language="multi",
                manager="cibuildwheel",
                configFile="pyproject.toml",
                role="build-tool",
                description="Cross-platform wheel builder",
            ))

    # Standalone Rust
    if (root / "Cargo.toml").exists():
        cargo_content = (root / "Cargo.toml").read_text()
        is_workspace = "[workspace]" in cargo_content
        has_lib_or_bin = "[lib]" in cargo_content or "[[bin]]" in cargo_content

        if is_workspace or (has_lib_or_bin and not any(s.language == "rust" for s in systems)):
            role = "primary" if not systems else "native"
            systems.append(BuildSystem(
                name="cargo",
                language="rust",
                manager="cargo",
                configFile="Cargo.toml",
                role=role,
                description="Rust workspace" if is_workspace else "Rust project",
                commands={
                    "build": "cargo build",
                    "build-release": "cargo build --release",
                    "test": "cargo test",
                    "lint": "cargo clippy",
                    "fmt": "cargo fmt",
                }
            ))

    # Node.js / TypeScript
    if (root / "package.json").exists():
        pkg_content = (root / "package.json").read_text()
        try:
            pkg = json.loads(pkg_content)
            has_typescript = (root / "tsconfig.json").exists()

            role = "primary" if not systems else "native"
            node_system = BuildSystem(
                name="node",
                language="typescript" if has_typescript else "javascript",
                manager="npm",
                configFile="package.json",
                role=role,
                description="Node.js/TypeScript project"
            )
            node_system.commands = get_npm_commands(pkg)

            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "node-gyp" in deps or "bindings" in deps:
                node_system.description += " with native C++ addons (node-gyp)"
            if "@napi-rs/cli" in deps or "napi" in deps:
                node_system.description += " with native Rust addons (napi-rs)"
            if "neon-cli" in deps:
                node_system.description += " with native Rust addons (neon)"

            systems.append(node_system)
        except json.JSONDecodeError:
            pass

    # CMake (C/C++)
    if (root / "CMakeLists.txt").exists():
        role = "primary" if not systems else "native"
        uses_ninja = (root / "build.ninja").exists() or (root / "build" / "build.ninja").exists()

        systems.append(BuildSystem(
            name="cmake",
            language="c/c++",
            manager="cmake" + ("+ninja" if uses_ninja else ""),
            configFile="CMakeLists.txt",
            role=role,
            description="C/C++ project via CMake" + (" with Ninja" if uses_ninja else ""),
            commands={
                "configure": "cmake -B build" + (" -G Ninja" if uses_ninja else ""),
                "build": "cmake --build build",
                "build-release": "cmake --build build --config Release",
                "test": "ctest --test-dir build",
                "clean": "cmake --build build --target clean",
            }
        ))

    # Meson
    if (root / "meson.build").exists():
        role = "primary" if not systems else "native"
        systems.append(BuildSystem(
            name="meson",
            language="c/c++",
            manager="meson",
            configFile="meson.build",
            role=role,
            description="C/C++ project via Meson",
            commands={
                "setup": "meson setup build",
                "build": "meson compile -C build",
                "test": "meson test -C build",
            }
        ))

    # Makefile
    if (root / "Makefile").exists():
        if not any(s.language == "c/c++" for s in systems):
            makefile_content = (root / "Makefile").read_text()
            lang = "c/c++"
            if "rustc" in makefile_content or "cargo" in makefile_content:
                lang = "rust"
            elif "go build" in makefile_content:
                lang = "go"

            systems.append(BuildSystem(
                name="make",
                language=lang,
                manager="make",
                configFile="Makefile",
                role="primary" if not systems else "build-tool",
                description=f"{lang.upper()} project with Makefile",
                commands={
                    "build": "make",
                    "test": "make test",
                    "clean": "make clean",
                }
            ))

    # Go
    if (root / "go.mod").exists():
        role = "primary" if not systems else "native"
        systems.append(BuildSystem(
            name="go",
            language="go",
            manager="go",
            configFile="go.mod",
            role=role,
            description="Go module",
            commands={
                "build": "go build ./...",
                "test": "go test ./...",
                "lint": "golangci-lint run",
                "fmt": "gofmt -w .",
            }
        ))

    # vcpkg / conan
    if (root / "vcpkg.json").exists():
        systems.append(BuildSystem(
            name="vcpkg",
            language="c/c++",
            manager="vcpkg",
            configFile="vcpkg.json",
            role="dependency-manager",
            description="C++ dependency management via vcpkg",
        ))

    if (root / "conanfile.py").exists() or (root / "conanfile.txt").exists():
        config_file = "conanfile.py" if (root / "conanfile.py").exists() else "conanfile.txt"
        systems.append(BuildSystem(
            name="conan",
            language="c/c++",
            manager="conan",
            configFile=config_file,
            role="dependency-manager",
            description="C++ dependency management via Conan",
        ))

    role_order = {"primary": 0, "native": 1, "extension": 2, "build-tool": 3, "dependency-manager": 4}
    systems.sort(key=lambda s: role_order.get(s.role, 5))

    return systems


def get_python_commands(root: Path, manager: str) -> dict:
    """Extract Python build commands based on manager type."""
    commands = {}
    prefix = {"uv": "uv run", "pdm": "pdm run", "poetry": "poetry run"}.get(manager, "")

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()

        if "pytest" in content:
            commands["test"] = f"{prefix} pytest" if prefix else "pytest"
        if "ruff" in content:
            commands["lint"] = f"{prefix} ruff check ." if prefix else "ruff check ."
            commands["fmt"] = f"{prefix} ruff format ." if prefix else "ruff format ."
        if "black" in content:
            commands["fmt"] = f"{prefix} black ." if prefix else "black ."
        if "pyright" in content:
            commands["typecheck"] = f"{prefix} pyright" if prefix else "pyright"
        elif "mypy" in content:
            commands["typecheck"] = f"{prefix} mypy ." if prefix else "mypy ."

        if "[project.scripts]" in content or "[tool.poetry.scripts]" in content:
            commands["run"] = f"{manager} run <script-name>"

    return commands


def get_npm_commands(pkg: dict) -> dict:
    """Extract npm/yarn commands from package.json."""
    commands = {}
    scripts = pkg.get("scripts", {})

    for key in ["build", "test", "lint", "dev", "start", "typecheck", "fmt", "format"]:
        if key in scripts:
            commands[key] = f"npm run {key}"

    return commands


def find_entry_points(root: Path, build_systems: list[BuildSystem]) -> list[dict]:
    """Find entry points based on detected build systems."""
    entry_points = []
    seen_paths = set()

    for system in build_systems:
        if system.language == "python":
            for pattern in ["src/main.py", "main.py", "app.py", "src/__main__.py", "__main__.py"]:
                path = root / pattern
                if path.exists() and pattern not in seen_paths:
                    entry_points.append({"path": pattern, "type": "main", "system": system.name})
                    seen_paths.add(pattern)

            pyproject = root / "pyproject.toml"
            if pyproject.exists() and "[project.scripts]" in pyproject.read_text():
                entry_points.append({"path": "pyproject.toml [project.scripts]", "type": "cli-entrypoint", "system": system.name})

        elif system.language in ("typescript", "javascript"):
            pkg_path = root / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text())
                    for key in ["main", "module", "bin"]:
                        if key in pkg:
                            val = pkg[key]
                            if isinstance(val, str) and val not in seen_paths:
                                entry_points.append({"path": val, "type": key, "system": system.name})
                                seen_paths.add(val)
                except json.JSONDecodeError:
                    pass

            for pattern in ["src/index.ts", "src/index.js", "index.ts", "index.js"]:
                path = root / pattern
                if path.exists() and pattern not in seen_paths:
                    entry_points.append({"path": pattern, "type": "module", "system": system.name})
                    seen_paths.add(pattern)

        elif system.language == "rust":
            for pattern in ["src/main.rs", "src/lib.rs"]:
                path = root / pattern
                if path.exists() and pattern not in seen_paths:
                    etype = "binary" if "main" in pattern else "library"
                    entry_points.append({"path": pattern, "type": etype, "system": system.name})
                    seen_paths.add(pattern)

        elif system.language == "go":
            for pattern in ["main.go", "cmd/main.go"]:
                path = root / pattern
                if path.exists() and pattern not in seen_paths:
                    entry_points.append({"path": pattern, "type": "main", "system": system.name})
                    seen_paths.add(pattern)

        elif system.language == "c/c++":
            for pattern in ["src/main.c", "src/main.cpp", "main.c", "main.cpp"]:
                path = root / pattern
                if path.exists() and pattern not in seen_paths:
                    entry_points.append({"path": pattern, "type": "main", "system": system.name})
                    seen_paths.add(pattern)

    return entry_points


def get_directory_structure(root: Path) -> dict:
    """Identify key directories."""
    structure = {}
    mappings = {
        "sourceRoot": ["src", "lib", "app", "source"],
        "testRoot": ["tests", "test", "__tests__", "spec"],
        "configRoot": ["config", "conf", "configuration"],
        "docsRoot": ["docs", "doc", "documentation"],
        "scriptsRoot": ["scripts", "bin", "tools"],
        "nativeRoot": ["native", "crates", "rust", "cpp", "c"],
    }

    for key, candidates in mappings.items():
        for candidate in candidates:
            if (root / candidate).is_dir():
                structure[key] = candidate
                break

    return structure


def get_key_files(root: Path) -> list[str]:
    """Identify key files that should be read for understanding."""
    key_files = []
    candidates = [
        "README.md", "CLAUDE.md", ".claude/CLAUDE.md", "ARCHITECTURE.md",
        "docs/ARCHITECTURE.md", "CONTRIBUTING.md", "package.json",
        "pyproject.toml", "Cargo.toml", "go.mod", "CMakeLists.txt", "Makefile",
    ]

    for candidate in candidates:
        if (root / candidate).exists():
            key_files.append(candidate)

    return key_files


def get_recent_activity(root: Path) -> dict:
    """Get recent git activity."""
    activity = {}

    branch = run_cmd(["git", "branch", "--show-current"], root)
    if branch:
        activity["currentBranch"] = branch

    log = run_cmd(["git", "log", "--oneline", "-5"], root)
    if log:
        activity["recentCommits"] = log.split("\n")

    status = run_cmd(["git", "status", "--porcelain"], root)
    if status:
        lines = status.split("\n")
        activity["uncommittedChanges"] = len(lines)
        activity["modifiedFiles"] = [line[3:] for line in lines[:10] if line]

    head = run_cmd(["git", "rev-parse", "--short", "HEAD"], root)
    if head:
        activity["headCommit"] = head

    return activity


def count_files_by_type(root: Path) -> dict:
    """Count source files by extension (includes vendored code for language detection)."""
    counts = {}
    # Note: vendor is NOT excluded - we want to detect languages in vendored code
    exclude_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "target", "build", "dist", ".next", ".cache"}
    extensions = {
        ".py": "Python", ".pyi": "Python (stubs)", ".ts": "TypeScript", ".tsx": "TypeScript (React)",
        ".js": "JavaScript", ".jsx": "JavaScript (React)", ".rs": "Rust", ".go": "Go",
        ".c": "C", ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".h": "C/C++ Header", ".hpp": "C++ Header",
    }

    for ext, lang in extensions.items():
        count = 0
        try:
            for path in root.rglob(f"*{ext}"):
                if not any(ex in path.parts for ex in exclude_dirs):
                    count += 1
        except (PermissionError, OSError):
            pass
        if count > 0:
            counts[lang] = count

    return counts


def generate_manifest(root: Path) -> dict:
    """Generate complete project manifest."""
    build_systems = detect_build_systems(root)
    primary_system = build_systems[0] if build_systems else None
    file_stats = count_files_by_type(root)

    # Combine languages from build systems and detected files
    build_languages = set(s.language for s in build_systems)
    file_languages = set()
    for lang_name in file_stats.keys():
        # Map file stat names to canonical language names
        if "Python" in lang_name:
            file_languages.add("python")
        elif "TypeScript" in lang_name:
            file_languages.add("typescript")
        elif "JavaScript" in lang_name:
            file_languages.add("javascript")
        elif "Rust" in lang_name:
            file_languages.add("rust")
        elif "Go" in lang_name:
            file_languages.add("go")
        elif lang_name in ("C", "C/C++ Header"):
            file_languages.add("c")
        elif "C++" in lang_name:
            file_languages.add("c++")
    all_languages = list(build_languages | file_languages)

    manifest = {
        "version": "1.0",
        "generatedAt": datetime.now().isoformat(),
        "project": {
            "name": root.name,
            "path": str(root.absolute()),
            "isPolyglot": len(all_languages) > 1,
            "primaryLanguage": primary_system.language if primary_system else (all_languages[0] if all_languages else "unknown"),
            "languages": all_languages,
        },
        "buildSystems": [asdict(s) for s in build_systems],
        "structure": get_directory_structure(root),
        "entryPoints": find_entry_points(root, build_systems),
        "keyFiles": get_key_files(root),
        "fileStats": file_stats,
        "gitActivity": get_recent_activity(root),
    }

    if len(build_systems) > 1:
        manifest["polyglotInfo"] = {
            "description": describe_polyglot_setup(build_systems),
            "buildOrder": get_build_order(build_systems),
        }

    return manifest


def describe_polyglot_setup(systems: list[BuildSystem]) -> str:
    """Generate a human-readable description of the polyglot setup."""
    if len(systems) <= 1:
        return systems[0].description if systems else "Unknown project type"

    primary = systems[0]
    extensions = [s for s in systems[1:] if s.role == "extension"]
    natives = [s for s in systems[1:] if s.role == "native"]

    parts = [f"{primary.language.title()} project"]
    if extensions:
        parts.append(f"with native extensions: {', '.join(f'{e.language} ({e.manager})' for e in extensions)}")
    if natives:
        parts.append(f"includes {', '.join(n.language for n in natives)} components")

    return " ".join(parts)


def get_build_order(systems: list[BuildSystem]) -> list[str]:
    """Determine the order in which build systems should be invoked."""
    order = []
    for s in systems:
        if s.role == "dependency-manager":
            order.append(f"{s.name}: install dependencies")
    for s in systems:
        if s.role in ("extension", "native"):
            order.append(f"{s.name}: {s.commands.get('build', f'{s.manager} build')}")
    for s in systems:
        if s.role == "primary":
            order.append(f"{s.name}: {s.commands.get('build', f'{s.manager} build')}")
    return order


def main():
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    else:
        root = Path.cwd()

    manifest = generate_manifest(root)

    claude_dir = root / ".claude"
    claude_dir.mkdir(exist_ok=True)

    manifest_path = claude_dir / "project-manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
