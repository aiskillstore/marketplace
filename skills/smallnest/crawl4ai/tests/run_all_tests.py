#!/usr/bin/env python3
"""
Run all skill tests
"""
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=False
    )

    return result.returncode == 0

def main():
    test_dir = Path(__file__).parent
    test_files = [
        "test_basic_crawling.py",
        "test_markdown_generation.py",
        "test_data_extraction.py",
        "test_advanced_patterns.py"
    ]

    results = {}
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            results[test_file] = run_test(str(test_path))
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)

    all_passed = True
    for test_file, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_file}")
        if not passed:
            all_passed = False

    print('='*60)

    if all_passed:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
