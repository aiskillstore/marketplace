#!/usr/bin/env python3
"""
Conventional Commits Helper
Generates and validates conventional commit messages
"""

import argparse
import re
import subprocess
import sys

VALID_TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore', 'ci', 'build', 'revert']

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def run_git(args):
    """Execute git command"""
    try:
        result = subprocess.run(['git'] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error: {e.stderr}{NC}", file=sys.stderr)
        return ""


def validate_message(message):
    """Validate a commit message"""
    lines = message.strip().split('\n')
    subject = lines[0]

    issues = []

    # Check type
    has_valid_type = any(subject.startswith(t + ':') or subject.startswith(t + '(') for t in VALID_TYPES)
    if not has_valid_type:
        issues.append(f"Missing valid type. Use one of: {', '.join(VALID_TYPES)}")

    # Check subject length
    if len(subject) > 72:
        issues.append(f"Subject too long: {len(subject)} chars (max 72)")

    # Check subject ends with period
    if subject.endswith('.'):
        issues.append("Subject should not end with period")

    # Check imperative mood (basic heuristic)
    if any(subject.lower().startswith(t + 'ed ') for t in VALID_TYPES):
        issues.append("Use imperative mood ('add' not 'added')")

    return len(issues) == 0, issues


def generate_from_diff():
    """Generate commit message from staged changes"""
    # Get staged files
    staged = run_git(['diff', '--cached', '--name-only'])
    if not staged:
        print(f"{YELLOW}No staged changes{NC}")
        return

    files = staged.split('\n')
    print(f"\n{BLUE}Staged files:{NC}")
    for f in files[:10]:
        print(f"  - {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

    # Get diff stats
    stats = run_git(['diff', '--cached', '--stat'])

    # Try to infer type and scope
    scope = None
    commit_type = None

    # Infer from paths
    if any('test' in f for f in files):
        commit_type = 'test'
    elif any('.md' in f or 'doc' in f.lower() for f in files):
        commit_type = 'docs'
    elif any('ci' in f or '.github' in f for f in files):
        commit_type = 'ci'

    # Infer scope from common path prefixes
    common_paths = set()
    for f in files:
        parts = f.split('/')
        if len(parts) > 1:
            common_paths.add(parts[0])

    if len(common_paths) == 1:
        scope = list(common_paths)[0]

    print(f"\n{BLUE}Suggested:{ NC}")
    if commit_type:
        print(f"  Type: {commit_type}")
    if scope:
        print(f"  Scope: {scope}")

    print("\n" + "="*60)
    print(stats)
    print("="*60)


def interactive():
    """Interactive commit message builder"""
    print(f"\n{BLUE}=== Interactive Commit Builder ==={NC}\n")

    # Step 1: Show changes
    generate_from_diff()

    # Step 2: Get type
    print(f"\n{BLUE}Step 1: Select type{NC}")
    for i, t in enumerate(VALID_TYPES, 1):
        print(f"  {i}. {t}")

    type_choice = input("Enter number (or type name): ").strip()
    if type_choice.isdigit():
        commit_type = VALID_TYPES[int(type_choice) - 1]
    else:
        commit_type = type_choice

    # Step 3: Get scope (optional)
    print(f"\n{BLUE}Step 2: Enter scope (optional){NC}")
    scope = input("Scope: ").strip()

    # Step 4: Get subject
    print(f"\n{BLUE}Step 3: Enter subject{NC}")
    subject = input("Subject: ").strip()

    # Step 5: Get body (optional)
    print(f"\n{BLUE}Step 4: Enter body (optional, press Enter twice to finish){NC}")
    body_lines = []
    while True:
        line = input()
        if not line:
            break
        body_lines.append(line)
    body = '\n'.join(body_lines)

    # Step 6: Get footer (optional)
    print(f"\n{BLUE}Step 5: Add references (optional){NC}")
    footer = input("Footer (e.g., 'Closes #42'): ").strip()

    # Build message
    if scope:
        message_subject = f"{commit_type}({scope}): {subject}"
    else:
        message_subject = f"{commit_type}: {subject}"

    full_message = message_subject
    if body:
        full_message += "\n\n" + body
    if footer:
        full_message += "\n\n" + footer

    # Preview
    print(f"\n{'='*60}")
    print(full_message)
    print(f"{'='*60}\n")

    # Validate
    is_valid, issues = validate_message(full_message)
    if not is_valid:
        print(f"{YELLOW}Warnings:{NC}")
        for issue in issues:
            print(f"  - {issue}")
        print()

    # Confirm
    confirm = input("Commit with this message? [y/n/e(dit)]: ").strip().lower()

    if confirm == 'y':
        # Write to temp file and commit
        with open('/tmp/commit-msg.txt', 'w') as f:
            f.write(full_message)

        result = run_git(['commit', '-F', '/tmp/commit-msg.txt'])
        if result:
            print(f"\n{GREEN}✓ Committed{NC}")
    elif confirm == 'e':
        print("Opening editor...")
        subprocess.run(['git', 'commit', '-e', '-m', full_message])
    else:
        print("Cancelled")


def validate_branch(branch):
    """Validate all commits on a branch"""
    # Get commits
    commits = run_git(['log', f'main...{branch}', '--format=%H|%s']).split('\n')

    print(f"\n{'='*60}")
    print(f"Validating commits on {branch}")
    print(f"{'='*60}\n")

    valid = 0
    invalid = 0

    for commit_line in commits:
        if not commit_line:
            continue

        commit_hash, subject = commit_line.split('|', 1)
        is_valid, issues = validate_message(subject)

        if is_valid:
            print(f"{GREEN}✓{NC} {commit_hash[:7]}: {subject}")
            valid += 1
        else:
            print(f"{RED}✗{NC} {commit_hash[:7]}: {subject}")
            for issue in issues:
                print(f"  - {issue}")
            invalid += 1

    total = valid + invalid
    print(f"\nValid: {valid}/{total} ({valid/total*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description='Conventional Commits Helper')
    subparsers = parser.add_subparsers(dest='command')

    # validate
    validate_parser = subparsers.add_parser('validate', help='Validate commit message')
    validate_parser.add_argument('message', nargs='?', help='Commit message to validate')

    # generate
    subparsers.add_parser('generate', help='Generate message from changes')

    # interactive
    subparsers.add_parser('interactive', help='Interactive commit builder')

    # validate-branch
    branch_parser = subparsers.add_parser('validate-branch', help='Validate all commits on branch')
    branch_parser.add_argument('branch', help='Branch to validate')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'validate':
        if args.message:
            is_valid, issues = validate_message(args.message)
            if is_valid:
                print(f"{GREEN}✓ Valid conventional commit{NC}")
            else:
                print(f"{RED}✗ Invalid commit message{NC}")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)
        else:
            print("Error: message required")
            sys.exit(1)
    elif args.command == 'generate':
        generate_from_diff()
    elif args.command == 'interactive':
        interactive()
    elif args.command == 'validate-branch':
        validate_branch(args.branch)


if __name__ == '__main__':
    main()
