#!/usr/bin/env python3
"""
GitHub Issue Relationship Manager

Manages parent-child (sub-issue) relationships and queries issue hierarchies
using the GitHub GraphQL API.

Usage:
    python manage-relationships.py <command> [options]

Commands:
    add-sub-issue       Add a child issue to a parent
    remove-sub-issue    Remove a child from a parent
    list-sub-issues     List all sub-issues of an issue
    get-parent          Get the parent of an issue
    get-ids             Get node IDs for issue numbers
    show-all            Show all relationships for an issue
    show-dependencies   Show blocking/blocked-by dependencies
"""

import argparse
import json
import subprocess
import sys
from typing import Optional


def run_graphql(query: str) -> dict:
    """Execute a GraphQL query via gh api."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Try to extract error message from response
        try:
            error_data = json.loads(result.stdout)
            if "errors" in error_data:
                for error in error_data["errors"]:
                    print(f"Error: {error.get('message', 'Unknown error')}", file=sys.stderr)
            # Return data even if there are errors (partial success)
            if "data" in error_data:
                return error_data
        except json.JSONDecodeError:
            pass
        print(f"GraphQL error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return json.loads(result.stdout)


def get_repo_info() -> tuple[str, str]:
    """Get current repository owner and name."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Error: Could not determine repository. Run from a git repository.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def get_issue_ids(owner: str, repo: str, issue_numbers: list[int]) -> dict[int, str]:
    """Get node IDs for a list of issue numbers."""
    if not issue_numbers:
        return {}

    # Build query with aliases for each issue
    issue_queries = []
    for num in issue_numbers:
        issue_queries.append(f'issue{num}: issue(number: {num}) {{ id number }}')

    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        {" ".join(issue_queries)}
      }}
    }}
    '''

    result = run_graphql(query)

    ids = {}
    repo_data = result.get("data", {}).get("repository", {})
    for num in issue_numbers:
        issue_data = repo_data.get(f"issue{num}")
        if issue_data:
            ids[num] = issue_data["id"]
        else:
            print(f"Warning: Issue #{num} not found", file=sys.stderr)

    return ids


def add_sub_issue(owner: str, repo: str, parent_num: int, child_num: int, replace_parent: bool = False):
    """Add a child issue as a sub-issue of a parent."""
    # Get node IDs
    ids = get_issue_ids(owner, repo, [parent_num, child_num])

    if parent_num not in ids:
        print(f"Error: Parent issue #{parent_num} not found", file=sys.stderr)
        sys.exit(1)
    if child_num not in ids:
        print(f"Error: Child issue #{child_num} not found", file=sys.stderr)
        sys.exit(1)

    replace_str = "true" if replace_parent else "false"

    query = f'''
    mutation {{
      addSubIssue(input: {{
        issueId: "{ids[parent_num]}",
        subIssueId: "{ids[child_num]}",
        replaceParent: {replace_str}
      }}) {{
        issue {{ number title }}
        subIssue {{ number title }}
      }}
    }}
    '''

    result = run_graphql(query)

    if result.get("data", {}).get("addSubIssue"):
        data = result["data"]["addSubIssue"]
        print(f"Added #{data['subIssue']['number']} as sub-issue of #{data['issue']['number']}")
        print(f"  Parent: {data['issue']['title']}")
        print(f"  Child:  {data['subIssue']['title']}")
    else:
        print("Failed to add sub-issue", file=sys.stderr)
        sys.exit(1)


def remove_sub_issue(owner: str, repo: str, parent_num: int, child_num: int):
    """Remove a child issue from a parent."""
    ids = get_issue_ids(owner, repo, [parent_num, child_num])

    if parent_num not in ids or child_num not in ids:
        print("Error: Issue not found", file=sys.stderr)
        sys.exit(1)

    query = f'''
    mutation {{
      removeSubIssue(input: {{
        issueId: "{ids[parent_num]}",
        subIssueId: "{ids[child_num]}"
      }}) {{
        issue {{ number }}
        subIssue {{ number }}
      }}
    }}
    '''

    result = run_graphql(query)

    if result.get("data", {}).get("removeSubIssue"):
        print(f"Removed #{child_num} from parent #{parent_num}")
    else:
        print("Failed to remove sub-issue", file=sys.stderr)
        sys.exit(1)


def list_sub_issues(owner: str, repo: str, issue_num: int):
    """List all sub-issues of an issue."""
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {issue_num}) {{
          number
          title
          subIssuesSummary {{
            total
            completed
            percentCompleted
          }}
          subIssues(first: 100) {{
            nodes {{
              number
              title
              state
            }}
          }}
        }}
      }}
    }}
    '''

    result = run_graphql(query)
    issue = result.get("data", {}).get("repository", {}).get("issue")

    if not issue:
        print(f"Error: Issue #{issue_num} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Issue #{issue['number']}: {issue['title']}")

    summary = issue.get("subIssuesSummary", {})
    if summary.get("total", 0) > 0:
        print(f"\nProgress: {summary['completed']}/{summary['total']} ({summary['percentCompleted']}%)")

    sub_issues = issue.get("subIssues", {}).get("nodes", [])

    if not sub_issues:
        print("\nNo sub-issues")
        return

    print(f"\nSub-issues ({len(sub_issues)}):")
    for sub in sub_issues:
        state_icon = "" if sub["state"] == "CLOSED" else ""
        print(f"  {state_icon} #{sub['number']}: {sub['title']}")


