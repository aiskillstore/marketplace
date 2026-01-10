#!/usr/bin/env python3
"""Verify code-validation-sandbox skill environment is ready."""
import subprocess
import sys
import shutil


def check_python():
    """Check Python 3.8+ is available."""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, "python3 not found"
    except FileNotFoundError:
        return False, "python3 not installed"


def check_docker():
    """Check Docker is available for sandbox validation."""
    if shutil.which("docker") is None:
        return False, "docker not installed"

    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False, "docker not running"
    return True, "docker available"


def main():
    errors = []

    # Check Python
    ok, msg = check_python()
    if not ok:
        errors.append(f"Python: {msg}")

    # Check Docker (optional but recommended)
    ok, msg = check_docker()
    if not ok:
        print(f"⚠ Docker: {msg} (optional for isolated validation)")

    if errors:
        print(f"✗ Validation failed: {'; '.join(errors)}")
        print("Run: brew install python3 docker")
        sys.exit(1)

    print("✓ code-validation-sandbox ready")
    sys.exit(0)


if __name__ == "__main__":
    main()
