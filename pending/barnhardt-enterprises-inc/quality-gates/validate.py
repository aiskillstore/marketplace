#!/usr/bin/env python3
"""
Quality Gates Validation Aggregator

Runs all quality validators and aggregates results.
Exits 0 if all pass, 1 if any fail.

Usage:
    .claude/skills/quality-gates/validate.py [--verbose]
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class Validator:
    """Runs a validation script and captures results."""

    def __init__(self, name: str, script_path: str, description: str):
        self.name = name
        self.script_path = script_path
        self.description = description
        self.passed = False
        self.output = ""

    def run(self, verbose: bool = False) -> bool:
        """Run the validator and capture output."""
        if not Path(self.script_path).exists():
            self.output = f"Script not found: {self.script_path}"
            return False

        try:
            result = subprocess.run(
                ['python3', self.script_path],
                capture_output=True,
                text=True,
                timeout=60
            )

            self.output = result.stdout + result.stderr
            self.passed = result.returncode == 0

            if verbose:
                print(f"\n{BLUE}[{self.name}]{RESET}")
                print(self.output)

            return self.passed

        except subprocess.TimeoutExpired:
            self.output = "Validation timed out after 60 seconds"
            return False
        except Exception as e:
            self.output = f"Error running validator: {str(e)}"
            return False


def find_project_root() -> Path:
    """Find project root by looking for .claude directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.claude').exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (.claude directory)")


def main():
    """Run all quality validators and aggregate results."""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Quality Gates Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Find project root
    try:
        project_root = find_project_root()
    except RuntimeError as e:
        print(f"{RED}✗ {str(e)}{RESET}")
        sys.exit(1)

    # Define all validators
    validators = [
        Validator(
            name="TypeScript Strict Mode",
            script_path=str(project_root / '.claude/skills/typescript-strict-guard/validate-types.py'),
            description="Check for 'any' types, @ts-ignore, and non-null assertions"
        ),
        Validator(
            name="Security Vulnerabilities",
            script_path=str(project_root / '.claude/skills/security-sentinel/validate-security.py'),
            description="Check for hardcoded secrets, missing input validation, SQL injection"
        ),
        Validator(
            name="Next.js Patterns",
            script_path=str(project_root / '.claude/skills/nextjs-15-specialist/validate-patterns.py'),
            description="Check for async client components, improper data fetching"
        ),
        Validator(
            name="Database Queries",
            script_path=str(project_root / '.claude/skills/drizzle-orm-patterns/validate-queries.py'),
            description="Check for SQL injection risks, missing error handling"
        ),
        Validator(
            name="React 19 Patterns",
            script_path=str(project_root / '.claude/skills/react-19-patterns/validate-react.py'),
            description="Check for improper hook usage, server/client component violations"
        ),
    ]

    # Run all validators
    results: List[Tuple[Validator, bool]] = []
    for validator in validators:
        print(f"Running {validator.name}...", end=' ', flush=True)
        passed = validator.run(verbose)
        results.append((validator, passed))

        if passed:
            print(f"{GREEN}✓ PASS{RESET}")
        else:
            print(f"{RED}✗ FAIL{RESET}")

    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed_count = sum(1 for _, passed in results if passed)
    failed_count = len(results) - passed_count

    for validator, passed in results:
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"{status} {validator.name}")
        if not passed and not verbose:
            print(f"  {YELLOW}└─ {validator.output[:100]}...{RESET}")

    print(f"\n{BLUE}Total:{RESET} {passed_count} passed, {failed_count} failed")

    # Exit code
    if failed_count > 0:
        print(f"\n{RED}Quality gates FAILED. Fix issues before proceeding.{RESET}")
        print(f"{YELLOW}Run with --verbose flag for detailed output.{RESET}\n")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All quality gates PASSED. Ready to proceed.{RESET}\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
