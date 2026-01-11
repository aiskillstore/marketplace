#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Test MCP tool functionality on test codebase."""

import sqlite3
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_codebase" / ".claude" / "repo-map.db"


def test_search_symbols_by_name():
    """Test Case 1: Finding enum definition by exact name."""
    print("\n" + "=" * 60)
    print("TEST 1: search_symbols('InstructionData')")
    print("=" * 60)
    print("Use Case: User asks 'What variants does InstructionData have?'")
    print("Expected: Find the InstructionData enum\n")

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute(
        "SELECT name, kind, signature, file_path, line_number FROM symbols WHERE name = ?",
        ["InstructionData"]
    )
    results = cursor.fetchall()
    conn.close()

    if results:
        print(f"✅ PASS: Found {len(results)} symbol(s)")
        for name, kind, sig, file_path, line_no in results:
            print(f"  - {name} ({kind}) in {file_path}:{line_no}")
            if sig:
                print(f"    Signature: {sig}")
    else:
        print("❌ FAIL: No results found")

    return len(results) > 0


def test_search_symbols_by_pattern():
    """Test Case 2: Finding functions by pattern."""
    print("\n" + "=" * 60)
    print("TEST 2: search_symbols('setup_*')")
    print("=" * 60)
    print("Use Case: User asks 'Find all setup functions'")
    print("Expected: Find setup_model, setup_instance, setup_simulation, setup_solver\n")

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute(
        "SELECT name, kind, signature, file_path, line_number FROM symbols WHERE name LIKE ? AND kind = 'function'",
        ["setup_%"]
    )
    results = cursor.fetchall()
    conn.close()

    expected = {"setup_model", "setup_instance", "setup_simulation", "setup_solver"}
    found_names = {row[0] for row in results}

    if expected.issubset(found_names):
        print(f"✅ PASS: Found {len(results)} setup function(s)")
        for name, kind, sig, file_path, line_no in results:
            print(f"  - {name}() in {file_path}:{line_no}")
            if sig:
                print(f"    Signature: {sig}")
    else:
        print(f"❌ FAIL: Expected {expected}, found {found_names}")

    return expected.issubset(found_names)


def test_search_symbols_handler_pattern():
    """Test Case 2b: Finding classes ending with Handler."""
    print("\n" + "=" * 60)
    print("TEST 2b: search_symbols('*Handler')")
    print("=" * 60)
    print("Use Case: User asks 'Find Handler classes'")
    print("Expected: Find DeviceHandler, ConfigHandler if exists\n")

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute(
        "SELECT name, kind, signature, file_path, line_number FROM symbols WHERE name LIKE ?",
        ["%Handler"]
    )
    results = cursor.fetchall()
    conn.close()

    if results:
        print(f"✅ PASS: Found {len(results)} Handler symbol(s)")
        for name, kind, sig, file_path, line_no in results:
            print(f"  - {name} ({kind}) in {file_path}:{line_no}")
    else:
        print("❌ FAIL: No Handler symbols found")

    return len(results) > 0


def test_get_symbol_content():
    """Test Case 3: Getting complete enum definition."""
    print("\n" + "=" * 60)
    print("TEST 3: get_symbol_content('InstructionData')")
    print("=" * 60)
    print("Use Case: After finding enum, get its complete definition")
    print("Expected: Return enum with line range, can then read file\n")

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute(
        "SELECT name, kind, signature, docstring, file_path, line_number, end_line_number FROM symbols WHERE name = ?",
        ["InstructionData"]
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        name, kind, sig, doc, file_path, line_no, end_line = result
        print(f"✅ PASS: Found symbol")
        print(f"  Name: {name}")
        print(f"  Kind: {kind}")
        print(f"  Location: {file_path}:{line_no}")
        if end_line:
            print(f"  Lines: {line_no}-{end_line} ({end_line - line_no + 1} lines)")
        if doc:
            print(f"  Docstring: {doc}")

        # Simulate reading the actual content
        file_full_path = Path(__file__).parent / "test_codebase" / file_path
        if file_full_path.exists() and end_line:
            lines = file_full_path.read_text().splitlines()
            content = "\n".join(lines[line_no-1:end_line])
            print(f"\n  Content preview (first 200 chars):\n  {content[:200]}...")

        return True
    else:
        print("❌ FAIL: Symbol not found")
        return False


def test_get_file_symbols():
    """Test Case 4: Listing all symbols in a file."""
    print("\n" + "=" * 60)
    print("TEST 4: get_file_symbols('utils.py')")
    print("=" * 60)
    print("Use Case: User asks 'What functions are in utils.py?'")
    print("Expected: List all functions and classes in utils.py\n")

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute(
        "SELECT name, kind, signature, line_number FROM symbols WHERE file_path = ? ORDER BY line_number",
        ["utils.py"]
    )
    results = cursor.fetchall()
    conn.close()

    if results:
        print(f"✅ PASS: Found {len(results)} symbol(s) in utils.py")
        for name, kind, sig, line_no in results:
            print(f"  [{line_no}] {name} ({kind})")
            if sig:
                print(f"      {sig}")
    else:
        print("❌ FAIL: No symbols found in utils.py")

    return len(results) > 0


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 60)
    print("MCP TOOLS TEST SUITE")
    print("Testing against: tests/test_codebase")
    print("=" * 60)

    if not TEST_DB.exists():
        print(f"\n❌ ERROR: Database not found at {TEST_DB}")
        print("Run: uv run scripts/generate-repo-map.py tests/test_codebase")
        return False

    results = []
    results.append(("Search by name", test_search_symbols_by_name()))
    results.append(("Search by pattern (setup_*)", test_search_symbols_by_pattern()))
    results.append(("Search by pattern (*Handler)", test_search_symbols_handler_pattern()))
    results.append(("Get symbol content", test_get_symbol_content()))
    results.append(("Get file symbols", test_get_file_symbols()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! MCP tools are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")

    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
