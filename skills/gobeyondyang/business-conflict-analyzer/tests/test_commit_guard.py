#!/usr/bin/env python3
"""
commit_guard unit tests — isolated, no git dependency for basic logic tests.

Usage: python tests/test_commit_guard.py
"""
import sys
import json
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_script_imports():
    """All analysis modules import successfully via _load_scripts path."""
    from commit_guard import _load_scripts
    analyze, map_impact, generate_report, Translator = _load_scripts()
    assert callable(analyze), "analyze should be callable"
    assert callable(map_impact), "map_impact should be callable"
    assert callable(generate_report), "generate_report should be callable"
    assert Translator is not None, "Translator should be imported"
    print(f"  [OK] test_script_imports: all 4 modules loaded")


def test_no_pending_changes():
    """_has_pending_changes returns False in an empty temp dir (not a git repo)."""
    from commit_guard import _has_pending_changes, _find_project_root
    # In a non-git directory, _has_pending_changes should not crash.
    with tempfile.TemporaryDirectory() as tmp:
        result = _has_pending_changes(Path(tmp))
        assert result is False, f"Empty dir should have no pending changes: {result}"
    print(f"  [OK] test_no_pending_changes: non-git dir returns False")


def test_block_reason_en():
    """_block_reason returns English block message for non-zh lang."""
    from lang import Translator
    from commit_guard import _block_reason

    t = Translator("en")
    reason = _block_reason(t)
    assert "P0 breaking changes" in reason, f"EN block reason expected: {reason}"
    print(f"  [OK] test_block_reason_en")


def test_block_reason_zh():
    """_block_reason returns Chinese block message for zh lang."""
    from lang import Translator
    from commit_guard import _block_reason

    t = Translator("zh")
    reason = _block_reason(t)
    assert "P0 级别" in reason, f"ZH block reason expected: {reason}"
    print(f"  [OK] test_block_reason_zh")


def test_find_project_root_not_git():
    """_find_project_root returns cwd when not in a git repo."""
    from commit_guard import _find_project_root
    import tempfile
    old_cwd = Path.cwd()
    tmp = tempfile.mkdtemp()
    try:
        os.chdir(tmp)
        root = _find_project_root()
        # Compare resolved paths to handle Windows 8.3 short-name vs long-name
        assert str(root.resolve()) == str(Path.cwd().resolve()), \
            f"Should return cwd, got {root} (cwd={Path.cwd()})"
    finally:
        os.chdir(old_cwd)
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"  [OK] test_find_project_root_not_git")


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  commit_guard tests")
    print(f"{'='*50}\n")

    tests = [
        test_script_imports,
        test_no_pending_changes,
        test_block_reason_en,
        test_block_reason_zh,
        test_find_project_root_not_git,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  Result: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    sys.exit(0 if failed == 0 else 1)
