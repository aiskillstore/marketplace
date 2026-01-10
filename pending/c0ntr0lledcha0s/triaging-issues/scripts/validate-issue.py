#!/usr/bin/env python3
"""
Issue Quality Validator
Checks issue quality and completeness
"""

import argparse
import json
import subprocess
import sys

GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'


def run_gh(args):
    """Execute gh command"""
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def check_issue_quality(issue_number):
    """Check quality of an issue"""
    data = run_gh(['issue', 'view', str(issue_number), '--json', 'title,body,labels'])
    if not data:
        print(f"{RED}Issue #{issue_number} not found{NC}")
        return

    issue = json.loads(data)
    title = issue['title']
    body = issue.get('body', '')
    labels = issue.get('labels', [])

    print(f"\n{'='*60}")
    print(f"Issue #{issue_number}: {title}")
    print(f"{'='*60}\n")

    score = 0
    issues = []

    # Check title
    if len(title) > 10:
        score += 15
        print(f"{GREEN}✓{NC} Title is descriptive")
    else:
        issues.append("Title too short")
        print(f"{RED}✗{NC} Title too short")

    # Check body
    if body and len(body) > 50:
        score += 25
        print(f"{GREEN}✓{NC} Has detailed description")
    else:
        issues.append("Missing or short description")
        print(f"{RED}✗{NC} Missing detailed description")

    # Check for steps (bug reports)
    if 'bug' in [l['name'] for l in labels]:
        if any(word in body.lower() for word in ['steps', 'reproduce', 'expected', 'actual']):
            score += 20
            print(f"{GREEN}✓{NC} Has reproduction steps")
        else:
            issues.append("Bug report missing steps to reproduce")
            print(f"{YELLOW}⚠{NC} Missing reproduction steps")

    # Check labels
    if labels:
        score += 20
        print(f"{GREEN}✓{NC} Has labels ({len(labels)})")
    else:
        issues.append("No labels")
        print(f"{RED}✗{NC} No labels applied")

    # Check for related issues
    if '#' in body:
        score += 10
        print(f"{GREEN}✓{NC} References other issues")
    else:
        print(f"{YELLOW}⚠{NC} No issue references")

    # Check for environment details (for bugs)
    if 'bug' in [l['name'] for l in labels]:
        if any(word in body.lower() for word in ['version', 'browser', 'os', 'environment']):
            score += 10
            print(f"{GREEN}✓{NC} Has environment details")
        else:
            issues.append("Bug report missing environment details")
            print(f"{YELLOW}⚠{NC} Missing environment details")

    # Overall
    print(f"\n{' Score: '}{score}/100")

    if score >= 80:
        print(f"{GREEN}Quality: Excellent{NC}")
    elif score >= 60:
        print(f"{YELLOW}Quality: Good{NC}")
    elif score >= 40:
        print(f"{YELLOW}Quality: Needs Improvement{NC}")
    else:
        print(f"{RED}Quality: Poor{NC}")

    if issues:
        print(f"\n{RED}Issues:{NC}")
        for issue in issues:
            print(f"  - {issue}")


def check_batch(filter_query):
    """Check quality for multiple issues"""
    data = run_gh(['issue', 'list', '--search', filter_query, '--json', 'number', '--limit', '50'])
    if not data:
        print("No issues found")
        return

    issues = json.loads(data)
    print(f"\nChecking {len(issues)} issues...\n")

    for issue in issues:
        check_issue_quality(issue['number'])
        print()


def generate_report():
    """Generate quality report"""
    print(f"\n{'='*60}")
    print("Issue Quality Report")
    print(f"{'='*60}\n")

    # Get all open issues
    data = run_gh(['issue', 'list', '--state', 'open', '--json', 'number,title,body,labels', '--limit', '100'])
    if not data:
        print("No issues found")
        return

    issues = json.loads(data)

    excellent = 0
    good = 0
    poor = 0

    for issue in issues:
        # Quick quality check
        has_labels = len(issue.get('labels', [])) > 0
        has_body = len(issue.get('body', '')) > 50

        if has_labels and has_body:
            excellent += 1
        elif has_labels or has_body:
            good += 1
        else:
            poor += 1

    total = len(issues)
    print(f"Total issues: {total}")
    print(f"{GREEN}Excellent:{NC} {excellent} ({excellent/total*100:.0f}%)")
    print(f"{YELLOW}Good:{NC} {good} ({good/total*100:.0f}%)")
    print(f"{RED}Needs Work:{NC} {poor} ({poor/total*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description='Issue Quality Validator')
    subparsers = parser.add_subparsers(dest='command')

    # check
    check_parser = subparsers.add_parser('check', help='Check single issue')
    check_parser.add_argument('issue', type=int, help='Issue number')

    # check-batch
    batch_parser = subparsers.add_parser('check-batch', help='Check multiple issues')
    batch_parser.add_argument('--filter', default='is:open', help='Filter query')

    # report
    subparsers.add_parser('report', help='Generate quality report')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'check':
        check_issue_quality(args.issue)
    elif args.command == 'check-batch':
        check_batch(args.filter)
    elif args.command == 'report':
        generate_report()


if __name__ == '__main__':
    main()
