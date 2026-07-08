#!/usr/bin/env python3
"""
Issue Tracker - Sync and cache GitHub issues for commit integration.

Usage:
    python issue-tracker.py sync [filter] [value]   # Sync issues from GitHub
    python issue-tracker.py show                    # Display cached issues
    python issue-tracker.py context                 # Show issues filtered by context
    python issue-tracker.py scope                   # Show issues matching branch scope
    python issue-tracker.py branch                  # Show only branch-selected issues
    python issue-tracker.py select <numbers...>     # Select issues for current branch
    python issue-tracker.py find-related [files...] # Find related issues
    python issue-tracker.py get [number]            # Get specific issue
    python issue-tracker.py suggest-refs            # Suggest issue refs for staged changes
    python issue-tracker.py clear                   # Clear the cache
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Cache file location (in .claude for project-specific storage)
CACHE_DIR = ".claude/github-workflows"
CACHE_FILE = "active-issues.json"

def get_cache_path():
    """Get the cache file path, creating directory if needed."""
    cache_dir = Path(CACHE_DIR)
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / CACHE_FILE

def run_gh_command(args):
    """Run a GitHub CLI command and return JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return None

def get_repo_info():
    """Get current repository owner/name."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        data = json.loads(result.stdout)
        return data.get("nameWithOwner", "unknown/unknown")
    except Exception:
        return "unknown/unknown"

def sync_issues(filter_type="assigned", filter_value=None):
    """Sync issues from GitHub based on filter."""
    args = ["issue", "list", "--state", "open", "--json",
            "number,title,state,labels,assignees,milestone,createdAt,updatedAt,url,body"]

    if filter_type == "assigned":
        args.extend(["--assignee", "@me"])
    elif filter_type == "labeled" and filter_value:
        args.extend(["--label", filter_value])
    elif filter_type == "milestone" and filter_value:
        args.extend(["--milestone", filter_value])
    elif filter_type == "all":
        pass  # No additional filters
    else:
        args.extend(["--assignee", "@me"])  # Default to assigned

    print(f"Syncing issues (filter: {filter_type})...", file=sys.stderr)
    issues = run_gh_command(args)

    if issues is None:
        return False

    # Process issues
    processed = []
    for issue in issues:
        processed.append({
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "state": issue.get("state", "open"),
            "labels": [l.get("name", "") for l in issue.get("labels", [])],
            "assignees": [a.get("login", "") for a in issue.get("assignees", [])],
            "milestone": issue.get("milestone", {}).get("title") if issue.get("milestone") else None,
            "created_at": issue.get("createdAt", ""),
            "updated_at": issue.get("updatedAt", ""),
            "url": issue.get("url", ""),
            "body_preview": (issue.get("body", "") or "")[:500]
        })

    # Save to cache
    cache_data = {
        "lastSync": datetime.now(timezone.utc).isoformat(),
        "repository": get_repo_info(),
        "filter": filter_type,
        "filterValue": filter_value,
        "issues": processed
    }

    cache_path = get_cache_path()
    with open(cache_path, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"Cached {len(processed)} issues to {cache_path}", file=sys.stderr)
    return True

def load_cache():
    """Load issues from cache."""
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None

    try:
        with open(cache_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}", file=sys.stderr)
        return None


def load_environment():
    """Load environment from env.json."""
    env_path = Path(CACHE_DIR) / "env.json"
    if not env_path.exists():
        return None

    try:
        with open(env_path) as f:
            return json.load(f)
    except Exception:
        return None


def filter_by_scope(issues, scope_label):
    """Filter issues by scope label."""
    if not scope_label:
        return issues

    # Extract scope name for exact matching
    scope_name = scope_label.replace("scope:", "")

    return [
        issue for issue in issues
        if scope_label in issue.get("labels", []) or
           f"scope:{scope_name}" in issue.get("labels", []) or
           scope_name in issue.get("labels", [])  # Exact match only, no substring
    ]


def filter_by_project(issues, project_number):
    """Filter issues that are in a specific project board."""
    if not project_number:
        return issues

    # Get issues from project via GraphQL
    env = load_environment()
    if not env:
        print("Warning: No environment loaded, skipping project filtering", file=sys.stderr)
        return issues

    owner = env.get("user", {}).get("login", "")
    if not owner:
        print("Warning: No user login in environment, skipping project filtering", file=sys.stderr)
        return issues

    # Also get repository owner for org projects
    repo_owner = env.get("repository", {}).get("owner", "")

    def try_query(query_owner, is_org=False):
        """Try to query project items for user or org."""
        if is_org:
            query = '''
            query($owner: String!, $number: Int!) {
                organization(login: $owner) {
                    projectV2(number: $number) {
                        items(first: 100) {
                            nodes {
                                content {
                                    ... on Issue {
                                        number
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''
        else:
            query = '''
            query($owner: String!, $number: Int!) {
                user(login: $owner) {
                    projectV2(number: $number) {
                        items(first: 100) {
                            nodes {
                                content {
                                    ... on Issue {
                                        number
                                    }
                                }
                            }
                        }
                    }
                }
            }
            '''

        result = subprocess.run(
            ["gh", "api", "graphql",
             "-f", f"query={query}",
             "-f", f"owner={query_owner}",
             "-F", f"number={project_number}"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            return None, result.stderr

        data = json.loads(result.stdout)

        # Check for errors in response
        if data.get("errors"):
            error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
            return None, error_msg

        # Extract items based on query type
        if is_org:
            items = data.get("data", {}).get("organization", {}).get("projectV2", {}).get("items", {}).get("nodes", [])
        else:
            items = data.get("data", {}).get("user", {}).get("projectV2", {}).get("items", {}).get("nodes", [])

        return items, None

    # Try user project first
    items, error = try_query(owner, is_org=False)

    # If user query failed and we have a different repo owner, try org
    if items is None and repo_owner and repo_owner != owner:
        items, error = try_query(repo_owner, is_org=True)

    # If still no items, log the error
    if items is None:
        print(f"Warning: Project filtering failed: {error}", file=sys.stderr)
        print("Troubleshooting: Check that project #{} exists and you have access".format(project_number), file=sys.stderr)
        return issues

    # Extract issue numbers
    project_issues = set()
    for item in items:
        content = item.get("content", {})
        if content and content.get("number"):
            project_issues.add(content["number"])

    return [issue for issue in issues if issue["number"] in project_issues]


def filter_by_assignment(issues, user_login):
    """Filter issues assigned to a specific user."""
    if not user_login:
        return issues

    return [
        issue for issue in issues
        if user_login in issue.get("assignees", [])
    ]


def apply_context_filters(issues, env):
    """Apply contextual filters based on environment settings."""
    if not env:
        return issues

    filtered = issues

    # Filter by project if set
    default_project = env.get("preferences", {}).get("defaultProject")
    if default_project:
        filtered = filter_by_project(filtered, default_project)

    # Filter by detected scope if available
    scope_label = env.get("branch", {}).get("scopeLabel")
    if scope_label:
        scope_filtered = filter_by_scope(filtered, scope_label)
        # Only apply if it doesn't filter everything out
        if scope_filtered:
            filtered = scope_filtered

    # Filter by assignment for team projects
    project_type = env.get("preferences", {}).get("projectType")
    if project_type == "team":
        user_login = env.get("user", {}).get("login")
        if user_login:
            filtered = filter_by_assignment(filtered, user_login)

    return filtered


def get_branch_issues():
    """Get issues related to current branch from env.json."""
    env = load_environment()
    if not env:
        return []

    return env.get("branch", {}).get("relatedIssues", [])

def show_issues():
    """Display cached issues as a task list."""
    cache = load_cache()

    if not cache:
        print("No cached issues. Run: python issue-tracker.py sync")
        return

    # Check cache age
    last_sync = datetime.fromisoformat(cache["lastSync"].replace("Z", "+00:00"))
    age_minutes = (datetime.now(timezone.utc) - last_sync).total_seconds() / 60

    if age_minutes > 60:
        print(f"⚠️  Cache is {int(age_minutes)} minutes old. Consider running: sync")
        print()

    print(f"📋 Active Issues (synced {int(age_minutes)} minutes ago)")
    print(f"Repository: {cache['repository']}")
    print(f"Filter: {cache['filter']}")
    if cache.get('filterValue'):
        print(f"Value: {cache['filterValue']}")
    print()

    issues = cache.get("issues", [])
    if not issues:
        print("No issues found.")
        return

    # Sort by priority
    high_priority = []
    normal = []

    for issue in issues:
        labels = issue.get("labels", [])
        is_high = any("high" in l.lower() for l in labels)
        if is_high:
            high_priority.append(issue)
        else:
            normal.append(issue)

    def print_issue(issue):
        labels = ", ".join(issue.get("labels", [])) or "none"
        milestone = issue.get("milestone") or "none"
        print(f"┌─ #{issue['number']} {issue['title']}")
        print(f"│  Labels: {labels}")
        if milestone != "none":
            print(f"│  Milestone: {milestone}")
        print(f"└─ Use: Closes #{issue['number']} or Refs #{issue['number']}")
        print()

    if high_priority:
        print("HIGH PRIORITY:")
        for issue in high_priority:
            print_issue(issue)

    if normal:
        print("NORMAL PRIORITY:")
        for issue in normal:
            print_issue(issue)

    print("💡 Tip: Use /commit-smart to auto-suggest these in commits")

def get_current_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def extract_issue_from_branch(branch_name):
    """Extract issue number from branch name."""
    if not branch_name:
        return None

    # Patterns: feature/issue-42, feature/42-auth, fix/42, 42-something
    patterns = [
        r"issue-(\d+)",
        r"/(\d+)-",
        r"^(\d+)-",
        r"-(\d+)$"
    ]

    for pattern in patterns:
        match = re.search(pattern, branch_name)
        if match:
            return int(match.group(1))

    return None

def find_related_issues(files=None):
    """Find issues related to given files or staged changes."""
    cache = load_cache()
    if not cache:
        print("No cached issues. Run sync first.", file=sys.stderr)
        return []

    issues = cache.get("issues", [])
    if not issues:
        return []

    # Get files to analyze
    if not files:
        # Get staged files
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        except Exception:
            files = []

    # Score each issue
    scored = []
    branch = get_current_branch()
    branch_issue = extract_issue_from_branch(branch)

    # Get all related issues from env.json
    env = load_environment()
    branch_related_issues = env.get("branch", {}).get("relatedIssues", []) if env else []
    detected_scope = env.get("branch", {}).get("scopeLabel") if env else None
    default_project = env.get("preferences", {}).get("defaultProject") if env else None

    for issue in issues:
        score = 0
        reasons = []

        # Branch match (highest priority) - check both env.json and branch name
        if issue["number"] in branch_related_issues:
            score += 100
            reasons.append("branch selected issue")
        elif branch_issue and issue["number"] == branch_issue:
            score += 100
            reasons.append("branch name match")

        # Scope match
        if detected_scope and detected_scope in issue.get("labels", []):
            score += 50
            reasons.append(f"scope match: {detected_scope}")

        # Keyword matching
        issue_text = f"{issue['title']} {issue.get('body_preview', '')}".lower()

        for file in files:
            # Extract keywords from file path
            parts = Path(file).stem.replace("-", " ").replace("_", " ").split()
            for part in parts:
                if len(part) > 2 and part.lower() in issue_text:
                    score += 10
                    if f"file keyword: {part}" not in reasons:
                        reasons.append(f"file keyword: {part}")

        # Label matching
        labels = issue.get("labels", [])
        for file in files:
            if "test" in file and any("test" in l.lower() for l in labels):
                score += 5
            if "auth" in file and any("auth" in l.lower() for l in labels):
                score += 5
            if "api" in file and any("api" in l.lower() for l in labels):
                score += 5

        if score > 0:
            scored.append({
                "issue": issue,
                "score": score,
                "reasons": reasons
            })

    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored

def suggest_refs():
    """Suggest issue references for current staged changes."""
    related = find_related_issues()

    if not related:
        print("No related issues found.")
        return

    branch = get_current_branch()
    branch_issue = extract_issue_from_branch(branch)

    # Get all related issues from env.json
    env = load_environment()
    branch_related_issues = env.get("branch", {}).get("relatedIssues", []) if env else []

    print("Suggested issue references for your commit:\n")

    for i, item in enumerate(related[:5]):  # Top 5
        issue = item["issue"]
        score = item["score"]
        reasons = item["reasons"]

        # Determine reference type
        is_branch_issue = issue["number"] in branch_related_issues or (branch_issue and issue["number"] == branch_issue)
        if is_branch_issue:
            ref_type = "Closes"
            confidence = "HIGH"
        elif score >= 50:
            ref_type = "Closes"
            confidence = "HIGH"
        elif score >= 20:
            ref_type = "Refs"
            confidence = "MEDIUM"
        else:
            ref_type = "Refs"
            confidence = "LOW"

        print(f"{i+1}. [{confidence}] {ref_type} #{issue['number']}")
        print(f"   Title: {issue['title']}")
        print(f"   Match: {', '.join(reasons)}")
        print()

    # Provide formatted footer for all branch issues
    if related:
        # Collect all branch issues first
        branch_refs = []
        other_refs = []

        for item in related[:5]:
            issue = item["issue"]
            is_branch_issue = issue["number"] in branch_related_issues or (branch_issue and issue["number"] == branch_issue)
            if is_branch_issue:
                branch_refs.append(f"Closes #{issue['number']}")
            elif item["score"] >= 20:
                other_refs.append(f"Refs #{issue['number']}")

        print("Suggested commit footer:")
        if branch_refs:
            print("\n".join(branch_refs))
        if other_refs:
            print("\n".join(other_refs[:2]))  # Limit other refs

def get_issue(number):
    """Get a specific issue from cache."""
    cache = load_cache()
    if not cache:
        return None

    for issue in cache.get("issues", []):
        if issue["number"] == number:
            return issue

    return None

def show_filtered_issues(filter_type="all"):
    """Display issues with specific filtering."""
    cache = load_cache()

    if not cache:
        print("No cached issues. Run: python issue-tracker.py sync")
        return

    issues = cache.get("issues", [])
    env = load_environment()

    # Apply filters based on type
    if filter_type == "context":
        issues = apply_context_filters(issues, env)
        filter_desc = "context (project + scope + assignment)"
    elif filter_type == "scope":
        scope_label = env.get("branch", {}).get("scopeLabel") if env else None
        if scope_label:
            issues = filter_by_scope(issues, scope_label)
            filter_desc = f"scope: {scope_label}"
        else:
            filter_desc = "scope (none detected)"
    elif filter_type == "branch":
        branch_issues = get_branch_issues()
        issues = [i for i in issues if i["number"] in branch_issues]
        filter_desc = f"branch issues: {branch_issues}"
    else:
        filter_desc = "all"

    # Display
    last_sync = datetime.fromisoformat(cache["lastSync"].replace("Z", "+00:00"))
    age_minutes = (datetime.now(timezone.utc) - last_sync).total_seconds() / 60

    print(f"📋 Filtered Issues ({filter_desc})")
    print(f"Synced {int(age_minutes)} minutes ago")
    print()

    if not issues:
        print("No issues match this filter.")
        return

    # Sort by priority
    high_priority = []
    normal = []

    for issue in issues:
        labels = issue.get("labels", [])
        is_high = any("high" in l.lower() for l in labels)
        if is_high:
            high_priority.append(issue)
        else:
            normal.append(issue)

    def print_issue(issue):
        labels = ", ".join(issue.get("labels", [])) or "none"
        print(f"┌─ #{issue['number']} {issue['title']}")
        print(f"│  Labels: {labels}")
        print(f"└─ Use: Closes #{issue['number']} or Refs #{issue['number']}")
        print()

    if high_priority:
        print("HIGH PRIORITY:")
        for issue in high_priority:
            print_issue(issue)

    if normal:
        print("NORMAL PRIORITY:")
        for issue in normal:
            print_issue(issue)


def select_branch_issues(issue_numbers):
    """Set the related issues for the current branch."""
    env = load_environment()
    if not env:
        print("Environment not initialized. Run /github-workflows:init first.")
        return False

    # Validate issue numbers exist in cache
    cache = load_cache()
    if cache:
        cached_numbers = {i["number"] for i in cache.get("issues", [])}
        invalid = [n for n in issue_numbers if n not in cached_numbers]
        if invalid:
            print(f"Warning: Issues not in cache: {invalid}")
            print("Run /issue-track sync to update cache.")

    # Update env.json
    if "branch" not in env:
        env["branch"] = {"name": "", "relatedIssues": []}

    env["branch"]["relatedIssues"] = issue_numbers

    env_path = Path(CACHE_DIR) / "env.json"
    with open(env_path, "w") as f:
        json.dump(env, f, indent=2)

    print(f"✓ Selected issues for branch: {issue_numbers}")
    return True


def clear_cache():
    """Clear the issue cache."""
    cache_path = get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
        print(f"Cleared cache: {cache_path}")
    else:
        print("No cache to clear.")

def main():
    if len(sys.argv) < 2:
        show_issues()
        return

    command = sys.argv[1]

    if command == "sync":
        filter_type = sys.argv[2] if len(sys.argv) > 2 else "assigned"
        filter_value = sys.argv[3] if len(sys.argv) > 3 else None
        if sync_issues(filter_type, filter_value):
            show_issues()

    elif command == "show":
        show_issues()

    elif command == "context":
        # Show issues filtered by context (project + scope + assignment)
        show_filtered_issues("context")

    elif command == "scope":
        # Show issues matching branch scope
        show_filtered_issues("scope")

    elif command == "branch":
        # Show only issues selected for current branch
        show_filtered_issues("branch")

    elif command == "select":
        # Select issues for current branch
        if len(sys.argv) < 3:
            print("Usage: issue-tracker.py select <issue_numbers...>")
            print("Example: issue-tracker.py select 42 43 44")
            return
        try:
            issue_numbers = [int(n) for n in sys.argv[2:]]
            select_branch_issues(issue_numbers)
        except ValueError:
            print("Error: Issue numbers must be integers")
            return

    elif command == "find-related":
        files = sys.argv[2:] if len(sys.argv) > 2 else None
        related = find_related_issues(files)
        print(json.dumps(related, indent=2, default=str))

    elif command == "suggest-refs":
        suggest_refs()

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: issue-tracker.py get <number>")
            return
        number = int(sys.argv[2])
        issue = get_issue(number)
        if issue:
            print(json.dumps(issue, indent=2))
        else:
            print(f"Issue #{number} not found in cache.")

    elif command == "clear":
        clear_cache()

    elif command == "json":
        # Output cache as JSON for other tools
        cache = load_cache()
        if cache:
            print(json.dumps(cache, indent=2))
        else:
            print("{}")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
