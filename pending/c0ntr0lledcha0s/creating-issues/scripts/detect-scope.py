#!/usr/bin/env python3
"""
Detect Scope - Automatically detect scope label from context.

Usage:
    python detect-scope.py              # Auto-detect scope
    python detect-scope.py --list       # List available scopes
    python detect-scope.py --validate "scope:name"  # Validate scope exists

Returns:
    Detected scope label (e.g., "scope:github-workflows") or empty if not detected.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ENV_FILE = ".claude/github-workflows/env.json"


def load_environment():
    """Load environment from env.json."""
    env_path = Path(ENV_FILE)
    if not env_path.exists():
        return None

    try:
        with open(env_path) as f:
            return json.load(f)
    except Exception:
        return None


def get_current_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def get_suggested_scopes(env=None):
    """Get suggested scopes from environment or project structure."""
    if env:
        return env.get("labels", {}).get("suggestedScopes", [])

    # Fallback: analyze project structure
    scopes = []

    # Check for plugin directories
    try:
        for item in Path(".").iterdir():
            if item.is_dir():
                if (item / "plugin.json").exists():
                    scopes.append(item.name)
                elif (item / ".claude-plugin" / "plugin.json").exists():
                    scopes.append(item.name)
    except Exception:
        pass

    # Check git-conventional-commits.json
    config_path = Path("git-conventional-commits.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                data = json.load(f)
                configured = data.get("convention", {}).get("commitScopes", [])
                if configured:
                    return configured
        except Exception:
            pass

    return scopes


def detect_from_environment(env):
    """Detect scope from environment settings."""
    if not env:
        return None

    # Check branch.scopeLabel
    scope_label = env.get("branch", {}).get("scopeLabel")
    if scope_label:
        return scope_label

    return None


def detect_from_branch(branch, suggested_scopes):
    """Detect scope by matching branch name to suggested scopes."""
    if not branch or not suggested_scopes:
        return None

    branch_lower = branch.lower()

    # Direct match
    for scope in suggested_scopes:
        scope_lower = scope.lower()
        if scope_lower in branch_lower:
            return f"scope:{scope}"

    # Pattern matching
    patterns = [
        r"^(?:feature|fix|plugin|bugfix|hotfix)/([a-z0-9-]+)",
        r"^([a-z0-9-]+)/",
    ]

    for pattern in patterns:
        match = re.search(pattern, branch_lower)
        if match:
            potential = match.group(1).split("-")[0]
            for scope in suggested_scopes:
                if potential == scope.lower():
                    return f"scope:{scope}"

    return None


def detect_scope():
    """
    Detect scope from multiple sources with priority:
    1. Environment settings (branch.scopeLabel)
    2. Branch name matching suggested scopes
    3. Return None if cannot detect
    """
    env = load_environment()
    suggested_scopes = get_suggested_scopes(env)

    # 1. Check environment
    scope = detect_from_environment(env)
    if scope:
        return scope, "environment", suggested_scopes

    # 2. Check branch name
    branch = get_current_branch()
    if branch:
        scope = detect_from_branch(branch, suggested_scopes)
        if scope:
            return scope, "branch", suggested_scopes

    return None, None, suggested_scopes


def list_scopes():
    """List all available scopes."""
    env = load_environment()
    scopes = get_suggested_scopes(env)

    if not scopes:
        print("No scopes detected. Run /github-workflows:init to analyze project structure.")
        return

    print("Available scopes:")
    for scope in sorted(scopes):
        print(f"  scope:{scope}")


def validate_scope(scope_label):
    """Validate that a scope label is in the suggested list."""
    env = load_environment()
    scopes = get_suggested_scopes(env)

    # Extract scope name from label
    scope_name = scope_label.replace("scope:", "")

    if scope_name.lower() in [s.lower() for s in scopes]:
        print(f"✅ Valid scope: {scope_label}")
        return True
    else:
        print(f"⚠️ Unknown scope: {scope_label}")
        print("\nAvailable scopes:")
        for scope in sorted(scopes):
            print(f"  scope:{scope}")
        return False


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--list":
            list_scopes()
            return

        if arg == "--validate":
            if len(sys.argv) < 3:
                print("Usage: detect-scope.py --validate <scope-label>")
                sys.exit(1)
            success = validate_scope(sys.argv[2])
            sys.exit(0 if success else 1)

        # Unknown argument
        print(f"Unknown argument: {arg}")
        print(__doc__)
        sys.exit(1)

    # Default: detect scope
    scope, source, suggested = detect_scope()

    if scope:
        print(f"Detected: {scope}")
        print(f"Source: {source}")
    else:
        print("Could not auto-detect scope.")
        if suggested:
            print("\nAvailable scopes:")
            for s in sorted(suggested):
                print(f"  scope:{s}")
        else:
            print("No scopes configured. Run /github-workflows:init to analyze project structure.")
        sys.exit(1)


if __name__ == "__main__":
    main()
