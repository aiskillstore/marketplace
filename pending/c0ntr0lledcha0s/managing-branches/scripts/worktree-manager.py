#!/usr/bin/env python3
"""
Worktree Manager - Manage git worktrees for parallel development.

Commands:
  add <branch> [--path PATH] [--auto-path]  - Create a worktree
  list                                       - List all worktrees
  remove <name>                              - Remove a worktree
  clean [--dry-run]                          - Clean merged worktrees
  status                                     - Show worktree status
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_git(args: list, capture: bool = True, check: bool = True) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=capture,
            text=True,
            check=check
        )
        return result.stdout.strip() if capture else ""
    except subprocess.CalledProcessError as e:
        if capture and e.stderr:
            print(f"Error: {e.stderr.strip()}", file=sys.stderr)
        raise


def get_config_path() -> Path:
    """Get the branching config file path."""
    git_root = run_git(["rev-parse", "--show-toplevel"])
    config_path = Path(git_root) / ".claude" / "github-workflows" / "branching-config.json"
    return config_path


def load_config() -> dict:
    """Load the branching configuration."""
    config_path = get_config_path()

    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    # Return default config
    return {
        "worktrees": {
            "enabled": True,
            "baseDir": "../worktrees",
            "autoCreate": {
                "hotfix": True,
                "release": True
            }
        }
    }


def get_worktree_base_dir(config: dict) -> Path:
    """Get the base directory for worktrees."""
    git_root = Path(run_git(["rev-parse", "--show-toplevel"]))
    base_dir = config.get("worktrees", {}).get("baseDir", "../worktrees")

    # Resolve relative to git root
    if not os.path.isabs(base_dir):
        base_dir = git_root / base_dir

    return Path(base_dir)


def list_worktrees() -> list:
    """Get list of all worktrees with their info."""
    output = run_git(["worktree", "list", "--porcelain"])
    worktrees = []
    current = {}

    for line in output.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["commit"] = line.split(" ", 1)[1][:8]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True

    if current:
        worktrees.append(current)

    return worktrees


def add_worktree(args):
    """Add a new worktree."""
    config = load_config()
    branch = args.branch

    # Determine path
    if args.path:
        path = Path(args.path)
    elif args.auto_path:
        base_dir = get_worktree_base_dir(config)
        # Generate path from branch name
        safe_name = branch.replace("/", "-").replace("\\", "-")
        path = base_dir / safe_name
    else:
        # Use the last part of branch name
        base_dir = get_worktree_base_dir(config)
        safe_name = branch.split("/")[-1]
        path = base_dir / safe_name

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Creating worktree...")
    print(f"  Branch: {branch}")
    print(f"  Path: {path}")
    print()

    # Check if branch exists
    branch_exists = False
    try:
        run_git(["rev-parse", "--verify", branch])
        branch_exists = True
    except subprocess.CalledProcessError:
        # Check remote
        try:
            run_git(["rev-parse", "--verify", f"origin/{branch}"])
            branch_exists = True
        except subprocess.CalledProcessError:
            pass

    # Create worktree
    if branch_exists:
        # Use existing branch
        run_git(["worktree", "add", str(path), branch])
    else:
        # Create new branch
        # Determine base branch from config
        base = "main"  # default

        # Try to determine from branch prefix
        config_flows = config.get("flows", {})
        for branch_type, flow in config_flows.items():
            prefix = config.get("branches", {}).get("prefixes", {}).get(branch_type, "")
            if branch.startswith(prefix):
                base = flow.get("from", base)
                break

        print(f"Creating new branch from {base}")
        run_git(["worktree", "add", "-b", branch, str(path), base])

    print()
    print(f"✅ Worktree created: {path}")
    print()
    print(f"To work in this worktree:")
    print(f"  cd {path}")


def list_worktrees_cmd(args):
    """List all worktrees."""
    worktrees = list_worktrees()

    print("Active Worktrees")
    print("=" * 60)

    for i, wt in enumerate(worktrees, 1):
        path = wt.get("path", "")
        branch = wt.get("branch", "")
        commit = wt.get("commit", "")
        detached = wt.get("detached", False)

        # Determine if this is the main worktree
        is_main = i == 1

        # Format output
        if detached:
            branch_info = f"(detached at {commit})"
        elif branch:
            branch_info = branch
        else:
            branch_info = "(bare)"

        marker = " (main)" if is_main else ""
        print(f"{i}. {path}")
        print(f"   Branch: {branch_info}{marker}")
        print(f"   Commit: {commit}")

        # Get additional info
        if not wt.get("bare"):
            try:
                # Check if dirty
                status = subprocess.run(
                    ["git", "-C", path, "status", "--porcelain"],
                    capture_output=True,
                    text=True
                )
                if status.stdout.strip():
                    print(f"   Status: uncommitted changes")
                else:
                    print(f"   Status: clean")
            except subprocess.CalledProcessError:
                pass

        print()

    print(f"Total: {len(worktrees)} worktree(s)")


def remove_worktree(args):
    """Remove a worktree."""
    name = args.name
    force = args.force

    # Find the worktree
    worktrees = list_worktrees()
    target = None

    for wt in worktrees:
        path = wt.get("path", "")
        # Match by path or by name (last component)
        if path.endswith(name) or Path(path).name == name:
            target = wt
            break

    if not target:
        print(f"Error: Worktree '{name}' not found")
        print("Available worktrees:")
        for wt in worktrees:
            print(f"  - {wt.get('path', '')}")
        sys.exit(1)

    path = target.get("path")
    branch = target.get("branch", "")

    print(f"Removing worktree: {path}")
    if branch:
        print(f"Branch: {branch}")

    # Check for uncommitted changes
    if not force:
        try:
            status = subprocess.run(
                ["git", "-C", path, "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            if status.stdout.strip():
                print()
                print("Warning: Worktree has uncommitted changes!")
                if not args.yes:
                    if not sys.stdin.isatty():
                        print("Error: Cannot prompt in non-interactive mode. Use --yes to skip.")
                        return
                    response = input("Continue anyway? [y/N] ").strip().lower()
                    if response != "y":
                        print("Cancelled")
                        return
        except subprocess.CalledProcessError:
            pass

    # Remove worktree
    try:
        if force:
            run_git(["worktree", "remove", "--force", path])
        else:
            run_git(["worktree", "remove", path])
        print(f"✅ Worktree removed: {path}")
    except subprocess.CalledProcessError as e:
        if "not empty" in str(e) or "changes" in str(e):
            print("Worktree has changes. Use --force to remove anyway.")
        raise

    # Offer to delete branch
    if branch and not args.keep_branch:
        try:
            # Check if branch is merged
            merged = run_git(["branch", "--merged", "main"], check=False)
            if branch in merged:
                if args.yes:
                    run_git(["branch", "-d", branch])
                    print(f"✅ Branch deleted: {branch}")
                elif sys.stdin.isatty():
                    response = input(f"Delete merged branch '{branch}'? [y/N] ").strip().lower()
                    if response == "y":
                        run_git(["branch", "-d", branch])
                        print(f"✅ Branch deleted: {branch}")
        except subprocess.CalledProcessError:
            pass


def clean_worktrees(args):
    """Clean up worktrees for merged branches."""
    worktrees = list_worktrees()
    config = load_config()

    main_branch = config.get("branches", {}).get("main", "main")

    # Get merged branches
    try:
        merged = run_git(["branch", "--merged", main_branch]).split("\n")
        merged = [b.strip().lstrip("* ") for b in merged if b.strip()]
    except subprocess.CalledProcessError:
        merged = []

    # Find worktrees with merged branches
    to_clean = []

    for wt in worktrees[1:]:  # Skip main worktree
        branch = wt.get("branch", "")
        if branch in merged and branch != main_branch:
            to_clean.append(wt)

    if not to_clean:
        print("No worktrees to clean")
        return

    print(f"Found {len(to_clean)} worktree(s) with merged branches:")
    for wt in to_clean:
        print(f"  - {wt.get('path')} ({wt.get('branch')})")

    print()

    if args.dry_run:
        print("Dry run - no worktrees removed")
        return

    # Confirm removal (skip if --yes flag or non-interactive)
    if not args.yes:
        if not sys.stdin.isatty():
            print("Error: Cannot prompt in non-interactive mode. Use --yes to skip.")
            return
        response = input("Remove these worktrees? [y/N] ").strip().lower()
        if response != "y":
            print("Cancelled")
            return

    # Remove worktrees
    for wt in to_clean:
        path = wt.get("path")
        branch = wt.get("branch")

        try:
            run_git(["worktree", "remove", path])
            print(f"✅ Removed: {path}")

            # Delete branch
            try:
                run_git(["branch", "-d", branch])
                print(f"✅ Deleted branch: {branch}")
            except subprocess.CalledProcessError:
                pass
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove {path}: {e}")

    # Prune stale entries
    run_git(["worktree", "prune"])
    print()
    print("Cleanup complete!")


def show_status(args):
    """Show worktree status overview."""
    worktrees = list_worktrees()
    config = load_config()

    print("Worktree Status")
    print("=" * 60)

    # Current directory
    cwd = os.getcwd()
    current_worktree = None

    for wt in worktrees:
        if os.path.samefile(cwd, wt.get("path", "")):
            current_worktree = wt
            break

    if current_worktree:
        print(f"Current: {current_worktree.get('path')}")
        print(f"Branch: {current_worktree.get('branch', 'detached')}")
    else:
        print(f"Current directory: {cwd}")
        print("(not in a worktree)")

    print()

    # Summary
    clean_count = 0
    dirty_count = 0

    for wt in worktrees:
        path = wt.get("path", "")
        if wt.get("bare"):
            continue

        try:
            status = subprocess.run(
                ["git", "-C", path, "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            if status.stdout.strip():
                dirty_count += 1
            else:
                clean_count += 1
        except subprocess.CalledProcessError:
            pass

    print(f"Total worktrees: {len(worktrees)}")
    print(f"  Clean: {clean_count}")
    print(f"  With changes: {dirty_count}")

    # Configuration
    print()
    print("Configuration:")
    wt_config = config.get("worktrees", {})
    print(f"  Enabled: {wt_config.get('enabled', True)}")
    print(f"  Base dir: {wt_config.get('baseDir', '../worktrees')}")

    auto_create = wt_config.get("autoCreate", {})
    if auto_create:
        auto_types = [k for k, v in auto_create.items() if v]
        if auto_types:
            print(f"  Auto-create for: {', '.join(auto_types)}")


def main():
    parser = argparse.ArgumentParser(
        description="Worktree Manager - Manage git worktrees for parallel development"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Create a worktree")
    add_parser.add_argument("branch", help="Branch for the worktree")
    add_parser.add_argument("--path", "-p", help="Custom path for worktree")
    add_parser.add_argument("--auto-path", "-a", action="store_true",
                          help="Auto-generate path from branch name")

    # List command
    subparsers.add_parser("list", help="List all worktrees")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a worktree")
    remove_parser.add_argument("name", help="Worktree name or path to remove")
    remove_parser.add_argument("--force", "-f", action="store_true",
                             help="Force remove even with changes")
    remove_parser.add_argument("--keep-branch", "-k", action="store_true",
                             help="Keep the branch after removing worktree")
    remove_parser.add_argument("--yes", "-y", action="store_true",
                             help="Skip confirmation prompts")

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean merged worktrees")
    clean_parser.add_argument("--dry-run", "-n", action="store_true",
                            help="Show what would be removed")
    clean_parser.add_argument("--yes", "-y", action="store_true",
                            help="Skip confirmation prompt")

    # Status command
    subparsers.add_parser("status", help="Show worktree status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "add":
            add_worktree(args)
        elif args.command == "list":
            list_worktrees_cmd(args)
        elif args.command == "remove":
            remove_worktree(args)
        elif args.command == "clean":
            clean_worktrees(args)
        elif args.command == "status":
            show_status(args)
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
