#!/usr/bin/env python3
"""
Validate Board Configuration
Validates GitHub Projects v2 board configuration including fields, items, and views.
"""

import argparse
import json
import subprocess
import sys
from typing import Any

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def run_gh(args: list[str]) -> str:
    """Execute gh command and return output."""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error running gh command: {e.stderr}{NC}", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(f"{RED}Error: GitHub CLI (gh) not found. Install from: https://github.com/cli/cli{NC}", file=sys.stderr)
        sys.exit(1)


def get_project_data(owner: str, project_number: int) -> dict[str, Any]:
    """Fetch project data via GraphQL."""
    query = '''
    query($owner: String!, $number: Int!) {
      organization(login: $owner) {
        projectV2(number: $number) {
          id
          title
          fields(first: 50) {
            nodes {
              ... on ProjectV2Field {
                id
                name
                dataType
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                dataType
                options {
                  id
                  name
                }
              }
              ... on ProjectV2IterationField {
                id
                name
                dataType
              }
            }
          }
          items(first: 100) {
            nodes {
              id
              type
              content {
                ... on Issue {
                  number
                  title
                  state
                }
                ... on PullRequest {
                  number
                  title
                  state
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2Field { name } }
                  }
                  ... on ProjectV2ItemFieldNumberValue {
                    number
                    field { ... on ProjectV2Field { name } }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field { ... on ProjectV2Field { name } }
                  }
                }
              }
            }
          }
          views(first: 20) {
            nodes {
              id
              name
              layout
            }
          }
        }
      }
      user(login: $owner) {
        projectV2(number: $number) {
          id
          title
          fields(first: 50) {
            nodes {
              ... on ProjectV2Field {
                id
                name
                dataType
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                dataType
                options {
                  id
                  name
                }
              }
              ... on ProjectV2IterationField {
                id
                name
                dataType
              }
            }
          }
          items(first: 100) {
            nodes {
              id
              type
              content {
                ... on Issue {
                  number
                  title
                  state
                }
                ... on PullRequest {
                  number
                  title
                  state
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2Field { name } }
                  }
                  ... on ProjectV2ItemFieldNumberValue {
                    number
                    field { ... on ProjectV2Field { name } }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field { ... on ProjectV2Field { name } }
                  }
                }
              }
            }
          }
          views(first: 20) {
            nodes {
              id
              name
              layout
            }
          }
        }
      }
    }
    '''

    result = run_gh([
        'api', 'graphql',
        '-f', f'query={query}',
        '-f', f'owner={owner}',
        '-F', f'number={project_number}'
    ])

    if not result:
        return {}

    try:
        data = json.loads(result)
        # Try organization first, then user
        project = (data.get('data', {}).get('organization', {}).get('projectV2') or
                   data.get('data', {}).get('user', {}).get('projectV2'))
        return project or {}
    except json.JSONDecodeError as e:
        print(f"{RED}Error parsing GraphQL response: {e}{NC}", file=sys.stderr)
        return {}


def validate_fields(project: dict[str, Any]) -> list[dict[str, str]]:
    """Validate project field configuration."""
    issues = []
    fields = project.get('fields', {}).get('nodes', [])

    if not fields:
        issues.append({
            'severity': 'error',
            'message': 'No fields found in project',
            'suggestion': 'Add fields like Status, Priority, etc.'
        })
        return issues

    field_names = [f.get('name', '') for f in fields]

    # Check for required fields
    recommended_fields = ['Status', 'Priority']
    for field in recommended_fields:
        if field not in field_names:
            issues.append({
                'severity': 'warning',
                'message': f'Recommended field "{field}" not found',
                'suggestion': f'Consider adding a {field} field for better organization'
            })

    # Check single select fields have options
    for field in fields:
        if field.get('dataType') == 'SINGLE_SELECT':
            options = field.get('options', [])
            if not options:
                issues.append({
                    'severity': 'error',
                    'message': f'SingleSelect field "{field.get("name")}" has no options',
                    'suggestion': 'Add options to the field'
                })
            elif len(options) < 2:
                issues.append({
                    'severity': 'warning',
                    'message': f'SingleSelect field "{field.get("name")}" has only {len(options)} option(s)',
                    'suggestion': 'Consider adding more options for flexibility'
                })

    # Check for duplicate field names (shouldn't happen but good to check)
    seen = set()
    for name in field_names:
        if name in seen:
            issues.append({
                'severity': 'error',
                'message': f'Duplicate field name: "{name}"',
                'suggestion': 'Remove or rename duplicate field'
            })
        seen.add(name)

    return issues


def validate_items(project: dict[str, Any], check_orphans: bool = False) -> list[dict[str, str]]:
    """Validate project items."""
    issues = []
    items = project.get('items', {}).get('nodes', [])
    fields = project.get('fields', {}).get('nodes', [])

    if not items:
        issues.append({
            'severity': 'info',
            'message': 'No items in project',
            'suggestion': 'Add issues or PRs to the project board'
        })
        return issues

    # Get Status field options if exists
    status_field = next((f for f in fields if f.get('name') == 'Status'), None)
    status_options = [opt.get('name') for opt in status_field.get('options', [])] if status_field else []

    # Check each item
    orphan_count = 0
    items_without_status = []

    for item in items:
        item_id = item.get('id', 'unknown')
        content = item.get('content', {})
        item_title = content.get('title', 'Unknown')
        item_number = content.get('number', '?')

        if not content:
            orphan_count += 1
            if check_orphans:
                issues.append({
                    'severity': 'warning',
                    'message': f'Item {item_id} has no linked content (orphaned)',
                    'suggestion': 'Remove orphaned items or link to an issue/PR'
                })
            continue

        # Check if item has Status field value
        field_values = item.get('fieldValues', {}).get('nodes', [])
        has_status = any(
            fv.get('field', {}).get('name') == 'Status'
            for fv in field_values
            if fv.get('field')
        )

        if not has_status and status_field:
            items_without_status.append(f"#{item_number}: {item_title}")

    if orphan_count > 0 and not check_orphans:
        issues.append({
            'severity': 'warning',
            'message': f'{orphan_count} orphaned item(s) found (no linked content)',
            'suggestion': 'Run with --check-orphans for details'
        })

    if items_without_status:
        if len(items_without_status) <= 5:
            for item in items_without_status:
                issues.append({
                    'severity': 'warning',
                    'message': f'Item without Status: {item}',
                    'suggestion': 'Set Status field for better tracking'
                })
        else:
            issues.append({
                'severity': 'warning',
                'message': f'{len(items_without_status)} items without Status field',
                'suggestion': 'Set Status field for better tracking'
            })

    return issues


