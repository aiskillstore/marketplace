#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

"""Find code relationships: imports, dependents, callers, and tests.

Usage:
    uv run find_code_relationships.py <file_or_module> [--type imports|dependents|callers|tests|all]

Examples:
    uv run find_code_relationships.py src/auth/service.py --type all
    uv run find_code_relationships.py auth_service --type dependents
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CodeRelationships:
    target: str
    imports: list[str] = field(default_factory=list)
    imported_by: list[tuple[str, int]] = field(default_factory=list)  # (file, line)
    callers: list[tuple[str, int, str]] = field(default_factory=list)  # (file, line, context)
    tests: list[str] = field(default_factory=list)


def find_python_imports(file_path: Path) -> list[str]:
    """Extract imports from a Python file."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # Match: import X, from X import Y
        import_pattern = re.compile(
            r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE
        )
        for match in import_pattern.finditer(content):
            module = match.group(1) or match.group(2)
            if module:
                imports.append(module)
    except Exception:
        pass
    return imports


def find_dependents(
    target: str, root: Path, extensions: tuple[str, ...] = (".py",)
) -> list[tuple[str, int]]:
    """Find files that import the target module."""
    dependents = []
    target_patterns = [
        re.compile(rf"from\s+{re.escape(target)}\s+import"),
        re.compile(rf"import\s+{re.escape(target)}(?:\s|$|,)"),
        re.compile(rf"from\s+[\w.]*{re.escape(target)}\s+import"),
    ]

    for file_path in root.rglob("*"):
        if file_path.suffix not in extensions:
            continue
        if "__pycache__" in str(file_path) or ".git" in str(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                for pattern in target_patterns:
                    if pattern.search(line):
                        dependents.append((str(file_path.relative_to(root)), i))
                        break
        except Exception:
            pass

    return dependents


def find_callers(
    target: str, root: Path, extensions: tuple[str, ...] = (".py",)
) -> list[tuple[str, int, str]]:
    """Find files that call a function or use a class."""
    callers = []
    # Pattern for function calls or class instantiation
    call_pattern = re.compile(rf"\b{re.escape(target)}\s*\(")

    for file_path in root.rglob("*"):
        if file_path.suffix not in extensions:
            continue
        if "__pycache__" in str(file_path) or ".git" in str(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                if call_pattern.search(line):
                    callers.append((str(file_path.relative_to(root)), i, line.strip()[:80]))
        except Exception:
            pass

    return callers


def find_tests(target: str, root: Path) -> list[str]:
    """Find test files that reference the target."""
    tests = []
    test_patterns = ["test_*.py", "*_test.py", "tests/**/*.py"]

    for pattern in test_patterns:
        for test_file in root.glob(pattern):
            if "__pycache__" in str(test_file):
                continue
            try:
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                if target in content:
                    tests.append(str(test_file.relative_to(root)))
            except Exception:
                pass

    return list(set(tests))


def analyze(target: str, root: Path, analysis_type: str = "all") -> CodeRelationships:
    """Run relationship analysis on target."""
    result = CodeRelationships(target=target)

    # If target is a file, get its module name
    target_path = root / target if not Path(target).is_absolute() else Path(target)
    module_name = target

    if target_path.exists() and target_path.is_file():
        # Extract module name from file path
        module_name = target_path.stem
        if analysis_type in ("all", "imports"):
            result.imports = find_python_imports(target_path)

    if analysis_type in ("all", "dependents"):
        result.imported_by = find_dependents(module_name, root)

    if analysis_type in ("all", "callers"):
        result.callers = find_callers(module_name, root)

    if analysis_type in ("all", "tests"):
        result.tests = find_tests(module_name, root)

    return result


def format_output(result: CodeRelationships) -> str:
    """Format analysis results as markdown."""
    lines = [f"# Code Relationships: `{result.target}`\n"]

    if result.imports:
        lines.append("## Imports (dependencies)")
        for imp in sorted(set(result.imports)):
            lines.append(f"- `{imp}`")
        lines.append("")

    if result.imported_by:
        lines.append("## Imported By (dependents)")
        for file, line in sorted(set(result.imported_by)):
            lines.append(f"- `{file}:{line}`")
        lines.append("")

    if result.callers:
        lines.append("## Callers")
        for file, line, context in result.callers[:20]:  # Limit output
            lines.append(f"- `{file}:{line}` - `{context}`")
        if len(result.callers) > 20:
            lines.append(f"- ... and {len(result.callers) - 20} more")
        lines.append("")

    if result.tests:
        lines.append("## Tests")
        for test in sorted(result.tests):
            lines.append(f"- `{test}`")
        lines.append("")

    if not any([result.imports, result.imported_by, result.callers, result.tests]):
        lines.append("No relationships found.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find code relationships for a file or module")
    parser.add_argument("target", help="File path or module/function name to analyze")
    parser.add_argument(
        "--type",
        choices=["imports", "dependents", "callers", "tests", "all"],
        default="all",
        help="Type of analysis to perform",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to search (default: current directory)",
    )

    args = parser.parse_args()
    result = analyze(args.target, args.root, args.type)
    print(format_output(result))


if __name__ == "__main__":
    main()