def get_parent(owner: str, repo: str, issue_num: int):
    """Get the parent of an issue."""
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {issue_num}) {{
          number
          title
          parent {{
            number
            title
            state
          }}
        }}
      }}
    }}
    '''

    result = run_graphql(query)
    issue = result.get("data", {}).get("repository", {}).get("issue")

    if not issue:
        print(f"Error: Issue #{issue_num} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Issue #{issue['number']}: {issue['title']}")

    parent = issue.get("parent")
    if parent:
        state_icon = "" if parent["state"] == "CLOSED" else ""
        print(f"\nParent: {state_icon} #{parent['number']}: {parent['title']}")
    else:
        print("\nNo parent (top-level issue)")


def show_all_relationships(owner: str, repo: str, issue_num: int):
    """Show all relationships for an issue."""
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {issue_num}) {{
          number
          title
          state

          parent {{
            number
            title
          }}

          subIssues(first: 50) {{
            nodes {{
              number
              title
              state
            }}
          }}
          subIssuesSummary {{
            total
            completed
            percentCompleted
          }}

          blockedBy(first: 20) {{
            nodes {{
              number
              title
              state
            }}
          }}

          blocking(first: 20) {{
            nodes {{
              number
              title
              state
            }}
          }}

          trackedInIssues(first: 20) {{
            nodes {{
              number
              title
            }}
          }}

          trackedIssuesCount
        }}
      }}
    }}
    '''

    result = run_graphql(query)
    issue = result.get("data", {}).get("repository", {}).get("issue")

    if not issue:
        print(f"Error: Issue #{issue_num} not found", file=sys.stderr)
        sys.exit(1)

    state_icon = "" if issue["state"] == "CLOSED" else ""
    print(f"{state_icon} Issue #{issue['number']}: {issue['title']}")
    print("=" * 60)

    # Parent
    parent = issue.get("parent")
    if parent:
        print(f"\n Parent: #{parent['number']} - {parent['title']}")

    # Sub-issues
    sub_issues = issue.get("subIssues", {}).get("nodes", [])
    if sub_issues:
        summary = issue.get("subIssuesSummary", {})
        print(f"\n Sub-issues ({summary.get('completed', 0)}/{summary.get('total', 0)}):")
        for sub in sub_issues:
            icon = "" if sub["state"] == "CLOSED" else ""
            print(f"    {icon} #{sub['number']}: {sub['title']}")

    # Blocked by
    blocked_by = issue.get("blockedBy", {}).get("nodes", [])
    if blocked_by:
        print(f"\n Blocked by:")
        for blocker in blocked_by:
            icon = "" if blocker["state"] == "CLOSED" else ""
            print(f"    {icon} #{blocker['number']}: {blocker['title']}")

    # Blocking
    blocking = issue.get("blocking", {}).get("nodes", [])
    if blocking:
        print(f"\n Blocking:")
        for blocked in blocking:
            icon = "" if blocked["state"] == "CLOSED" else ""
            print(f"    {icon} #{blocked['number']}: {blocked['title']}")

    # Tracked in
    tracked_in = issue.get("trackedInIssues", {}).get("nodes", [])
    if tracked_in:
        print(f"\n Tracked in:")
        for tracker in tracked_in:
            print(f"    #{tracker['number']}: {tracker['title']}")

    # Tracks count
    tracks_count = issue.get("trackedIssuesCount", 0)
    if tracks_count:
        print(f"\n Tracks: {tracks_count} issues")

    # Summary if no relationships
    if not any([parent, sub_issues, blocked_by, blocking, tracked_in, tracks_count]):
        print("\nNo relationships found")


