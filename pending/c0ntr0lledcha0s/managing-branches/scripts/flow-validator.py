#!/usr/bin/env python3
"""
Flow Validator - Validate branch names and flow compliance.

Commands:
  validate-name <branch-name>           - Validate a branch name
  check-flow <branch-name>              - Check flow compliance
  validate-merge <source> <target>      - Validate a merge is allowed
  report                                - Full validation report
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


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
            return ""
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
        "strategy": "gitflow",
        "branches": {
            "main": "main",
            "develop": "develop",
            "prefixes": {
                "feature": "feature/",
                "bugfix": "bugfix/",
                "hotfix": "hotfix/",
                "release": "release/"
            }
        },
        "naming": {
            "pattern": "{prefix}{issue?-}{name}",
            "requireIssue": False,
            "maxLength": 64,
            "allowedChars": "a-z0-9-"
        },
        "flows": {
            "feature": {"from": "develop", "to": "develop"},
            "bugfix": {"from": "develop", "to": "develop"},
            "hotfix": {"from": "main", "to": ["main", "develop"]},
            "release": {"from": "develop", "to": ["main", "develop"]}
        }
    }


def get_branch_type(branch: str, config: dict) -> Optional[str]:
    """Determine the type of a branch based on its name."""
    prefixes = config.get("branches", {}).get("prefixes", {})

    for branch_type, prefix in prefixes.items():
        if branch.startswith(prefix):
            return branch_type

    return None


def validate_branch_name(branch: str, config: dict) -> Tuple[bool, list, list]:
    """
    Validate a branch name against configuration.

    Returns: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    naming = config.get("naming", {})
    prefixes = config.get("branches", {}).get("prefixes", {})
    main_branch = config.get("branches", {}).get("main", "main")
    develop_branch = config.get("branches", {}).get("develop", "develop")

    # Check for protected branch names
    if branch in [main_branch, develop_branch]:
        return True, [], []  # These are valid system branches

    # Check max length
    max_length = naming.get("maxLength", 64)
    if len(branch) > max_length:
        errors.append(f"Branch name exceeds max length ({len(branch)} > {max_length})")

    # Check allowed characters
    allowed_chars = naming.get("allowedChars", "a-z0-9-")
    # Build regex from allowed chars specification
    if not re.match(f"^[{allowed_chars}/]+$", branch):
        errors.append(f"Branch name contains invalid characters (allowed: {allowed_chars})")

    # Check for uppercase
    if branch != branch.lower():
        errors.append("Branch name must be lowercase")

    # Check for underscores (common mistake)
    if "_" in branch:
        errors.append("Branch name should use hyphens (-) not underscores (_)")

    # Check if it starts with a known prefix
    has_prefix = False
    for branch_type, prefix in prefixes.items():
        if branch.startswith(prefix):
            has_prefix = True
            break

    if not has_prefix:
        errors.append(f"Branch name must start with a known prefix: {', '.join(prefixes.values())}")

    # Check for double hyphens or slashes
    if "--" in branch:
        warnings.append("Branch name contains double hyphens")
    if "//" in branch:
        errors.append("Branch name contains double slashes")

    # Check for trailing/leading hyphens
    parts = branch.split("/")
    for part in parts:
        if part.startswith("-") or part.endswith("-"):
            warnings.append(f"Branch segment '{part}' has leading/trailing hyphen")

    # Check for issue reference if required
    if naming.get("requireIssue", False):
        if not re.search(r"issue-\d+|#\d+|\d+-", branch):
            warnings.append("Branch name should include issue reference (e.g., issue-42)")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def check_flow_compliance(branch: str, config: dict) -> Tuple[bool, list, dict]:
    """
    Check if a branch follows the configured flow.

    Returns: (is_compliant, issues, flow_info)
    """
    issues = []
    flow_info = {}

    branch_type = get_branch_type(branch, config)
    if not branch_type:
        issues.append(f"Cannot determine branch type for '{branch}'")
        return False, issues, flow_info

    flows = config.get("flows", {})
    flow = flows.get(branch_type, {})

    if not flow:
        issues.append(f"No flow configured for branch type '{branch_type}'")
        return False, issues, flow_info

    flow_info = {
        "type": branch_type,
        "from": flow.get("from", "unknown"),
        "to": flow.get("to", "unknown"),
        "deleteAfterMerge": flow.get("deleteAfterMerge", False),
        "squashMerge": flow.get("squashMerge", False),
        "createTag": flow.get("createTag", False)
    }

    # Check if base branch exists
    base_branch = flow.get("from", "")
    if base_branch:
        try:
            run_git(["rev-parse", "--verify", base_branch])
        except subprocess.CalledProcessError:
            issues.append(f"Base branch '{base_branch}' does not exist")

    # Check branch age for trunk-based
    strategy = config.get("strategy", "")
    if strategy == "trunk-based":
        try:
            # Get branch creation date
            first_commit = run_git([
                "log", branch, "--reverse", "--format=%cr", "-1"
            ])
            if first_commit:
                # Simple check - if "weeks" or "months" in age, warn
                if "week" in first_commit or "month" in first_commit:
                    issues.append(f"Branch is too old for trunk-based development ({first_commit})")
        except subprocess.CalledProcessError:
            pass

    is_compliant = len(issues) == 0
    return is_compliant, issues, flow_info


