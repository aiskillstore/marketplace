#!/usr/bin/env python3
"""
pytest runner script with common configurations.
Usage: uv run scripts/run_tests.py [mode] [additional pytest args]

Modes:
  quick     - Fast tests only, stop on first failure
  full      - All tests with verbose output
  coverage  - Full tests with coverage report
  failed    - Re-run only failed tests
  watch     - Run tests matching a pattern (pass pattern as next arg)
"""

import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Find project root by looking for pyproject.toml."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return current


def run_pytest(args: list[str]) -> int:
    """Run pytest with uv."""
    cmd = ["uv", "run", "pytest"] + args
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=get_project_root())


def main():
    args = sys.argv[1:]

    if not args:
        # Default: run all tests with verbose output
        return run_pytest(["-v"])

    mode = args[0]
    extra_args = args[1:]

    modes = {
        "quick": ["-v", "-x", "--tb=short", "-m", "not slow"],
        "full": ["-v", "--tb=short"],
        "coverage": [
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
        ],
        "failed": ["--lf", "-v"],
        "watch": ["-v", "-k"] + (extra_args[:1] if extra_args else [""]),
    }

    if mode in modes:
        pytest_args = modes[mode]
        if mode != "watch":
            pytest_args.extend(extra_args)
        else:
            pytest_args.extend(extra_args[1:])
        return run_pytest(pytest_args)

    # If mode is not recognized, pass all args directly to pytest
    return run_pytest(args)


if __name__ == "__main__":
    sys.exit(main())