def show_dependencies(owner: str, repo: str, issue_num: int):
    """Show blocking dependencies for an issue."""
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo}") {{
        issue(number: {issue_num}) {{
          number
          title
          state

          blockedBy(first: 50) {{
            nodes {{
              number
              title
              state
            }}
          }}

          blocking(first: 50) {{
            nodes {{
              number
              title
              state
            }}
          }}
        }}
      }}
    }}
    '''

    result = run_graphql(query)
    issue = result.get("data", {}).get("repository", {}).get("issue")

    if not issue:
        print(f"Error: Issue #{issue_num} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Dependencies for #{issue['number']}: {issue['title']}")
    print("=" * 60)

    blocked_by = issue.get("blockedBy", {}).get("nodes", [])
    if blocked_by:
        print(f"\n Blocked by ({len(blocked_by)}):")
        for blocker in blocked_by:
            icon = "" if blocker["state"] == "CLOSED" else ""
            print(f"    {icon} #{blocker['number']}: {blocker['title']}")
    else:
        print("\n Not blocked by any issues")

    blocking = issue.get("blocking", {}).get("nodes", [])
    if blocking:
        print(f"\n Blocking ({len(blocking)}):")
        for blocked in blocking:
            icon = "" if blocked["state"] == "CLOSED" else ""
            print(f"    {icon} #{blocked['number']}: {blocked['title']}")
    else:
        print("\n Not blocking any issues")


def print_issue_ids(owner: str, repo: str, issue_numbers: list[int]):
    """Print node IDs for issues."""
    ids = get_issue_ids(owner, repo, issue_numbers)

    print("Issue Node IDs:")
    for num in issue_numbers:
        if num in ids:
            print(f"  #{num}: {ids[num]}")
        else:
            print(f"  #{num}: NOT FOUND")


def main():
    parser = argparse.ArgumentParser(
        description="Manage GitHub issue relationships via GraphQL API"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # add-sub-issue
    add_parser = subparsers.add_parser("add-sub-issue", help="Add a sub-issue to a parent")
    add_parser.add_argument("--parent", type=int, required=True, help="Parent issue number")
    add_parser.add_argument("--child", type=int, required=True, help="Child issue number")
    add_parser.add_argument("--replace-parent", action="store_true",
                          help="Replace existing parent if child has one")

    # remove-sub-issue
    remove_parser = subparsers.add_parser("remove-sub-issue", help="Remove a sub-issue from parent")
    remove_parser.add_argument("--parent", type=int, required=True, help="Parent issue number")
    remove_parser.add_argument("--child", type=int, required=True, help="Child issue number")

    # list-sub-issues
    list_parser = subparsers.add_parser("list-sub-issues", help="List sub-issues of an issue")
    list_parser.add_argument("--issue", type=int, required=True, help="Issue number")

    # get-parent
    parent_parser = subparsers.add_parser("get-parent", help="Get parent of an issue")
    parent_parser.add_argument("--issue", type=int, required=True, help="Issue number")

    # get-ids
    ids_parser = subparsers.add_parser("get-ids", help="Get node IDs for issue numbers")
    ids_parser.add_argument("--issues", required=True,
                          help="Comma-separated issue numbers (e.g., 67,68,69)")

    # show-all
    all_parser = subparsers.add_parser("show-all", help="Show all relationships for an issue")
    all_parser.add_argument("--issue", type=int, required=True, help="Issue number")

    # show-dependencies
    deps_parser = subparsers.add_parser("show-dependencies", help="Show blocking dependencies")
    deps_parser.add_argument("--issue", type=int, required=True, help="Issue number")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get repository info
    owner, repo = get_repo_info()

    # Execute command
    if args.command == "add-sub-issue":
        add_sub_issue(owner, repo, args.parent, args.child, args.replace_parent)
    elif args.command == "remove-sub-issue":
        remove_sub_issue(owner, repo, args.parent, args.child)
    elif args.command == "list-sub-issues":
        list_sub_issues(owner, repo, args.issue)
    elif args.command == "get-parent":
        get_parent(owner, repo, args.issue)
    elif args.command == "get-ids":
        issue_nums = [int(n.strip()) for n in args.issues.split(",")]
        print_issue_ids(owner, repo, issue_nums)
    elif args.command == "show-all":
        show_all_relationships(owner, repo, args.issue)
    elif args.command == "show-dependencies":
        show_dependencies(owner, repo, args.issue)


if __name__ == "__main__":
    main()
