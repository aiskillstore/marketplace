#!/usr/bin/env python3
"""
Branch Manager - Core branch operations for the managing-branches skill.

Commands:
  start <type> <name> [--issue N]  - Start a new branch
  finish [branch-name] [--current] - Finish/merge a branch
  status                           - Show current branch status
  list [type] [--all]              - List branches by type
  clean [--dry-run]                - Clean merged branches
  config --show|--set              - View or update configuration
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
        if capture:
            print(f"Error: {e.stderr.strip()}", file=sys.stderr)
        raise


def get_config_path() -> Path:
    """Get the branching config file path."""
    # Check for project-level config first
    git_root = run_git(["rev-parse", "--show-toplevel"])
    config_path = Path(git_root) / ".claude" / "github-workflows" / "branching-config.json"
    return config_path


def load_config() -> dict:
    """Load the branching configuration."""
    config_path = get_config_path()

    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    # Return default gitflow config
    return {
        "version": "1.0.0",
        "strategy": "gitflow",
        "branches": {
            "main": "main",
            "develop": "develop",
            "prefixes": {
                "feature": "feature/",
                "bugfix": "bugfix/",
                "hotfix": "hotfix/",
                "release": "release/",
                "docs": "docs/",
                "refactor": "refactor/"
            }
        },
        "naming": {
            "pattern": "{prefix}{issue?-}{name}",
            "requireIssue": False,
            "maxLength": 64,
            "allowedChars": "a-z0-9-"
        },
        "flows": {
            "feature": {
                "from": "develop",
                "to": "develop",
                "deleteAfterMerge": True,
                "squashMerge": False
            },
            "bugfix": {
                "from": "develop",
                "to": "develop",
                "deleteAfterMerge": True,
                "squashMerge": False
            },
            "hotfix": {
                "from": "main",
                "to": ["main", "develop"],
                "deleteAfterMerge": True,
                "createTag": True
            },
            "release": {
                "from": "develop",
                "to": ["main", "develop"],
                "deleteAfterMerge": True,
                "createTag": True
            }
        },
        "worktrees": {
            "enabled": True,
            "baseDir": "../worktrees",
            "autoCreate": {
                "hotfix": True,
                "release": True
            }
        },
        "policies": {
            "requirePRForMain": True,
            "preventDirectPush": ["main"]
        }
    }


def save_config(config: dict):
    """Save the branching configuration."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Configuration saved to: {config_path}")


