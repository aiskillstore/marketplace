#!/usr/bin/env python3
"""
Test runner — runs all test suites and aggregates results.
Usage: python tests/run_all.py
"""
import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
TESTS_DIR = ROOT / "tests"

test_files = [
    "test_lang.py",
    "test_diff_analyzer.py",
    "test_impact_mapper.py",
    "test_report_generator.py",
    "test_commit_guard.py",
]

# Ensure child processes can output UTF-8 (emoji, Chinese)
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

all_passed = True
for tf in test_files:
    print(f"\n{'='*60}")
    print(f"  Running: {tf}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, str(TESTS_DIR / tf)],
        cwd=str(ROOT),
        capture_output=False,
        env=env,
    )
    if result.returncode != 0:
        all_passed = False

print(f"\n{'='*60}")
if all_passed:
    print(f"  [OK] All tests passed")
else:
    print(f"  [FAIL] Some tests failed")
print(f"{'='*60}\n")
sys.exit(0 if all_passed else 1)
