#!/usr/bin/env python3
"""
Issue creation helper utilities.

Usage:
    python issue-helpers.py list-labels
    python issue-helpers.py list-milestones
    python issue-helpers.py list-projects
    python issue-helpers.py create --title "Title" --type bug --priority high
"""

import subprocess
import json
import sys
import argparse
from typing import Optional


def run_gh_command(args: list) -> tuple[bool, str]:
    """Run a gh CLI command and return success status and output."""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "gh CLI not found. Install from https://cli.github.com/"


def list_labels():
    """List all available labels."""
    success, output = run_gh_command([
        'label', 'list',
        '--json', 'name,description,color',
        '--limit', '100'
    ])

    if not success:
        print(f"Error: {output}", file=sys.stderr)
        return False

    labels = json.loads(output)

    # Group labels by category
    categories = {
        'Type': [],
        'Priority': [],
        'Scope': [],
        'Branch': [],
        'Other': []
    }

    for label in labels:
        name = label['name']
        if name in ['bug', 'feature', 'enhancement', 'documentation', 'refactor', 'chore', 'test']:
            categories['Type'].append(label)
        elif name.startswith('priority:'):
            categories['Priority'].append(label)
        elif name.startswith('scope:'):
            categories['Scope'].append(label)
        elif name.startswith('branch:'):
            categories['Branch'].append(label)
        else:
            categories['Other'].append(label)

    # Print grouped labels
    for category, labels in categories.items():
        if labels:
            print(f"\n## {category} Labels\n")
            for label in sorted(labels, key=lambda x: x['name']):
                desc = label.get('description', '')
                if desc:
                    print(f"- `{label['name']}` - {desc}")
                else:
                    print(f"- `{label['name']}`")

    return True


def list_milestones():
    """List open milestones with progress."""
    success, output = run_gh_command([
        'api', 'repos/:owner/:repo/milestones',
        '--jq', '.[] | {title, open_issues, closed_issues, due_on, state, description}'
    ])

    if not success:
        print(f"Error: {output}", file=sys.stderr)
        return False

    if not output:
        print("No milestones found.")
        return True

    print("\n## Open Milestones\n")

    # Parse JSONL output
    for line in output.split('\n'):
        if line.strip():
            milestone = json.loads(line)
            if milestone['state'] == 'open':
                total = milestone['open_issues'] + milestone['closed_issues']
                closed = milestone['closed_issues']
                pct = (closed / total * 100) if total > 0 else 0

                print(f"### {milestone['title']}")
                print(f"- Progress: {closed}/{total} issues ({pct:.0f}%)")
                if milestone['due_on']:
                    print(f"- Due: {milestone['due_on'][:10]}")
                if milestone['description']:
                    print(f"- {milestone['description'][:100]}")
                print()

    return True


def list_projects():
    """List available projects."""
    # Try user projects first
    success, output = run_gh_command([
        'api', 'graphql',
        '-f', 'query={ viewer { projectsV2(first: 10) { nodes { id title number } } } }'
    ])

    if not success:
        print(f"Error: {output}", file=sys.stderr)
        return False

    data = json.loads(output)
    projects = data.get('data', {}).get('viewer', {}).get('projectsV2', {}).get('nodes', [])

    if not projects:
        print("No projects found.")
        return True

    print("\n## Available Projects\n")
    for project in projects:
        print(f"- {project['title']} (#{project['number']})")

    return True


def create_issue(
    title: str,
    issue_type: str,
    priority: str,
    body: Optional[str] = None,
    body_file: Optional[str] = None,
    scope: Optional[str] = None,
    branch: Optional[str] = None,
    milestone: Optional[str] = None,
    project: Optional[str] = None,
    assignee: Optional[str] = None
):
    """Create an issue with full metadata."""

    # Build labels list
    labels = [issue_type, f"priority:{priority}"]
    # Scope is required - enforce scope: prefix
    labels.append(scope if scope.startswith('scope:') else f"scope:{scope}")
    if branch:
        labels.append(branch if branch.startswith('branch:') else f"branch:{branch}")

    # Build command
    cmd = [
        'issue', 'create',
        '--title', title,
        '--label', ','.join(labels)
    ]

    # Add body
    if body_file:
        cmd.extend(['--body-file', body_file])
    elif body:
        cmd.extend(['--body', body])
    else:
        # Default body template
        default_body = f"""## Summary

[Description of what needs to be done]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context

[Any relevant context]
"""
        cmd.extend(['--body', default_body])

    # Add milestone
    if milestone:
        cmd.extend(['--milestone', milestone])

    # Add project
    if project:
        cmd.extend(['--project', project])

    # Add assignee
    if assignee:
        cmd.extend(['--assignee', assignee])

    # Create the issue
    success, output = run_gh_command(cmd)

    if success:
        print(f"✅ Issue created successfully!")
        print(f"URL: {output}")
        print(f"\nLabels: {', '.join(labels)}")
        if milestone:
            print(f"Milestone: {milestone}")
        if project:
            print(f"Project: {project}")
        return True
    else:
        print(f"❌ Failed to create issue: {output}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Issue creation helper utilities'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # list-labels command
    subparsers.add_parser('list-labels', help='List available labels')

    # list-milestones command
    subparsers.add_parser('list-milestones', help='List open milestones')

    # list-projects command
    subparsers.add_parser('list-projects', help='List available projects')

    # create command
    create_parser = subparsers.add_parser('create', help='Create an issue')
    create_parser.add_argument('--title', required=True, help='Issue title')
    create_parser.add_argument('--type', required=True,
                               choices=['bug', 'feature', 'enhancement', 'documentation', 'refactor', 'chore'],
                               help='Issue type')
    create_parser.add_argument('--priority', required=True,
                               choices=['high', 'medium', 'low'],
                               help='Issue priority')
    create_parser.add_argument('--body', help='Issue body')
    create_parser.add_argument('--body-file', help='File containing issue body')
    create_parser.add_argument('--scope', required=True, help='Scope label (REQUIRED, e.g., scope:github-workflows)')
    create_parser.add_argument('--branch', help='Branch label (e.g., branch:feature/auth)')
    create_parser.add_argument('--milestone', help='Milestone title')
    create_parser.add_argument('--project', help='Project name')
    create_parser.add_argument('--assignee', help='Assignee username')

    args = parser.parse_args()

    if args.command == 'list-labels':
        sys.exit(0 if list_labels() else 1)
    elif args.command == 'list-milestones':
        sys.exit(0 if list_milestones() else 1)
    elif args.command == 'list-projects':
        sys.exit(0 if list_projects() else 1)
    elif args.command == 'create':
        success = create_issue(
            title=args.title,
            issue_type=args.type,
            priority=args.priority,
            body=args.body,
            body_file=args.body_file,
            scope=args.scope,
            branch=args.branch,
            milestone=args.milestone,
            project=args.project,
            assignee=args.assignee
        )
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
