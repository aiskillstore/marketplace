#!/usr/bin/env python3
"""
Intelligent File Grouping for Commits
Groups modified files by scope, type, and logical relationships
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple, Set

# Color constants
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

# Conventional commit types
COMMIT_TYPES = {
    'feat': 'New feature',
    'fix': 'Bug fix',
    'docs': 'Documentation',
    'test': 'Tests',
    'refactor': 'Code refactoring',
    'perf': 'Performance improvement',
    'chore': 'Maintenance',
    'ci': 'CI/CD changes',
    'build': 'Build system changes',
}

# File patterns for type detection
TYPE_PATTERNS = {
    'test': [r'\.test\.(ts|js|tsx|jsx|py)$', r'\.spec\.(ts|js|tsx|jsx)$', r'^tests?/'],
    'docs': [r'\.md$', r'^docs?/'],
    'config': [r'package\.json$', r'tsconfig\.json$', r'\.config\.(ts|js)$', r'\.(yml|yaml)$'],
}


def run_git(args: List[str]) -> str:
    """Execute git command"""
    try:
        result = subprocess.run(['git'] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Git error: {e.stderr}{NC}", file=sys.stderr)
        return ""


def get_changed_files(mode: str = 'all') -> List[Dict]:
    """Get changed files with stats"""
    files = []

    if mode == 'staged':
        # Only staged files
        status_output = run_git(['diff', '--cached', '--numstat'])
    else:
        # All changes (staged and unstaged)
        status_output = run_git(['diff', 'HEAD', '--numstat'])

    for line in status_output.split('\n'):
        if not line.strip():
            continue

        parts = line.split('\t')
        if len(parts) < 3:
            continue

        added = parts[0] if parts[0] != '-' else '0'
        removed = parts[1] if parts[1] != '-' else '0'
        filepath = parts[2]

        files.append({
            'path': filepath,
            'added': int(added),
            'removed': int(removed),
            'total_changes': int(added) + int(removed),
        })

    # Also check for untracked files if mode is 'all'
    if mode == 'all':
        untracked = run_git(['ls-files', '--others', '--exclude-standard'])
        for filepath in untracked.split('\n'):
            if filepath.strip():
                files.append({
                    'path': filepath.strip(),
                    'added': 0,  # Unknown for untracked
                    'removed': 0,
                    'total_changes': 0,
                })

    return files


def detect_scope(filepath: str) -> str:
    """Detect scope from file path"""
    path = Path(filepath)
    parts = path.parts

    # Common scope patterns
    if len(parts) >= 2:
        if parts[0] in ['src', 'lib', 'app']:
            # src/auth/jwt.ts → auth
            # src/components/Button.tsx → components or ui
            scope = parts[1]
            if scope in ['components', 'pages', 'views', 'layouts']:
                return 'ui'
            return scope
        elif parts[0] == 'tests':
            # tests/auth/jwt.test.ts → auth
            if len(parts) >= 2:
                return parts[1]

    # Fallback: use first directory
    if len(parts) > 1:
        return parts[0]

    return 'root'


def detect_type(filepath: str, added: int, removed: int) -> str:
    """Detect commit type from file characteristics"""
    # Check type patterns
    for type_name, patterns in TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, filepath, re.IGNORECASE):
                return type_name

    # Check if it's a new file (likely feat)
    if removed == 0 and added > 0:
        return 'feat'

    # Check if it's mostly deletions (could be refactor or fix)
    if removed > added and removed > 10:
        return 'refactor'

    # Default: assume feature if substantial additions
    if added > 20:
        return 'feat'

    # Default to fix for small changes
    return 'fix'


def group_files_by_scope(files: List[Dict]) -> Dict[str, List[Dict]]:
    """Group files by scope"""
    groups = defaultdict(list)

    for file_info in files:
        scope = detect_scope(file_info['path'])
        groups[scope].append(file_info)

    return dict(groups)


def group_files_by_type_and_scope(files: List[Dict]) -> List[Dict]:
    """Intelligently group files by type and scope"""
    # First, categorize each file
    categorized = []
    for file_info in files:
        scope = detect_scope(file_info['path'])
        file_type = detect_type(file_info['path'], file_info['added'], file_info['removed'])

        categorized.append({
            **file_info,
            'scope': scope,
            'type': file_type,
        })

    # Group by (type, scope) combination
    groups = defaultdict(list)
    for file_info in categorized:
        key = (file_info['type'], file_info['scope'])
        groups[key].append(file_info)

    # Convert to list of group dicts
    result = []
    for (file_type, scope), file_list in groups.items():
        total_added = sum(f['added'] for f in file_list)
        total_removed = sum(f['removed'] for f in file_list)

        result.append({
            'type': file_type,
            'scope': scope,
            'files': file_list,
            'file_count': len(file_list),
            'lines_added': total_added,
            'lines_removed': total_removed,
            'total_changes': total_added + total_removed,
        })

    # Sort by type priority, then scope
    type_priority = {'feat': 1, 'fix': 2, 'refactor': 3, 'test': 4, 'docs': 5, 'config': 6, 'chore': 7}
    result.sort(key=lambda g: (type_priority.get(g['type'], 99), g['scope']))

    return result


def generate_commit_subject(group: Dict) -> str:
    """Generate commit subject line for a group"""
    commit_type = group['type']
    scope = group['scope']
    file_count = group['file_count']

    # Generate subject based on files
    files = group['files']
    filepaths = [f['path'] for f in files]

    # Try to infer what changed
    if commit_type == 'feat':
        if file_count == 1:
            filename = Path(filepaths[0]).stem
            subject = f"add {filename} functionality"
        else:
            subject = f"add {scope} features"
    elif commit_type == 'fix':
        subject = f"resolve {scope} errors"
    elif commit_type == 'test':
        subject = f"add {scope} tests"
    elif commit_type == 'docs':
        if 'README' in filepaths[0]:
            subject = "update README"
        else:
            subject = f"document {scope}"
    elif commit_type == 'refactor':
        subject = f"refactor {scope} implementation"
    else:
        subject = f"update {scope}"

    return subject


def format_group_display(group: Dict, index: int) -> str:
    """Format group for display"""
    icons = {
        'feat': '📦',
        'fix': '🐛',
        'test': '✅',
        'docs': '📚',
        'refactor': '♻️',
        'perf': '⚡',
        'chore': '🔧',
    }

    icon = icons.get(group['type'], '📝')
    commit_type = group['type']
    scope = group['scope']
    file_count = group['file_count']
    changes = group['total_changes']

    header = f"{icon} Group {index}: {commit_type}({scope}) - {file_count} files, {changes} LOC"

    files_display = []
    for f in group['files']:
        added = f['added']
        removed = f['removed']
        path = f['path']
        sign = '+' if added >= removed else '~'
        files_display.append(f"  {sign} {path} (+{added}, -{removed})")

    subject = generate_commit_subject(group)
    suggested_msg = f"\n  Suggested: {commit_type}({scope}): {subject}"

    return f"{CYAN}{header}{NC}\n" + "\n".join(files_display) + f"{YELLOW}{suggested_msg}{NC}"


def main():
    parser = argparse.ArgumentParser(description='Intelligently group files for commits')
    parser.add_argument('--mode', choices=['all', 'staged', 'scope'], default='all',
                       help='Grouping mode (default: all)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--analyze', action='store_true', help='Show analysis only')

    args = parser.parse_args()

    # Get changed files
    files = get_changed_files(args.mode)

    if not files:
        print(f"{YELLOW}No changes detected.{NC}")
        return 0

    # Group files
    if args.mode == 'scope':
        scope_groups = group_files_by_scope(files)
        print(f"\n{BLUE}Files grouped by scope:{NC}\n")
        for scope, scope_files in scope_groups.items():
            print(f"{GREEN}{scope}:{NC} {len(scope_files)} files")
            for f in scope_files:
                print(f"  - {f['path']}")
    else:
        groups = group_files_by_type_and_scope(files)

        if args.json:
            # Output as JSON
            output = {
                'total_files': len(files),
                'total_groups': len(groups),
                'groups': groups,
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            print(f"\n{BLUE}Found {len(files)} changed files in {len(groups)} logical groups:{NC}\n")
            for i, group in enumerate(groups, 1):
                print(format_group_display(group, i))
                print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
