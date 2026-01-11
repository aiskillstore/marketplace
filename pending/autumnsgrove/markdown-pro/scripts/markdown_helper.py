#!/usr/bin/env python3
"""
Markdown Helper Utilities

Provides tools for working with Markdown documentation:
- Generate table of contents from headers
- Create changelogs from git history
- Validate markdown links

Usage:
    python markdown_helper.py toc <file.md>
    python markdown_helper.py changelog --since <tag> --output CHANGELOG.md
    python markdown_helper.py validate <directory>
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
from datetime import datetime


def extract_headers(markdown_content: str) -> List[Tuple[int, str, str]]:
    """
    Extract headers from markdown content.

    Args:
        markdown_content: Markdown file content

    Returns:
        List of tuples (level, text, anchor)
    """
    headers = []
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    for match in header_pattern.finditer(markdown_content):
        level = len(match.group(1))
        text = match.group(2).strip()

        # Generate anchor (GitHub style)
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[-\s]+', '-', anchor)

        headers.append((level, text, anchor))

    return headers


def generate_toc(file_path: str, max_level: int = 3) -> str:
    """
    Generate table of contents from markdown file.

    Args:
        file_path: Path to markdown file
        max_level: Maximum header level to include (default: 3)

    Returns:
        Generated table of contents as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    headers = extract_headers(content)

    # Skip the first H1 (usually the title)
    headers = [h for h in headers if h[0] > 1 and h[0] <= max_level]

    if not headers:
        return "No headers found to generate TOC"

    toc_lines = ["## Table of Contents\n"]

    for level, text, anchor in headers:
        indent = "  " * (level - 2)  # H2 = no indent, H3 = 2 spaces, etc.
        toc_lines.append(f"{indent}- [{text}](#{anchor})")

    return "\n".join(toc_lines)


def get_git_commits(since_tag: str = None) -> List[dict]:
    """
    Get git commits with metadata.

    Args:
        since_tag: Git tag to start from (optional)

    Returns:
        List of commit dictionaries
    """
    try:
        # Build git log command
        cmd = [
            'git', 'log',
            '--pretty=format:%H|%h|%an|%ae|%ad|%s|%b',
            '--date=short'
        ]

        if since_tag:
            cmd.append(f'{since_tag}..HEAD')

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        commits = []
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            parts = line.split('|', 6)
            if len(parts) >= 6:
                commits.append({
                    'hash': parts[0],
                    'short_hash': parts[1],
                    'author': parts[2],
                    'email': parts[3],
                    'date': parts[4],
                    'subject': parts[5],
                    'body': parts[6] if len(parts) > 6 else ''
                })

        return commits

    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git not installed")
        sys.exit(1)


def categorize_commit(commit_message: str) -> str:
    """
    Categorize commit based on conventional commits format.

    Args:
        commit_message: Commit message

    Returns:
        Category string
    """
    message_lower = commit_message.lower()

    if message_lower.startswith(('feat:', 'feature:')):
        return 'Added'
    elif message_lower.startswith('fix:'):
        return 'Fixed'
    elif message_lower.startswith(('docs:', 'doc:')):
        return 'Documentation'
    elif message_lower.startswith(('style:', 'format:')):
        return 'Changed'
    elif message_lower.startswith('refactor:'):
        return 'Changed'
    elif message_lower.startswith(('test:', 'tests:')):
        return 'Tests'
    elif message_lower.startswith(('perf:', 'performance:')):
        return 'Performance'
    elif message_lower.startswith('security:'):
        return 'Security'
    elif message_lower.startswith(('chore:', 'build:', 'ci:')):
        return 'Maintenance'
    elif 'breaking' in message_lower or 'breaking change' in message_lower:
        return 'Breaking Changes'
    else:
        return 'Changed'


def generate_changelog(since_tag: str = None, output_file: str = None) -> str:
    """
    Generate changelog from git history.

    Args:
        since_tag: Git tag to start from
        output_file: Output file path (optional)

    Returns:
        Generated changelog string
    """
    commits = get_git_commits(since_tag)

    if not commits:
        return "No commits found"

    # Categorize commits
    categories = {
        'Breaking Changes': [],
        'Added': [],
        'Changed': [],
        'Fixed': [],
        'Security': [],
        'Performance': [],
        'Documentation': [],
        'Tests': [],
        'Maintenance': []
    }

    for commit in commits:
        category = categorize_commit(commit['subject'])
        if category in categories:
            # Extract PR number if present
            pr_match = re.search(r'#(\d+)', commit['subject'])
            pr_suffix = f" (#{pr_match.group(1)})" if pr_match else ""

            # Clean up commit message
            message = commit['subject']
            message = re.sub(r'^(\w+):\s*', '', message)  # Remove prefix
            message = re.sub(r'\s*\(#\d+\)$', '', message)  # Remove PR number

            categories[category].append(f"- {message}{pr_suffix}")

    # Build changelog
    version = "Unreleased"
    date = datetime.now().strftime("%Y-%m-%d")

    changelog_lines = [
        "# Changelog\n",
        f"## [{version}] - {date}\n"
    ]

    for category, entries in categories.items():
        if entries:
            changelog_lines.append(f"### {category}\n")
            changelog_lines.extend(entries)
            changelog_lines.append("")  # Empty line between sections

    changelog = "\n".join(changelog_lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(changelog)
        print(f"Changelog written to {output_file}")

    return changelog


def validate_links(directory: str) -> List[str]:
    """
    Validate markdown links in directory.

    Args:
        directory: Directory to scan for markdown files

    Returns:
        List of broken link errors
    """
    errors = []
    md_files = Path(directory).rglob("*.md")

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            errors.append(f"{md_file}: Error reading file - {e}")
            continue

        # Find all markdown links
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip external URLs (http/https)
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue

            # Check if local file exists
            link_path = (md_file.parent / link_url).resolve()

            if not link_path.exists():
                errors.append(f"{md_file}:{match.start()} - Broken link: [{link_text}]({link_url})")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Markdown documentation helper utilities'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # TOC command
    toc_parser = subparsers.add_parser('toc', help='Generate table of contents')
    toc_parser.add_argument('file', help='Markdown file path')
    toc_parser.add_argument('--max-level', type=int, default=3,
                           help='Maximum header level (default: 3)')

    # Changelog command
    changelog_parser = subparsers.add_parser('changelog',
                                            help='Generate changelog from git')
    changelog_parser.add_argument('--since', help='Git tag to start from')
    changelog_parser.add_argument('--output', help='Output file path')

    # Validate command
    validate_parser = subparsers.add_parser('validate',
                                           help='Validate markdown links')
    validate_parser.add_argument('directory', help='Directory to validate')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'toc':
        toc = generate_toc(args.file, args.max_level)
        print(toc)

    elif args.command == 'changelog':
        changelog = generate_changelog(args.since, args.output)
        if not args.output:
            print(changelog)

    elif args.command == 'validate':
        errors = validate_links(args.directory)
        if errors:
            print(f"Found {len(errors)} broken links:\n")
            for error in errors:
                print(error)
            sys.exit(1)
        else:
            print("All links are valid!")


if __name__ == '__main__':
    main()
