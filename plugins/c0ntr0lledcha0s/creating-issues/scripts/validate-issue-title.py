#!/usr/bin/env python3
"""
Validate issue titles against project conventions.

Usage:
    python validate-issue-title.py "Issue title here"
    python validate-issue-title.py --file titles.txt
"""

import sys
import re
import argparse

# Type prefixes that should not appear in titles
TYPE_PREFIXES = [
    r'\[BUG\]',
    r'\[FEATURE\]',
    r'\[ENHANCEMENT\]',
    r'\[ENH\]',
    r'\[DOCS\]',
    r'\[DOC\]',
    r'\[DOCUMENTATION\]',
    r'\[REFACTOR\]',
    r'\[CHORE\]',
    r'\[TEST\]',
    r'\[FIX\]',
    r'BUG:',
    r'FEATURE:',
    r'ENHANCEMENT:',
    r'DOC:',
    r'DOCS:',
]

# Recommended title length
MIN_LENGTH = 10
MAX_LENGTH = 72
WARN_LENGTH = 50

def validate_title(title: str) -> dict:
    """
    Validate an issue title against conventions.

    Returns:
        dict with 'valid', 'errors', 'warnings', 'suggestions'
    """
    errors = []
    warnings = []
    suggestions = []

    title = title.strip()

    # Check for empty title
    if not title:
        return {
            'valid': False,
            'errors': ['Title is empty'],
            'warnings': [],
            'suggestions': ['Provide a descriptive title']
        }

    # Check for type prefixes
    for prefix in TYPE_PREFIXES:
        if re.match(prefix, title, re.IGNORECASE):
            errors.append(f'Contains type prefix (remove it, use labels instead)')
            # Suggest fixed title
            fixed = re.sub(prefix + r'\s*', '', title, flags=re.IGNORECASE).strip()
            if fixed:
                suggestions.append(f'Suggested: "{fixed}"')
            break

    # Check length
    if len(title) < MIN_LENGTH:
        errors.append(f'Too short ({len(title)} chars, minimum {MIN_LENGTH})')
        suggestions.append('Be more descriptive about what needs to be done')
    elif len(title) > MAX_LENGTH:
        warnings.append(f'Too long ({len(title)} chars, recommend {WARN_LENGTH}-{MAX_LENGTH})')
        suggestions.append('Consider shortening while keeping clarity')
    elif len(title) > WARN_LENGTH:
        warnings.append(f'Slightly long ({len(title)} chars, ideal is {WARN_LENGTH} or less)')

    # Check for vague titles
    vague_patterns = [
        (r'^fix\s+bug$', 'Too vague - describe what bug'),
        (r'^update\s+code$', 'Too vague - describe what update'),
        (r'^add\s+feature$', 'Too vague - describe what feature'),
        (r'^fix\s+issue$', 'Too vague - describe what issue'),
        (r'^change\s+', 'Consider using more specific verb'),
        (r'^do\s+', 'Too vague - use specific action verb'),
    ]

    for pattern, message in vague_patterns:
        if re.match(pattern, title, re.IGNORECASE):
            warnings.append(message)

    # Check for imperative mood (should start with verb)
    # Common non-imperative patterns
    non_imperative = [
        (r'^(the|a|an)\s+', 'Should start with verb (imperative mood)'),
        (r'^(this|that|these)\s+', 'Should start with verb (imperative mood)'),
        (r'^(i|we)\s+', 'Should start with verb, not pronoun'),
    ]

    for pattern, message in non_imperative:
        if re.match(pattern, title, re.IGNORECASE):
            warnings.append(message)
            break

    # Check for common good patterns
    good_patterns = [
        r'^(fix|add|update|remove|improve|implement|refactor|create|delete|move|rename|extract|simplify|optimize|validate|check|ensure|enable|disable|support|handle|convert|migrate|upgrade|downgrade)\s+',
    ]

    has_good_pattern = any(re.match(p, title, re.IGNORECASE) for p in good_patterns)
    if not has_good_pattern and not errors:
        suggestions.append('Consider starting with an action verb: Fix, Add, Update, Improve, etc.')

    # Check for ending punctuation (not recommended)
    if title.endswith('.'):
        warnings.append('Titles typically do not end with a period')

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'suggestions': suggestions
    }


def format_result(title: str, result: dict) -> str:
    """Format validation result for display."""
    lines = []

    if result['valid'] and not result['warnings']:
        lines.append(f'✅ Title is valid: "{title}"')
    elif result['valid']:
        lines.append(f'⚠️ Title is valid with warnings: "{title}"')
    else:
        lines.append(f'❌ Title has issues: "{title}"')

    if result['errors']:
        lines.append('\nErrors:')
        for error in result['errors']:
            lines.append(f'  - {error}')

    if result['warnings']:
        lines.append('\nWarnings:')
        for warning in result['warnings']:
            lines.append(f'  - {warning}')

    if result['suggestions']:
        lines.append('\nSuggestions:')
        for suggestion in result['suggestions']:
            lines.append(f'  - {suggestion}')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Validate issue titles against project conventions'
    )
    parser.add_argument(
        'title',
        nargs='?',
        help='Issue title to validate'
    )
    parser.add_argument(
        '--file', '-f',
        help='File containing titles to validate (one per line)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    if args.file:
        # Validate multiple titles from file
        try:
            with open(args.file, 'r') as f:
                titles = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f'Error: File not found: {args.file}', file=sys.stderr)
            sys.exit(1)

        all_valid = True
        for title in titles:
            result = validate_title(title)
            print(format_result(title, result))
            print()
            if not result['valid']:
                all_valid = False

        sys.exit(0 if all_valid else 1)

    elif args.title:
        # Validate single title
        result = validate_title(args.title)

        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            print(format_result(args.title, result))

        sys.exit(0 if result['valid'] else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
