#!/usr/bin/env python3
"""Gravitas verification runner.

Discovers project-declared validators (see gravitas_verify) instead of
assuming toolchains from language. Historical language->command chains are
kept only as a labeled last-resort fallback when discovery finds nothing.
"""
import json
import subprocess
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "plugins" / "gravitas-antigravity" / "scripts"))

try:
    from gravitas_verify import discover_validators
    _DISCOVERY = True
except ModuleNotFoundError:
    _DISCOVERY = False

# Last-resort fallback only: used solely when discovery finds no
# project-declared validators. Never preferred over discovered commands.
FALLBACK_CHAINS = {
    "typescript": "npx tsc --noEmit",
    "python": "python3 -m pytest -q",
    "rust": "cargo test",
    "go": "go test ./...",
}


def detect_language() -> str:
    cwd = Path.cwd()
    checks = [
        ("typescript", "tsconfig.json"),
        ("python", "pyproject.toml"),
        ("python", "setup.py"),
        ("rust", "Cargo.toml"),
        ("go", "go.mod"),
        ("java", "pom.xml"),
        ("java", "build.gradle"),
        ("csharp", ".sln"),
        ("ruby", "Gemfile"),
        ("php", "composer.json"),
    ]
    for lang, marker in checks:
        if (cwd / marker).exists():
            return lang
    return "unknown"


def run_verification(command: str) -> tuple[bool, str]:
    """Run the verification command and return (success, output)."""
    import shlex
    try:
        commands = [cmd.strip() for cmd in command.split("&&")]
        full_output = ""
        for cmd in commands:
            parts = shlex.split(cmd)
            result = subprocess.run(parts, capture_output=True, text=True, timeout=300)
            full_output += result.stdout + result.stderr
            if result.returncode != 0:
                return False, full_output
        return True, full_output
    except subprocess.TimeoutExpired:
        return False, "ERROR: verification timed out after 300 seconds"
    except Exception as e:
        return False, f"ERROR: {e}"


def main():
    parser = argparse.ArgumentParser(description="Gravitas verification runner")
    parser.add_argument("--lang", help="Override language detection")
    parser.add_argument("--cmd", help="Override verification command")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    language = args.lang or detect_language()

    if args.cmd:
        command = args.cmd
        provenance = "explicit --cmd"
    else:
        catalog = discover_validators(Path.cwd()) if _DISCOVERY else {"validators": []}
        tests = [v for v in catalog["validators"] if v["kind"] == "test"]
        if tests:
            command = " && ".join(" ".join(c) for c in [v["command"] for v in tests])
            provenance = "discovered: " + ", ".join(v["id"] for v in tests)
        elif language in FALLBACK_CHAINS:
            command = FALLBACK_CHAINS[language]
            provenance = f"fallback chain for {language} (no project-declared validators found)"
        else:
            print(f"VERDICT: FAIL -- no validators discovered for '{language}'")
            print("Specify --cmd to run verification manually.")
            sys.exit(1)

    print(f"Language: {language}")
    print(f"Command:  {command}")
    print(f"Source:   {provenance}")
    print("Running...")
    print("-" * 60)

    success, output = run_verification(command)

    print(output)
    print("-" * 60)

    if args.json:
        result = {
            "language": language,
            "command": command,
            "success": success,
            "output": output,
            "verdict": "PASS" if success else "FAIL",
        }
        print(json.dumps(result, indent=2))
    else:
        if success:
            print("VERDICT: PASS")
        else:
            print("VERDICT: FAIL -- see output above")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