def validate_merge(source: str, target: str, config: dict) -> Tuple[bool, list]:
    """
    Validate if a merge from source to target is allowed.

    Returns: (is_allowed, reasons)
    """
    reasons = []

    branch_type = get_branch_type(source, config)

    # Get protected branches
    main_branch = config.get("branches", {}).get("main", "main")
    develop_branch = config.get("branches", {}).get("develop", "develop")

    # Check if trying to merge TO a feature branch
    target_type = get_branch_type(target, config)
    if target_type and target_type in ["feature", "bugfix"]:
        reasons.append(f"Cannot merge into {target_type} branch")

    if not branch_type:
        # Unknown branch type - only warn, don't block
        reasons.append(f"Warning: '{source}' is not a recognized flow branch")
        return True, reasons

    flows = config.get("flows", {})
    flow = flows.get(branch_type, {})

    if not flow:
        reasons.append(f"No flow configured for branch type '{branch_type}'")
        return False, reasons

    # Get allowed targets
    allowed_targets = flow.get("to", [])
    if isinstance(allowed_targets, str):
        allowed_targets = [allowed_targets]

    # Check if target is allowed
    if target not in allowed_targets:
        reasons.append(
            f"{branch_type} branches should merge to {', '.join(allowed_targets)}, not '{target}'"
        )
        return False, reasons

    # Strategy-specific checks
    strategy = config.get("strategy", "gitflow")

    if strategy == "gitflow":
        # Prevent feature → main (should go to develop first)
        if branch_type == "feature" and target == main_branch:
            reasons.append("Feature branches should merge to develop, not main")
            return False, reasons

        # Prevent develop → main (should use release branch)
        if source == develop_branch and target == main_branch:
            reasons.append("Use a release branch to merge develop to main")
            return False, reasons

    elif strategy == "github-flow":
        # Everything goes to main
        if target != main_branch:
            reasons.append("In GitHub Flow, branches should merge to main")
            return False, reasons

    # Check policies
    policies = config.get("policies", {})

    # Check PR requirements
    if target == main_branch and policies.get("requirePRForMain", False):
        reasons.append(f"Merging to {main_branch} requires a Pull Request")

    if target == develop_branch and policies.get("requirePRForDevelop", False):
        reasons.append(f"Merging to {develop_branch} requires a Pull Request")

    is_allowed = not any("should" in r or "Cannot" in r or "requires" in r for r in reasons)
    return is_allowed, reasons


