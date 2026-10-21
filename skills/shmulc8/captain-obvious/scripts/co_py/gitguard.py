from __future__ import annotations
import os
import subprocess

def fix_blocker(root: str) -> str | None:
    """Why --fix should not run here, or None if it's safe.

    --fix rewrites test files in place with no backup, so the undo path is
    `git checkout -- <files>`. That only exists if the target is a git repo
    and the tests aren't already carrying uncommitted edits. Untracked files
    are fine — they can't be clobbered by an in-place rewrite.
    """
    if not os.path.isdir(root):
        return f"{root} is not an existing directory"
    try:
        inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root, capture_output=True, text=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return "git is not available, so there is no undo path"
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "not a git repository, so there is no undo path"

    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root, capture_output=True, text=True, timeout=60)
    if status.returncode != 0:
        return "could not read git status, so the undo path is unverified"
    if status.stdout.strip():
        n = len(status.stdout.strip().splitlines())
        return f"the working tree has {n} uncommitted change(s)"
    return None
