#!/usr/bin/env python3
"""
Git Commit Analyzer
Analyzes commit quality, format compliance, and suggests improvements
"""

import argparse
import re
import subprocess
import sys
from typing import List, Dict, Tuple

# Color constants
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Conventional commit types
VALID_TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore', 'ci', 'build', 'revert']

# Conventional commit pattern
CONVENTIONAL_PATTERN = re.compile(
    r'^(' + '|'.join(VALID_TYPES) + r')(\([a-z0-9-]+\))?!?: .{1,50}$'
)


def run_git(args: List[str]) -> str:
    """Execute git command"""
    try:
        result = subprocess.run(['git'] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Git error: {e.stderr}{NC}", file=sys.stderr)
        return ""


def get_commits(branch: str = None, count: int = 20) -> List[Dict]:
    """Get recent commits"""
    if branch:
        # Commits on branch not in main
        range_spec = f"main...{branch}"
    else:
        range_spec = f"-{count}"

    log_output = run_git(['log', range_spec, '--format=%H|%s|%b|%an|%ae'])

    commits = []
    for line in log_output.split('\n\n'):
        if not line.strip():
            continue

        parts = line.split('|', 4)
        if len(parts) >= 2:
            commits.append({
                'hash': parts[0],
                'subject': parts[1],
                'body': parts[2] if len(parts) > 2 else '',
                'author': parts[3] if len(parts) > 3 else '',
                'email': parts[4] if len(parts) > 4 else ''
            })

    return commits


def get_commit_stats(commit_hash: str) -> Tuple[int, int]:
    """Get insertions and deletions for a commit"""
    stats = run_git(['show', '--stat', '--format=', commit_hash])

    insertions = 0
    deletions = 0

    # Parse stats line like: "5 files changed, 123 insertions(+), 45 deletions(-)"
    match = re.search(r'(\d+) insertion', stats)
    if match:
        insertions = int(match.group(1))

    match = re.search(r'(\d+) deletion', stats)
    if match:
        deletions = int(match.group(1))

    return insertions, deletions


def check_conventional_format(subject: str) -> Tuple[bool, List[str]]:
    """Check if commit message follows conventional commits"""
    issues = []

    # Check pattern
    if not CONVENTIONAL_PATTERN.match(subject):
        # Try to identify specific issues
        if not any(subject.startswith(t) for t in VALID_TYPES):
            issues.append(f"Missing or invalid type. Valid types: {', '.join(VALID_TYPES)}")

        if len(subject) > 72:
            issues.append(f"Subject too long ({len(subject)} chars). Keep under 72 chars.")

        if subject.endswith('.'):
            issues.append("Subject should not end with a period")

        if subject != subject.lower() and not any(subject.startswith(t.upper()) for t in VALID_TYPES):
            issues.append("Subject should be lowercase (except type)")

    return len(issues) == 0, issues


def analyze_commit_quality(commit: Dict) -> Dict:
    """Analyze individual commit quality"""
    subject = commit['subject']
    body = commit['body']

    quality = {
        'hash': commit['hash'][:7],
        'subject': subject,
        'score': 0,
        'issues': [],
        'suggestions': []
    }

    # Check format (weight: 30 points)
    is_conventional, format_issues = check_conventional_format(subject)
    if is_conventional:
        quality['score'] += 30
    else:
        quality['issues'].extend(format_issues)

    # Check subject quality (weight: 25 points)
    if len(subject) > 10:
        quality['score'] += 10
    else:
        quality['issues'].append("Subject too short")

    if not any(vague in subject.lower() for vague in ['wip', 'temp', 'stuff', 'things', 'update', 'fix']):
        quality['score'] += 15
    else:
        quality['issues'].append("Subject too vague")
        quality['suggestions'].append("Be more specific about what changed")

    # Check body (weight: 20 points)
    if body and len(body) > 20:
        quality['score'] += 20
    elif len(subject) > 50:
        quality['suggestions'].append("Consider adding a body to explain changes")

    # Check issue references (weight: 15 points)
    if re.search(r'(closes?|fixes?|resolves?) #\d+', body, re.IGNORECASE):
        quality['score'] += 15
    elif re.search(r'#\d+', subject + body):
        quality['score'] += 10
        quality['suggestions'].append("Use 'Closes #N' syntax for automatic issue closing")
    else:
        quality['suggestions'].append("Add issue reference if applicable")

    # Check commit size (weight: 10 points)
    insertions, deletions = get_commit_stats(commit['hash'])
    total_changes = insertions + deletions

    if total_changes < 500:
        quality['score'] += 10
    elif total_changes < 1000:
        quality['score'] += 5
        quality['suggestions'].append("Consider splitting into smaller commits")
    else:
        quality['issues'].append(f"Very large commit ({total_changes} LOC)")
        quality['suggestions'].append("Definitely split into multiple atomic commits")

    quality['size'] = total_changes

    # Overall rating
    if quality['score'] >= 80:
        quality['rating'] = f"{GREEN}Excellent{NC}"
    elif quality['score'] >= 60:
        quality['rating'] = f"{BLUE}Good{NC}"
    elif quality['score'] >= 40:
        quality['rating'] = f"{YELLOW}Needs Improvement{NC}"
    else:
        quality['rating'] = f"{RED}Poor{NC}"

    return quality


def check_format(branch: str = None):
    """Check format compliance for commits"""
    commits = get_commits(branch=branch)

    print(f"\n{'='*60}")
    print(f"Checking Conventional Commit Format")
    print(f"{'='*60}\n")

    compliant = 0
    non_compliant = 0

    for commit in commits:
        is_conventional, issues = check_conventional_format(commit['subject'])

        if is_conventional:
            print(f"{GREEN}✓{NC} {commit['hash'][:7]}: {commit['subject']}")
            compliant += 1
        else:
            print(f"{RED}✗{NC} {commit['hash'][:7]}: {commit['subject']}")
            for issue in issues:
                print(f"  - {issue}")
            non_compliant += 1

    print(f"\nCompliance: {compliant}/{len(commits)} ({compliant/len(commits)*100:.0f}%)")

    if non_compliant > 0:
        print(f"\n{YELLOW}Suggestion:{NC} Run interactive rebase to fix non-compliant messages")


def find_fixups(branch: str = None):
    """Find commits that could be squashed"""
    commits = get_commits(branch=branch)

    print(f"\n{'='*60}")
    print(f"Finding Fixup Opportunities")
    print(f"{'='*60}\n")

    fixup_candidates = []

    for i, commit in enumerate(commits):
        subject = commit['subject'].lower()

        # Check for WIP/fixup/temp commits
        if any(marker in subject for marker in ['wip', 'fixup', 'temp', 'tmp', 'checkpoint']):
            fixup_candidates.append({
                'index': i,
                'commit': commit,
                'reason': 'Temporary commit'
            })

        # Check for very similar subjects (potential duplicates)
        for j, other_commit in enumerate(commits[i+1:], start=i+1):
            if len(subject) > 10 and subject in other_commit['subject'].lower():
                fixup_candidates.append({
                    'index': i,
                    'commit': commit,
                    'related_index': j,
                    'related_commit': other_commit,
                    'reason': 'Similar to another commit'
                })
                break

    if not fixup_candidates:
        print(f"{GREEN}✓{NC} No fixup opportunities found. Commit history looks clean!")
        return

    print(f"Found {len(fixup_candidates)} fixup opportunities:\n")

    for candidate in fixup_candidates:
        commit = candidate['commit']
        print(f"{YELLOW}→{NC} {commit['hash'][:7]}: {commit['subject']}")
        print(f"  Reason: {candidate['reason']}")

        if 'related_commit' in candidate:
            related = candidate['related_commit']
            print(f"  Related: {related['hash'][:7]}: {related['subject']}")

        print()

    print(f"\n{BLUE}Suggestion:{NC} Use interactive rebase to squash/fixup these commits")


def analyze_size(branch: str = None):
    """Analyze commit sizes"""
    commits = get_commits(branch=branch)

    print(f"\n{'='*60}")
    print(f"Commit Size Analysis")
    print(f"{'='*60}\n")

    sizes = []

    for commit in commits:
        insertions, deletions = get_commit_stats(commit['hash'])
        total = insertions + deletions
        sizes.append(total)

        # Categorize
        if total < 10:
            category = f"{BLUE}Tiny{NC}"
        elif total < 50:
            category = f"{GREEN}Small{NC}"
        elif total < 200:
            category = f"{YELLOW}Medium{NC}"
        elif total < 500:
            category = f"{YELLOW}Large{NC}"
        else:
            category = f"{RED}Very Large{NC}"

        print(f"{commit['hash'][:7]}: {total:4d} LOC - {category}")
        if total > 500:
            print(f"  ⚠️  Consider splitting this commit")
        print(f"  {commit['subject']}")
        print()

    # Statistics
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    print(f"\nAverage commit size: {avg_size:.0f} LOC")
    print(f"Largest commit: {max(sizes)} LOC")
    print(f"Smallest commit: {min(sizes)} LOC")


def generate_report(branch: str = None):
    """Generate comprehensive quality report"""
    commits = get_commits(branch=branch)

    print(f"\n{'='*60}")
    print(f"Commit Quality Report")
    if branch:
        print(f"Branch: {branch}")
    print(f"{'='*60}\n")

    print(f"Analyzed {len(commits)} commits\n")

    excellent = 0
    good = 0
    needs_improvement = 0
    poor = 0

    for commit in commits:
        quality = analyze_commit_quality(commit)

        print(f"{quality['hash']}: {quality['subject'][:60]}")
        print(f"  Score: {quality['score']}/100 - {quality['rating']}")

        if quality['issues']:
            print(f"  {RED}Issues:{NC}")
            for issue in quality['issues']:
                print(f"    - {issue}")

        if quality['suggestions']:
            print(f"  {BLUE}Suggestions:{NC}")
            for suggestion in quality['suggestions']:
                print(f"    - {suggestion}")

        print()

        # Count ratings
        if quality['score'] >= 80:
            excellent += 1
        elif quality['score'] >= 60:
            good += 1
        elif quality['score'] >= 40:
            needs_improvement += 1
        else:
            poor += 1

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}\n")
    print(f"{GREEN}Excellent:{NC} {excellent}")
    print(f"{BLUE}Good:{NC} {good}")
    print(f"{YELLOW}Needs Improvement:{NC} {needs_improvement}")
    print(f"{RED}Poor:{NC} {poor}")

    overall_quality = (excellent + good) / len(commits) * 100 if commits else 0
    print(f"\nOverall Quality: {overall_quality:.0f}%")


def main():
    parser = argparse.ArgumentParser(description='Git Commit Analyzer')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # check-format
    format_parser = subparsers.add_parser('check-format', help='Check conventional commit format')
    format_parser.add_argument('--branch', help='Branch to analyze')

    # find-fixups
    fixup_parser = subparsers.add_parser('find-fixups', help='Find commits to squash/fixup')
    fixup_parser.add_argument('--branch', help='Branch to analyze')

    # analyze-size
    size_parser = subparsers.add_parser('analyze-size', help='Analyze commit sizes')
    size_parser.add_argument('--branch', help='Branch to analyze')

    # report
    report_parser = subparsers.add_parser('report', help='Generate full quality report')
    report_parser.add_argument('--branch', help='Branch to analyze')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == 'check-format':
        check_format(args.branch)
    elif args.command == 'find-fixups':
        find_fixups(args.branch)
    elif args.command == 'analyze-size':
        analyze_size(args.branch)
    elif args.command == 'report':
        generate_report(args.branch)


if __name__ == '__main__':
    main()