def generate_report(args):
    """Generate a full validation report for the repository."""
    config = load_config()

    print("Branch Validation Report")
    print("=" * 50)
    print()

    # Show configuration
    print("Configuration:")
    print(f"  Strategy: {config.get('strategy', 'unknown')}")
    print(f"  Main branch: {config.get('branches', {}).get('main', 'main')}")
    print(f"  Develop branch: {config.get('branches', {}).get('develop', 'develop')}")
    print()

    # Get all branches
    branches = run_git(["branch", "--list"]).split("\n")
    branches = [b.strip().lstrip("* ") for b in branches if b.strip()]

    # Validate each branch
    print("Branch Validation:")
    print("-" * 50)

    valid_count = 0
    invalid_count = 0
    warning_count = 0

    for branch in branches:
        is_valid, errors, warnings = validate_branch_name(branch, config)

        if errors:
            print(f"❌ {branch}")
            for error in errors:
                print(f"   Error: {error}")
            invalid_count += 1
        elif warnings:
            print(f"⚠️  {branch}")
            for warning in warnings:
                print(f"   Warning: {warning}")
            warning_count += 1
            valid_count += 1
        else:
            print(f"✅ {branch}")
            valid_count += 1

    print()
    print("Flow Compliance:")
    print("-" * 50)

    for branch in branches:
        is_compliant, issues, flow_info = check_flow_compliance(branch, config)

        if flow_info:
            status = "✅" if is_compliant else "⚠️ "
            print(f"{status} {branch}")
            print(f"   Type: {flow_info.get('type', 'unknown')}")
            print(f"   Flow: {flow_info.get('from')} → {flow_info.get('to')}")
            for issue in issues:
                print(f"   Issue: {issue}")
        else:
            print(f"   {branch}: Not a flow branch")

    print()
    print("Summary:")
    print(f"  Valid branches: {valid_count}")
    print(f"  Invalid branches: {invalid_count}")
    print(f"  Warnings: {warning_count}")

    # Recommendations
    if invalid_count > 0 or warning_count > 0:
        print()
        print("Recommendations:")
        if invalid_count > 0:
            print("  - Rename invalid branches to follow conventions")
        if warning_count > 0:
            print("  - Consider addressing warnings for consistency")


def main():
    parser = argparse.ArgumentParser(
        description="Flow Validator - Validate branch names and flow compliance"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Validate name command
    name_parser = subparsers.add_parser("validate-name", help="Validate a branch name")
    name_parser.add_argument("branch", help="Branch name to validate")

    # Check flow command
    flow_parser = subparsers.add_parser("check-flow", help="Check flow compliance")
    flow_parser.add_argument("branch", help="Branch to check")

    # Validate merge command
    merge_parser = subparsers.add_parser("validate-merge", help="Validate a merge")
    merge_parser.add_argument("source", help="Source branch")
    merge_parser.add_argument("target", help="Target branch")

    # Report command
    subparsers.add_parser("report", help="Generate full validation report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config()

    if args.command == "validate-name":
        is_valid, errors, warnings = validate_branch_name(args.branch, config)

        if is_valid:
            print(f"✅ Valid: {args.branch}")
        else:
            print(f"❌ Invalid: {args.branch}")

        for error in errors:
            print(f"   Error: {error}")
        for warning in warnings:
            print(f"   Warning: {warning}")

        sys.exit(0 if is_valid else 1)

    elif args.command == "check-flow":
        is_compliant, issues, flow_info = check_flow_compliance(args.branch, config)

        if is_compliant:
            print(f"✅ Compliant: {args.branch}")
        else:
            print(f"⚠️  Issues found: {args.branch}")

        if flow_info:
            print(f"   Type: {flow_info.get('type', 'unknown')}")
            print(f"   Base: {flow_info.get('from', 'unknown')}")
            print(f"   Target: {flow_info.get('to', 'unknown')}")
            print(f"   Delete after merge: {flow_info.get('deleteAfterMerge', False)}")
            print(f"   Create tag: {flow_info.get('createTag', False)}")

        for issue in issues:
            print(f"   Issue: {issue}")

        sys.exit(0 if is_compliant else 1)

    elif args.command == "validate-merge":
        is_allowed, reasons = validate_merge(args.source, args.target, config)

        if is_allowed:
            print(f"✅ Merge allowed: {args.source} → {args.target}")
        else:
            print(f"❌ Merge not allowed: {args.source} → {args.target}")

        for reason in reasons:
            print(f"   {reason}")

        sys.exit(0 if is_allowed else 1)

    elif args.command == "report":
        generate_report(args)


if __name__ == "__main__":
    main()
