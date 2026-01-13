#!/usr/bin/env python3
"""
GitHub Milestone Manager Script
Handles milestone CRUD, bulk operations, and progress tracking
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Color constants
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def error(message: str) -> None:
    """Print error message and exit"""
    print(f"{RED}Error: {message}{NC}", file=sys.stderr)
    sys.exit(1)


def success(message: str) -> None:
    """Print success message"""
    print(f"{GREEN}✓ {message}{NC}")


def warn(message: str) -> None:
    """Print warning message"""
    print(f"{YELLOW}⚠ {message}{NC}")


def info(message: str) -> None:
    """Print info message"""
    print(f"{BLUE}ℹ {message}{NC}")


def run_gh_api(endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
    """Execute gh API command"""
    try:
        cmd = ['gh', 'api', endpoint]

        if method != 'GET':
            cmd.extend(['-X', method])

        if data:
            for key, value in data.items():
                cmd.extend(['-f', f'{key}={value}'])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout) if result.stdout else None
    except subprocess.CalledProcessError as e:
        error(f"API request failed: {e.stderr}")
        return None


def get_repo_path() -> str:
    """Get current repository owner/name"""
    try:
        result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'nameWithOwner', '-q', '.nameWithOwner'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        error("Not in a GitHub repository or gh CLI not authenticated")
        return ""


def parse_date(date_str: str) -> str:
    """Parse date string to ISO 8601 format"""
    try:
        # Try parsing various formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%dT00:00:00Z')
            except ValueError:
                continue

        # If numeric, treat as days from now
        days = int(date_str)
        dt = datetime.now() + timedelta(days=days)
        return dt.strftime('%Y-%m-%dT00:00:00Z')

    except (ValueError, TypeError):
        error(f"Invalid date format: {date_str}. Use YYYY-MM-DD, days from now (e.g., 14), or MM/DD/YYYY")
        return ""


def create_milestone(title: str, due_date: Optional[str], description: str = "") -> Dict:
    """Create a new milestone"""
    repo = get_repo_path()

    data = {
        'title': title,
        'description': description
    }

    if due_date:
        iso_date = parse_date(due_date)
        if iso_date:
            data['due_on'] = iso_date

    result = run_gh_api(f'/repos/{repo}/milestones', 'POST', data)

    if result:
        success(f"Created milestone: {title} (#{result['number']})")

        if due_date:
            due_date_formatted = datetime.fromisoformat(result['due_on'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            info(f"Due date: {due_date_formatted}")

        return result

    return {}


def list_milestones(with_progress: bool = False, state: str = 'open') -> None:
    """List all milestones"""
    repo = get_repo_path()
    milestones = run_gh_api(f'/repos/{repo}/milestones?state={state}')

    if not milestones:
        info(f"No {state} milestones found")
        return

    print(f"\n{'='*60}")
    print(f"{'Milestones':<40} ({len(milestones)} {state})")
    print(f"{'='*60}\n")

    for milestone in milestones:
        number = milestone['number']
        title = milestone['title']
        due_on = milestone.get('due_on')
        open_issues = milestone['open_issues']
        closed_issues = milestone['closed_issues']
        total = open_issues + closed_issues

        print(f"#{number}: {title}")

        if due_on:
            due_date = datetime.fromisoformat(due_on.replace('Z', '+00:00'))
            days_remaining = (due_date - datetime.now()).days

            if days_remaining < 0:
                print(f"  Due: {due_date.strftime('%Y-%m-%d')} ({RED}OVERDUE by {abs(days_remaining)} days{NC})")
            elif days_remaining == 0:
                print(f"  Due: {due_date.strftime('%Y-%m-%d')} ({YELLOW}DUE TODAY{NC})")
            else:
                print(f"  Due: {due_date.strftime('%Y-%m-%d')} ({days_remaining} days remaining)")

        if with_progress and total > 0:
            percentage = (closed_issues / total) * 100
            bar_length = 30
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)

            print(f"  Progress: [{bar}] {percentage:.0f}%")
            print(f"  Issues: {closed_issues}/{total} closed ({open_issues} open)")

        if milestone.get('description'):
            print(f"  Description: {milestone['description'][:100]}...")

        print()


def update_milestone(number: int, title: Optional[str] = None, due_date: Optional[str] = None,
                     description: Optional[str] = None, state: Optional[str] = None) -> None:
    """Update an existing milestone"""
    repo = get_repo_path()

    data = {}
    if title:
        data['title'] = title
    if due_date:
        data['due_on'] = parse_date(due_date)
    if description:
        data['description'] = description
    if state:
        data['state'] = state

    if not data:
        error("No updates specified")
        return

    result = run_gh_api(f'/repos/{repo}/milestones/{number}', 'PATCH', data)

    if result:
        success(f"Updated milestone #{number}")


def close_milestone(number: int) -> None:
    """Close a milestone"""
    update_milestone(number, state='closed')


def bulk_assign(milestone_title: str, filter_query: str, dry_run: bool = False) -> None:
    """Bulk assign issues to a milestone"""
    repo = get_repo_path()

    # Find milestone number by title
    milestones = run_gh_api(f'/repos/{repo}/milestones?state=open')
    milestone = next((m for m in milestones if m['title'] == milestone_title), None)

    if not milestone:
        error(f"Milestone '{milestone_title}' not found")
        return

    milestone_number = milestone['number']

    # Search for issues
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--search', filter_query, '--json', 'number,title', '--limit', '1000'],
            capture_output=True,
            text=True,
            check=True
        )
        issues = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        error(f"Issue search failed: {e.stderr}")
        return

    if not issues:
        warn("No issues found matching filter")
        return

    if dry_run:
        info(f"DRY RUN: Would assign {len(issues)} issues to milestone '{milestone_title}'")
        for issue in issues[:10]:
            print(f"  - #{issue['number']}: {issue['title']}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
        return

    info(f"Assigning {len(issues)} issues to milestone '{milestone_title}'...")

    for i, issue in enumerate(issues, 1):
        try:
            subprocess.run(
                ['gh', 'issue', 'edit', str(issue['number']), '--milestone', milestone_title],
                capture_output=True,
                check=True
            )
            print(f"\r{i}/{len(issues)}", end='', flush=True)
        except subprocess.CalledProcessError:
            warn(f"Failed to assign issue #{issue['number']}")

    print()  # New line
    success(f"Assigned {len(issues)} issues to milestone '{milestone_title}'")


def show_progress(number: int) -> None:
    """Show detailed progress for a milestone"""
    repo = get_repo_path()

    milestone = run_gh_api(f'/repos/{repo}/milestones/{number}')
    if not milestone:
        error(f"Milestone #{number} not found")
        return

    title = milestone['title']
    open_issues = milestone['open_issues']
    closed_issues = milestone['closed_issues']
    total = open_issues + closed_issues

    print(f"\n{'='*60}")
    print(f"Milestone Progress: {title}")
    print(f"{'='*60}\n")

    # Due date analysis
    if milestone.get('due_on'):
        due_date = datetime.fromisoformat(milestone['due_on'].replace('Z', '+00:00'))
        created_date = datetime.fromisoformat(milestone['created_at'].replace('Z', '+00:00'))
        now = datetime.now()

        total_duration = (due_date - created_date).days
        elapsed = (now - created_date).days
        remaining = (due_date - now).days

        print(f"Duration: {elapsed}/{total_duration} days ({remaining} days remaining)")

        if total_duration > 0:
            time_percentage = (elapsed / total_duration) * 100
            print(f"Time: {time_percentage:.0f}% elapsed")

    # Progress
    if total > 0:
        completion = (closed_issues / total) * 100

        bar_length = 40
        filled = int(bar_length * completion / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\nProgress: [{bar}] {completion:.0f}%")
        print(f"Issues: {closed_issues}/{total} complete")
        print(f"  ✅ Closed: {closed_issues}")
        print(f"  🔄 Open: {open_issues}")

        # Status indicator
        if milestone.get('due_on'):
            time_percentage = (elapsed / total_duration) * 100 if total_duration > 0 else 0

            if completion >= time_percentage + 10:
                print(f"\n{GREEN}🟢 Status: Ahead of schedule{NC}")
            elif completion >= time_percentage - 10:
                print(f"\n{BLUE}🟡 Status: On track{NC}")
            else:
                print(f"\n{RED}🔴 Status: Behind schedule{NC}")

            # Velocity analysis
            if elapsed > 0:
                velocity = closed_issues / elapsed
                needed_velocity = open_issues / max(remaining, 1)

                print(f"\nVelocity:")
                print(f"  Current: {velocity:.2f} issues/day")
                print(f"  Needed: {needed_velocity:.2f} issues/day")

                if needed_velocity > velocity * 1.5:
                    warn(f"Need to increase pace by {((needed_velocity / velocity) - 1) * 100:.0f}%")
    else:
        info("No issues assigned to this milestone")

    # Get issues by label
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--milestone', title, '--json', 'number,title,labels,state', '--limit', '1000'],
            capture_output=True,
            text=True,
            check=True
        )
        issues = json.loads(result.stdout)

        # Group by label
        label_stats = {}
        for issue in issues:
            for label in issue.get('labels', []):
                label_name = label['name']
                if label_name not in label_stats:
                    label_stats[label_name] = {'open': 0, 'closed': 0}

                if issue['state'] == 'OPEN':
                    label_stats[label_name]['open'] += 1
                else:
                    label_stats[label_name]['closed'] += 1

        if label_stats:
            print(f"\nProgress by Label:")
            for label_name, stats in sorted(label_stats.items(), key=lambda x: x[0]):
                label_total = stats['open'] + stats['closed']
                label_completion = (stats['closed'] / label_total) * 100 if label_total > 0 else 0
                print(f"  {label_name}: {stats['closed']}/{label_total} ({label_completion:.0f}%)")

    except subprocess.CalledProcessError:
        pass

    print()


def main():
    parser = argparse.ArgumentParser(description='GitHub Milestone Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # create
    create_parser = subparsers.add_parser('create', help='Create a new milestone')
    create_parser.add_argument('--title', required=True, help='Milestone title')
    create_parser.add_argument('--due', help='Due date (YYYY-MM-DD or days from now)')
    create_parser.add_argument('--description', default='', help='Milestone description')

    # list
    list_parser = subparsers.add_parser('list', help='List milestones')
    list_parser.add_argument('--with-progress', action='store_true', help='Show progress bars')
    list_parser.add_argument('--state', default='open', choices=['open', 'closed', 'all'], help='Milestone state')

    # update
    update_parser = subparsers.add_parser('update', help='Update a milestone')
    update_parser.add_argument('number', type=int, help='Milestone number')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--due', help='New due date')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--state', choices=['open', 'closed'], help='New state')

    # close
    close_parser = subparsers.add_parser('close', help='Close a milestone')
    close_parser.add_argument('number', type=int, help='Milestone number')

    # bulk-assign
    assign_parser = subparsers.add_parser('bulk-assign', help='Bulk assign issues to milestone')
    assign_parser.add_argument('--milestone', required=True, help='Milestone title')
    assign_parser.add_argument('--filter', required=True, help='Issue search filter')
    assign_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    # progress
    progress_parser = subparsers.add_parser('progress', help='Show detailed milestone progress')
    progress_parser.add_argument('number', type=int, help='Milestone number')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'create':
        create_milestone(args.title, args.due, args.description)
    elif args.command == 'list':
        list_milestones(args.with_progress, args.state)
    elif args.command == 'update':
        update_milestone(args.number, args.title, args.due, args.description, args.state)
    elif args.command == 'close':
        close_milestone(args.number)
    elif args.command == 'bulk-assign':
        bulk_assign(args.milestone, args.filter, args.dry_run)
    elif args.command == 'progress':
        show_progress(args.number)


if __name__ == '__main__':
    main()
