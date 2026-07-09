#!/usr/bin/env python3
"""
commit_guard.py — PreToolUse hook for git commit.

Intercepts `git commit` via Claude Code PreToolUse hook.
Runs business conflict analysis on staged changes.
- P0 breaking changes → blocks commit, prints full report
- No P0 changes → allows commit to proceed
- Analysis errors → allows commit (fail-open, don't block due to tooling)

Install:
  bash /path/to/skill/scripts/install_hook.sh

Or manually in .claude/settings.local.json:
  {
    "hooks": {
      "PreToolUse": {
        "matcher": "git commit",
        "command": "python /path/to/skill/scripts/commit_guard.py"
      }
    }
  }
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path


def _find_project_root() -> Path:
    """Detect the git repo root from cwd."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return Path.cwd()


def _has_pending_changes(project_root: Path) -> bool:
    """Check for changes that could be committed.

    Covers:
      - Staged changes (git add → git commit)
      - Unstaged tracked changes (git commit -a / --all)
    """
    try:
        # Staged
        cached = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            capture_output=True, text=True, timeout=10,
            cwd=project_root, encoding="utf-8", errors="replace",
        )
        if cached.stdout.strip():
            return True
        # Unstaged tracked (for git commit -a)
        unstaged = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, timeout=10,
            cwd=project_root, encoding="utf-8", errors="replace",
        )
        return bool(unstaged.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _block_reason(t: "Translator") -> str:
    """Bilingual block reason for the PreToolUse hook stop signal."""
    return t.t("guard.block")


def _load_scripts() -> tuple:
    """Import skill modules by adding the script directory to sys.path."""
    script_dir = Path(__file__).parent.resolve()
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    from diff_analyzer import analyze as _da_analyze
    from impact_mapper import map_impact as _mi_map
    from report_generator import generate_report as _rg_gen
    from lang import Translator as _Tr

    return _da_analyze, _mi_map, _rg_gen, _Tr


def main() -> int:
    """Run the guard. Returns 0 (allow) or 1 (block)."""
    project_root = _find_project_root()

    # 1. Quick check — no pending changes, nothing to guard
    if not _has_pending_changes(project_root):
        return 0

    # 2. Change to project root so git/grep operations use correct base
    os.chdir(project_root)

    # 3. Load skill modules
    try:
        analyze, map_impact, generate_report, Translator = _load_scripts()
    except ImportError as e:
        # Fail-open: if scripts are missing, don't block commits
        print(f"[commit_guard] Warning: cannot load analysis scripts: {e}",
              file=sys.stderr)
        return 0

    # 4. Run analysis pipeline (importing modules directly, no shell pipes)
    try:
        # Use --cached first to analyze only STAGED changes (what 'git commit' commits).
        # For 'git commit -a', auto-staging hasn't happened yet at hook time,
        # so --cached would be empty — fall back to HEAD in that case.
        manifest_obj = analyze("--cached")
        manifest = asdict(manifest_obj)
        manifest["lang"] = manifest_obj.lang

        # Fallback: no staged changes — may be 'git commit -a' or brand new repo
        if not manifest_obj.changes:
            manifest_obj = analyze("HEAD")
            if manifest_obj.changes:
                manifest = asdict(manifest_obj)
                manifest["lang"] = manifest_obj.lang

        # Use manifest's detected language for translator consistency
        t = Translator(manifest_obj.lang)
        matrix_obj = map_impact(manifest, t)

        # 5. Check for P0 / BREAKING changes
        has_p0 = matrix_obj.overall_impact == "CRITICAL" or any(
            c.impact == "BREAKING" for c in matrix_obj.consumer_impacts
        )

        if not has_p0:
            return 0

        # 6. Build serialized matrix
        matrix = asdict(matrix_obj)
        matrix["consumer_impacts"] = [asdict(c) for c in matrix_obj.consumer_impacts]
        matrix["data_migration"] = asdict(matrix_obj.data_migration)
        matrix["api_compatibility"] = asdict(matrix_obj.api_compatibility)
        matrix["lang"] = t.lang_for_pipe()

        # 7. Generate report
        report = generate_report(manifest, matrix, t)

        # 8. Save report to project root
        report_path = project_root / "conflict-report.md"
        report_path.write_text(report, encoding="utf-8")

        # 9. Block commit — show report on stderr (visible to user),
        #    output JSON stop signal on stdout (for hook system).
        print(report, file=sys.stderr)
        block_reason = _block_reason(t)
        block_msg = json.dumps({
            "stop": True,
            "reason": block_reason,
        }, ensure_ascii=False)
        print(block_msg)

        return 1

    except Exception as e:
        # Fail-open: don't block commits if analysis crashes
        print(f"[commit_guard] Analysis error (commit allowed): {e}",
              file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