def validate_views(project: dict[str, Any]) -> list[dict[str, str]]:
    """Validate project views configuration."""
    issues = []
    views = project.get('views', {}).get('nodes', [])

    if not views:
        issues.append({
            'severity': 'warning',
            'message': 'No views configured',
            'suggestion': 'Add views like Board, Table, or Roadmap'
        })
        return issues

    view_layouts = [v.get('layout') for v in views]

    # Check for recommended views
    if 'BOARD_LAYOUT' not in view_layouts:
        issues.append({
            'severity': 'info',
            'message': 'No Board view configured',
            'suggestion': 'Consider adding a Board view for Kanban-style workflow'
        })

    if 'TABLE_LAYOUT' not in view_layouts:
        issues.append({
            'severity': 'info',
            'message': 'No Table view configured',
            'suggestion': 'Consider adding a Table view for detailed item list'
        })

    # Check for duplicate view names
    view_names = [v.get('name', '') for v in views]
    seen = set()
    for name in view_names:
        if name in seen:
            issues.append({
                'severity': 'warning',
                'message': f'Duplicate view name: "{name}"',
                'suggestion': 'Rename one of the views for clarity'
            })
        seen.add(name)

    return issues


def print_validation_results(project_title: str, all_issues: list[dict[str, str]]) -> int:
    """Print validation results and return exit code."""
    errors = [i for i in all_issues if i['severity'] == 'error']
    warnings = [i for i in all_issues if i['severity'] == 'warning']
    infos = [i for i in all_issues if i['severity'] == 'info']

    print(f"\n{BLUE}Validation Results for: {project_title}{NC}")
    print("=" * 50)

    if not all_issues:
        print(f"\n{GREEN}All checks passed!{NC}")
        return 0

    # Print errors
    if errors:
        print(f"\n{RED}Errors ({len(errors)}):{NC}")
        for issue in errors:
            print(f"  {RED}[ERROR]{NC} {issue['message']}")
            print(f"         {issue['suggestion']}")

    # Print warnings
    if warnings:
        print(f"\n{YELLOW}Warnings ({len(warnings)}):{NC}")
        for issue in warnings:
            print(f"  {YELLOW}[WARN]{NC} {issue['message']}")
            print(f"        {issue['suggestion']}")

    # Print info
    if infos:
        print(f"\n{BLUE}Info ({len(infos)}):{NC}")
        for issue in infos:
            print(f"  {BLUE}[INFO]{NC} {issue['message']}")
            print(f"        {issue['suggestion']}")

    # Summary
    print(f"\n{BLUE}Summary:{NC}")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info:     {len(infos)}")

    # Return exit code
    if errors:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate GitHub Projects v2 board configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s myorg 1
      Basic validation of project #1 for organization 'myorg'

  %(prog)s myorg 1 --check-orphans
      Include detailed orphan item checking

  %(prog)s myorg 1 --check-fields --check-orphans
      Full validation with all checks
        '''
    )

    parser.add_argument('owner', help='GitHub organization or username')
    parser.add_argument('project_number', type=int, help='Project number')
    parser.add_argument('--check-orphans', action='store_true',
                        help='List individual orphaned items')
    parser.add_argument('--check-fields', action='store_true',
                        help='Perform detailed field validation')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')

    args = parser.parse_args()

    # Fetch project data
    print(f"Fetching project #{args.project_number} for {args.owner}...")
    project = get_project_data(args.owner, args.project_number)

    if not project:
        print(f"{RED}Error: Could not fetch project data{NC}", file=sys.stderr)
        print("Check that:", file=sys.stderr)
        print(f"  - Project #{args.project_number} exists for {args.owner}", file=sys.stderr)
        print("  - You have access to the project", file=sys.stderr)
        print("  - gh CLI is authenticated: gh auth status", file=sys.stderr)
        sys.exit(1)

    project_title = project.get('title', 'Unknown Project')
    print(f"Validating: {project_title}")

    # Run validations
    all_issues = []

    # Field validation
    field_issues = validate_fields(project)
    all_issues.extend(field_issues)

    # Item validation
    item_issues = validate_items(project, check_orphans=args.check_orphans)
    all_issues.extend(item_issues)

    # View validation
    view_issues = validate_views(project)
    all_issues.extend(view_issues)

    # Output results
    if args.json:
        result = {
            'project': project_title,
            'owner': args.owner,
            'project_number': args.project_number,
            'issues': all_issues,
            'summary': {
                'errors': len([i for i in all_issues if i['severity'] == 'error']),
                'warnings': len([i for i in all_issues if i['severity'] == 'warning']),
                'info': len([i for i in all_issues if i['severity'] == 'info'])
            }
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['summary']['errors'] == 0 else 1)
    else:
        exit_code = print_validation_results(project_title, all_issues)
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
