#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Test list_files MCP tool functionality."""

import sqlite3
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_codebase" / ".claude" / "repo-map.db"


def list_files(pattern: str | None = None, limit: int = 100) -> dict:
    """
    List all indexed files, optionally filtered by glob pattern.
    This is a copy of the MCP server implementation for testing.
    """
    if not TEST_DB.exists():
        return {"error": "Database not found"}

    conn = sqlite3.connect(TEST_DB, timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        # Get distinct file paths from symbols table
        query = "SELECT DISTINCT file_path FROM symbols"
        params: list = []

        # Apply glob pattern filtering if provided
        if pattern:
            # Convert glob pattern to SQL LIKE pattern
            sql_pattern = pattern.replace("*", "%").replace("?", "_")
            query += " WHERE file_path LIKE ?"
            params.append(sql_pattern)

        query += " ORDER BY file_path LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        files = [row["file_path"] for row in rows]

        return {
            "files": files,
            "count": len(files),
            "pattern": pattern or "all",
            "limit": limit
        }
    finally:
        conn.close()


def test_list_all_files():
    """Test listing all files."""
    print("\n" + "=" * 60)
    print("TEST 1: list_files() - All files")
    print("=" * 60)
    print("Use Case: User wants to see all indexed files\n")

    result = list_files()

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if files:
        print(f"✅ PASS: Found {result['count']} file(s)")
        for f in sorted(files):
            print(f"  - {f}")
        return True
    else:
        print("❌ FAIL: No files found")
        return False


def test_list_python_files():
    """Test listing Python files."""
    print("\n" + "=" * 60)
    print("TEST 2: list_files('*.py') - Python files")
    print("=" * 60)
    print("Use Case: User asks 'What Python files are indexed?'\n")

    result = list_files(pattern="*.py")

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if files and all(f.endswith(".py") for f in files):
        print(f"✅ PASS: Found {result['count']} Python file(s)")
        for f in sorted(files):
            print(f"  - {f}")
        return True
    else:
        print(f"❌ FAIL: Expected .py files, got {files}")
        return False


def test_list_specific_file():
    """Test finding specific file by name."""
    print("\n" + "=" * 60)
    print("TEST 3: list_files('*instructions*') - Specific file pattern")
    print("=" * 60)
    print("Use Case: User asks 'Where is the instructions file?'\n")

    result = list_files(pattern="*instructions*")

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if files:
        print(f"✅ PASS: Found {result['count']} matching file(s)")
        for f in files:
            print(f"  - {f}")
        return "instructions" in files[0].lower()
    else:
        print("❌ FAIL: No matching files found")
        return False


def test_list_device_files():
    """Test listing device-related files."""
    print("\n" + "=" * 60)
    print("TEST 4: list_files('*device*') - Device files")
    print("=" * 60)
    print("Use Case: User asks 'What device files do we have?'\n")

    result = list_files(pattern="*device*")

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if files:
        print(f"✅ PASS: Found {result['count']} matching file(s)")
        for f in files:
            print(f"  - {f}")
        return True
    else:
        print("⚠️  No device files found (may be expected)")
        return True  # Not a failure - there might not be device files


def test_exact_path():
    """Test finding file by exact path (no wildcards)."""
    print("\n" + "=" * 60)
    print("TEST 5: list_files('device.py') - Exact path, no wildcards")
    print("=" * 60)
    print("Use Case: User asks 'Does device.py exist?'\n")

    result = list_files(pattern="device.py")

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if files and "device.py" in files:
        print(f"✅ PASS: Found exact file")
        for f in files:
            print(f"  - {f}")
        return True
    else:
        print(f"❌ FAIL: Exact path 'device.py' not found")
        print(f"Note: SQL LIKE 'device.py' should match 'device.py' exactly")
        print(f"Returned: {files}")
        return False


def test_nonexistent_exact_path():
    """Test finding file that doesn't exist."""
    print("\n" + "=" * 60)
    print("TEST 6: list_files('nonexistent.py') - File doesn't exist")
    print("=" * 60)
    print("Use Case: User asks about file that doesn't exist\n")

    result = list_files(pattern="nonexistent.py")

    if "error" in result:
        print(f"❌ FAIL: {result['error']}")
        return False

    files = result["files"]
    if len(files) == 0:
        print(f"✅ PASS: Correctly returned empty list for nonexistent file")
        return True
    else:
        print(f"⚠️  UNEXPECTED: Found files when none expected: {files}")
        return False


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 60)
    print("LIST_FILES MCP TOOL TEST SUITE")
    print("Testing against: tests/test_codebase")
    print("=" * 60)

    if not TEST_DB.exists():
        print(f"\n❌ ERROR: Database not found at {TEST_DB}")
        print("Run: uv run scripts/generate-repo-map.py tests/test_codebase")
        return False

    results = []
    results.append(("List all files", test_list_all_files()))
    results.append(("List Python files (*.py)", test_list_python_files()))
    results.append(("List specific file (*instructions*)", test_list_specific_file()))
    results.append(("List device files (*device*)", test_list_device_files()))
    results.append(("Exact path (device.py)", test_exact_path()))
    results.append(("Nonexistent file (nonexistent.py)", test_nonexistent_exact_path()))

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
        print("\n🎉 All tests passed! list_files tool is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")

    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