def get_current_branch() -> str:
    """Get the current branch name."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def branch_exists(branch: str, remote: bool = False) -> bool:
    """Check if a branch exists."""
    try:
        if remote:
            run_git(["rev-parse", "--verify", f"origin/{branch}"])
        else:
            run_git(["rev-parse", "--verify", branch])
        return True
    except subprocess.CalledProcessError:
        return False


def get_branch_type(branch: str, config: dict) -> Optional[str]:
    """Determine the type of a branch based on its name."""
    prefixes = config.get("branches", {}).get("prefixes", {})

    for branch_type, prefix in prefixes.items():
        if branch.startswith(prefix):
            return branch_type

    return None


def generate_branch_name(branch_type: str, name: str, issue: Optional[int], config: dict) -> str:
    """Generate a branch name following conventions."""
    prefixes = config.get("branches", {}).get("prefixes", {})
    prefix = prefixes.get(branch_type, f"{branch_type}/")

    # Store original for error message
    original_name = name

    # Clean the name
    name = name.lower().replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-z0-9-]", "", name)
    name = name.strip("-")  # Remove leading/trailing hyphens

    # Validate name is not empty after cleaning
    if not name:
        raise ValueError(f"Branch name cannot be empty after cleaning: '{original_name}'")

    # Build branch name
    if issue:
        branch_name = f"{prefix}issue-{issue}-{name}"
    else:
        branch_name = f"{prefix}{name}"

    # Enforce max length
    max_length = config.get("naming", {}).get("maxLength", 64)
    if len(branch_name) > max_length:
        branch_name = branch_name[:max_length].rstrip("-")

    return branch_name


def start_branch(args):
    """Start a new branch following the configured flow."""
    config = load_config()
    strategy = config.get("strategy", "gitflow")

    branch_type = args.type
    name = args.name
    issue = args.issue

    # Validate branch type
    flows = config.get("flows", {})
    if branch_type not in flows:
        print(f"Error: Unknown branch type '{branch_type}'")
        print(f"Available types: {', '.join(flows.keys())}")
        sys.exit(1)

    flow = flows[branch_type]
    base_branch = flow.get("from", "main")

    # For github-flow, base is always main
    if strategy == "github-flow":
        base_branch = config.get("branches", {}).get("main", "main")

    # Generate branch name
    branch_name = generate_branch_name(branch_type, name, issue, config)

    print(f"Starting {branch_type} branch: {branch_name}")
    print(f"Base branch: {base_branch}")
    print()

    # Ensure we're on the base branch and it's up to date
    current = get_current_branch()
    if current != base_branch:
        print(f"Switching to {base_branch}...")
        run_git(["checkout", base_branch])

    print(f"Updating {base_branch} from origin...")
    try:
        run_git(["pull", "origin", base_branch])
    except subprocess.CalledProcessError:
        print(f"Warning: Could not pull from origin/{base_branch}")

    # Create the new branch
    print(f"Creating branch: {branch_name}")
    run_git(["checkout", "-b", branch_name])

    print()
    print(f"✅ Branch created: {branch_name}")
    print(f"✅ Based on: {base_branch}")

    if issue:
        print(f"✅ Linked to: #{issue}")

    print()
    print("Next steps:")
    print("1. Make your changes")
    print(f"2. Commit with: {get_commit_type(branch_type)}(scope): description")
    if issue:
        print(f"3. Reference issue: Refs #{issue}")
    print(f"4. When done: branch-manager.py finish {branch_name}")


def get_commit_type(branch_type: str) -> str:
    """Get the conventional commit type for a branch type."""
    mapping = {
        "feature": "feat",
        "bugfix": "fix",
        "hotfix": "fix",
        "docs": "docs",
        "refactor": "refactor",
        "release": "chore"
    }
    return mapping.get(branch_type, "feat")


def finish_branch(args):
    """Finish a branch by merging it following the configured flow."""
    config = load_config()

    # Determine which branch to finish
    if args.current:
        branch_name = get_current_branch()
    elif args.branch:
        branch_name = args.branch
    else:
        branch_name = get_current_branch()

    # Determine branch type
    branch_type = get_branch_type(branch_name, config)
    if not branch_type:
        print(f"Error: Cannot determine type for branch '{branch_name}'")
        print("Branch should start with a known prefix (feature/, bugfix/, etc.)")
        sys.exit(1)

    flows = config.get("flows", {})
    flow = flows.get(branch_type, {})

    target = flow.get("to", "develop")
    delete_after = flow.get("deleteAfterMerge", True)
    squash = flow.get("squashMerge", False)
    create_tag = flow.get("createTag", False)

    # Handle multiple targets (like hotfix → main AND develop)
    targets = [target] if isinstance(target, str) else target

    print(f"Finishing {branch_type} branch: {branch_name}")
    print(f"Target(s): {', '.join(targets)}")
    print()

    # Check for uncommitted changes
    status = run_git(["status", "--porcelain"])
    if status:
        print("Error: You have uncommitted changes")
        print("Please commit or stash them first")
        sys.exit(1)

    # Merge to each target
    for target_branch in targets:
        print(f"Merging to {target_branch}...")

        # Update target branch
        run_git(["checkout", target_branch])
        try:
            run_git(["pull", "origin", target_branch])
        except subprocess.CalledProcessError:
            print(f"Warning: Could not pull from origin/{target_branch}")

        # Merge
        merge_args = ["merge"]
        if not squash:
            merge_args.append("--no-ff")
        else:
            merge_args.append("--squash")
        merge_args.append(branch_name)

        run_git(merge_args)

        if squash:
            # Need to commit after squash
            run_git(["commit", "-m", f"Merge {branch_name} into {target_branch}"])

        # Push
        print(f"Pushing {target_branch} to origin...")
        run_git(["push", "origin", target_branch])

        print(f"✅ Merged to {target_branch}")

    # Create tag if needed
    if create_tag:
        # Extract version from branch name
        version_match = re.search(r"(\d+\.\d+\.\d+)", branch_name)
        if version_match:
            version = version_match.group(1)
            tag_name = f"v{version}"
            print(f"Creating tag: {tag_name}")
            run_git(["tag", "-a", tag_name, "-m", f"Release {version}"])
            run_git(["push", "origin", tag_name])
            print(f"✅ Created tag: {tag_name}")

    # Delete branch if configured
    if delete_after:
        print(f"Deleting branch: {branch_name}")

        # Delete local
        run_git(["branch", "-d", branch_name])

        # Delete remote
        try:
            run_git(["push", "origin", "--delete", branch_name])
            print(f"✅ Deleted remote branch")
        except subprocess.CalledProcessError:
            print("Note: Remote branch may not exist or already deleted")

        print(f"✅ Deleted local branch")

    print()
    print(f"✅ Branch {branch_name} completed!")


def show_status(args):
    """Show current branch status and flow information."""
    config = load_config()

    current = get_current_branch()
    branch_type = get_branch_type(current, config)

    print("Branch Status")
    print("=" * 40)
    print(f"Current branch: {current}")
    print(f"Strategy: {config.get('strategy', 'unknown')}")

    if branch_type:
        print(f"Branch type: {branch_type}")
        flow = config.get("flows", {}).get(branch_type, {})
        print(f"Base: {flow.get('from', 'unknown')}")
        print(f"Target: {flow.get('to', 'unknown')}")
    else:
        print(f"Branch type: (not a flow branch)")

    print()

    # Show uncommitted changes
    status = run_git(["status", "--short"])
    if status:
        print("Uncommitted changes:")
        print(status)
    else:
        print("Working directory clean")

    print()

    # Show recent commits on this branch
    try:
        main_branch = config.get("branches", {}).get("main", "main")
        commits = run_git(["log", f"{main_branch}..HEAD", "--oneline", "-5"])
        if commits:
            print(f"Recent commits (since {main_branch}):")
            print(commits)
        else:
            print(f"No commits ahead of {main_branch}")
    except subprocess.CalledProcessError:
        pass

    print()

    # Show related branches
    prefixes = config.get("branches", {}).get("prefixes", {})
    print("Active branches by type:")

    all_branches = run_git(["branch", "--list"]).split("\n")
    for branch_type, prefix in prefixes.items():
        matching = [b.strip().lstrip("* ") for b in all_branches if prefix in b]
        if matching:
            print(f"  {branch_type}: {len(matching)}")
            for b in matching[:3]:
                print(f"    - {b}")
            if len(matching) > 3:
                print(f"    ... and {len(matching) - 3} more")


def list_branches(args):
    """List branches by type."""
    config = load_config()
    prefixes = config.get("branches", {}).get("prefixes", {})

    all_branches = run_git(["branch", "--list", "-a"]).split("\n")
    all_branches = [b.strip().lstrip("* ") for b in all_branches if b.strip()]

    if args.all:
        # Show all branches grouped by type
        print("All branches by type:")
        print("=" * 40)

        for branch_type, prefix in prefixes.items():
            matching = [b for b in all_branches if f"/{prefix}" in b or b.startswith(prefix)]
            if matching:
                print(f"\n{branch_type.upper()} ({len(matching)}):")
                for b in matching:
                    print(f"  - {b}")

        # Show unmatched
        matched = set()
        for prefix in prefixes.values():
            for b in all_branches:
                if f"/{prefix}" in b or b.startswith(prefix):
                    matched.add(b)

        unmatched = [b for b in all_branches if b not in matched]
        if unmatched:
            print(f"\nOTHER ({len(unmatched)}):")
            for b in unmatched:
                print(f"  - {b}")

    elif args.type:
        # Show specific type
        prefix = prefixes.get(args.type)
        if not prefix:
            print(f"Error: Unknown branch type '{args.type}'")
            print(f"Available types: {', '.join(prefixes.keys())}")
            sys.exit(1)

        matching = [b for b in all_branches if f"/{prefix}" in b or b.startswith(prefix)]

        print(f"{args.type.upper()} branches ({len(matching)}):")
        for b in matching:
            # Get additional info
            try:
                age = run_git(["log", "-1", "--format=%cr", b.replace("remotes/origin/", "")])
                print(f"  - {b} ({age})")
            except subprocess.CalledProcessError:
                print(f"  - {b}")

    else:
        # Show summary
        print("Branch summary:")
        print("=" * 40)

        for branch_type, prefix in prefixes.items():
            matching = [b for b in all_branches if f"/{prefix}" in b or b.startswith(prefix)]
            count = len(matching)
            if count > 0:
                print(f"{branch_type}: {count}")

        print()
        print("Use --all for full list or specify type")


def clean_branches(args):
    """Clean up merged branches."""
    config = load_config()

    main_branch = config.get("branches", {}).get("main", "main")
    develop_branch = config.get("branches", {}).get("develop", "develop")

    print("Checking for merged branches...")
    print()

    # Get merged branches
    try:
        merged = run_git(["branch", "--merged", main_branch]).split("\n")
        merged = [b.strip().lstrip("* ") for b in merged if b.strip()]
    except subprocess.CalledProcessError:
        merged = []

    # Filter out protected branches
    protected = {main_branch, develop_branch, "HEAD"}
    to_delete = [b for b in merged if b not in protected and not b.startswith("remotes/")]

    if not to_delete:
        print("No merged branches to clean")
        return

    print(f"Found {len(to_delete)} merged branch(es):")
    for b in to_delete:
        print(f"  - {b}")

    print()

    if args.dry_run:
        print("Dry run - no branches deleted")
        return

    # Confirm deletion (skip if --yes flag or non-interactive)
    if not args.yes:
        if not sys.stdin.isatty():
            print("Error: Cannot prompt for confirmation in non-interactive mode")
            print("Use --yes flag to skip confirmation")
            return
        response = input("Delete these branches? [y/N] ").strip().lower()
        if response != "y":
            print("Cancelled")
            return

    # Delete branches
    for b in to_delete:
        try:
            run_git(["branch", "-d", b])
            print(f"✅ Deleted: {b}")

            # Try to delete remote
            try:
                run_git(["push", "origin", "--delete", b], check=False)
            except subprocess.CalledProcessError:
                pass
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to delete {b}: {e}")

    print()
    print("Cleanup complete!")


def show_config(args):
    """Show or update configuration."""
    config = load_config()

    if args.show:
        print("Branching Configuration")
        print("=" * 40)
        print(json.dumps(config, indent=2))

    elif args.set:
        # Parse key=value
        if "=" not in args.set:
            print("Error: Use format key=value")
            sys.exit(1)

        key, value = args.set.split("=", 1)

        # Handle nested keys
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Try to parse as JSON for complex values
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

        current[keys[-1]] = value
        save_config(config)
        print(f"Set {key} = {value}")

    elif args.init:
        # Initialize with template
        strategy = args.init
        templates_file = Path(__file__).parent.parent / "assets" / "templates" / "branching-config-templates.json"

        if templates_file.exists():
            with open(templates_file) as f:
                templates = json.load(f)

            if strategy in templates.get("templates", {}):
                template = templates["templates"][strategy]
                config = template.get("config", {})
                save_config(config)
                print(f"Initialized with {strategy} configuration")
            else:
                print(f"Error: Unknown strategy '{strategy}'")
                print(f"Available: {', '.join(templates.get('templates', {}).keys())}")
                sys.exit(1)
        else:
            print("Error: Templates file not found")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Branch Manager - Manage branches following configured flow"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a new branch")
    start_parser.add_argument("type", help="Branch type (feature, bugfix, hotfix, release)")
    start_parser.add_argument("name", help="Branch name/description")
    start_parser.add_argument("--issue", "-i", type=int, help="Related issue number")

    # Finish command
    finish_parser = subparsers.add_parser("finish", help="Finish a branch")
    finish_parser.add_argument("branch", nargs="?", help="Branch to finish")
    finish_parser.add_argument("--current", "-c", action="store_true", help="Finish current branch")

    # Status command
    subparsers.add_parser("status", help="Show branch status")

    # List command
    list_parser = subparsers.add_parser("list", help="List branches")
    list_parser.add_argument("type", nargs="?", help="Branch type to list")
    list_parser.add_argument("--all", "-a", action="store_true", help="Show all branches")

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean merged branches")
    clean_parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be deleted")
    clean_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # Config command
    config_parser = subparsers.add_parser("config", help="View or update configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--set", help="Set a configuration value (key=value)")
    config_parser.add_argument("--init", help="Initialize with a strategy template")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "start":
            start_branch(args)
        elif args.command == "finish":
            finish_branch(args)
        elif args.command == "status":
            show_status(args)
        elif args.command == "list":
            list_branches(args)
        elif args.command == "clean":
            clean_branches(args)
        elif args.command == "config":
            show_config(args)
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
