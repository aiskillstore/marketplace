# -*- coding: utf-8 -*-
"""Slides Data Validator & Fixer

Detect and fix an issue in the slides-data.js file that may cause PPTX conversion to fail.

Usage:
    python validate_data.py <input_file> #Detect problems
    python validate_data.py <input_file> --fix # Detect and fix
    python validate_data.py <input_file> --fix -o <output> # Repair and output to the specified file
    python validate_data.py <input_file> --verbose # Verbose output

Examples:
    python validate_data.py projects/my-slides.js
    python validate_data.py projects/my-slides.js --fix
    python validate_data.py projects/my-slides.js --fix -o projects/my-slides-fixed.js"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Tuple, List, Dict, Any

# Configure stdout encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# ============================================================
# Problem character definition
# ============================================================

# Special Unicode symbols and their replacements
UNICODE_REPLACEMENTS = {
    # Asterisk class
    '✦': '*', '✧': '*', '✶': '*', '✷': '*', '✸': '*', '★': '*', '☆': '*',
    # Geometry
    '◈': '+', '◆': '+', '◇': '-', '◉': 'O', '◎': 'O',
    '●': 'O', '○': 'o', '◐': '=', '◑': '=',
    '■': '[x]', '□': '[ ]', '▪': '-', '▫': '-',
    '◧': '[T]', '◨': '[E]', '◩': '[L]', '◪': '[R]',
    '⬡': '+', '⬢': '#',
    # arrow
    '→': '->', '←': '<-', '↑': '^', '↓': 'v',
    '➔': '->', '➜': '->', '➝': '->', '➞': '->',
    # symbol
    '✕': 'X', '✓': 'V', '✔': 'V', '✗': 'X', '✘': 'X',
    '⚡': '!', '⚙': '#', '∞': '~',
    # other
    '·': '-', '×': 'x', '÷': '/',
}

# Chinese quote replacement (uses Unicode code points to ensure exact match)
CHINESE_QUOTE_REPLACEMENTS = {
    '\u300c': '',  # 「
    '\u300d': '',  # 」
    '\u300e': '',  # 『
    '\u300f': '',  # 』
    '\u201c': '',  # "(left double quotation mark)
    '\u201d': '',  # "(right double quote)
    '\u2018': '',  # '(left single quote)
    '\u2019': '',  # '(right single quote)
}

# Emoji range (simplified version, mainly covers commonly used emoji)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # Various symbols and hieroglyphs
    "\U00002702-\U000027B0"  # Dingbats
    "\U0001F600-\U0001F64F"  # expression
    "\U0001F680-\U0001F6FF"  # Transportation and maps
    "\U0001F1E0-\U0001F1FF"  # banner
    "]+", 
    flags=re.UNICODE
)


# ============================================================
# core function
# ============================================================

def extract_slides_array(content: str) -> Tuple[str, int, int]:
    """Extract SLIDES array from JS file
    
    Returns:
        (array string, starting position, ending position)"""
    match = re.search(r'const\s+SLIDES\s*=\s*\[', content)
    if not match:
        raise ValueError("SLIDES array definition not found")
    
    start_idx = match.end() - 1
    bracket_count = 0
    end_idx = start_idx
    
    for i in range(start_idx, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_idx = i + 1
                break
    
    return content[start_idx:end_idx], start_idx, end_idx


def detect_issues(content: str) -> List[Dict[str, Any]]:
    """Detect problems in files
    
    Returns:
        Question List [{ type, char, line, column, context }]"""
    issues = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for col, char in enumerate(line, 1):
            issue = None
            
            # Detect special Unicode symbols
            if char in UNICODE_REPLACEMENTS:
                issue = {
                    'type': 'unicode_symbol',
                    'char': char,
                    'replacement': UNICODE_REPLACEMENTS[char],
                    'line': line_num,
                    'column': col,
                    'context': line[max(0, col-15):col+15].strip()
                }
            
            # Detect Chinese quotation marks
            elif char in CHINESE_QUOTE_REPLACEMENTS:
                issue = {
                    'type': 'chinese_quote',
                    'char': char,
                    'replacement': CHINESE_QUOTE_REPLACEMENTS[char],
                    'line': line_num,
                    'column': col,
                    'context': line[max(0, col-15):col+15].strip()
                }
            
            if issue:
                issues.append(issue)
        
        # Detect emoji
        for match in EMOJI_PATTERN.finditer(line):
            issues.append({
                'type': 'emoji',
                'char': match.group(),
                'replacement': '*',
                'line': line_num,
                'column': match.start() + 1,
                'context': line[max(0, match.start()-10):match.end()+10].strip()
            })
    
    # Detect comments in array
    try:
        slides_str, start, end = extract_slides_array(content)
        comment_pattern = re.compile(r'//\s*=+.*=+')
        for match in comment_pattern.finditer(slides_str):
            # Calculate actual line number
            prefix = content[:start + match.start()]
            line_num = prefix.count('\n') + 1
            issues.append({
                'type': 'array_comment',
                'char': match.group()[:30] + '...',
                'replacement': '(remove)',
                'line': line_num,
                'column': 1,
                'context': match.group()[:50]
            })
    except ValueError:
        pass
    
    # Detect single quotes within strings (may cause JSON parsing issues)
    # Matches single quotes within double-quoted strings: "...'...'"
    single_quote_in_string = re.compile(r'"[^"]*\'[^"]*"')
    for line_num, line in enumerate(lines, 1):
        for match in single_quote_in_string.finditer(line):
            issues.append({
                'type': 'single_quote_in_string',
                'char': "'",
                'replacement': '(remove or rephrase)',
                'line': line_num,
                'column': match.start() + 1,
                'context': match.group()[:50]
            })
    
    return issues


def fix_content(content: str) -> str:
    """Repair file content"""
    fixed = content
    
    # Replace special Unicode symbols
    for char, replacement in UNICODE_REPLACEMENTS.items():
        fixed = fixed.replace(char, replacement)
    
    # Replace Chinese quotation marks
    for char, replacement in CHINESE_QUOTE_REPLACEMENTS.items():
        fixed = fixed.replace(char, replacement)
    
    # Remove emoji
    fixed = EMOJI_PATTERN.sub('*', fixed)
    
    # Remove delimited comments within an array
    fixed = re.sub(r'\n\s*//\s*=+[^=\n]*=+\s*\n', '\n', fixed)
    
    return fixed


def validate_json_parse(content: str) -> Tuple[bool, str, int]:
    """Verify that the content can be parsed successfully as JSON
    
    Returns:
        (success?, error message, number of slides)"""
    try:
        slides_str, _, _ = extract_slides_array(content)
    except ValueError as e:
        return False, str(e), 0
    
    # Apply JS -> JSON conversion
    js_str = slides_str
    js_str = re.sub(r'//.*$', '', js_str, flags=re.MULTILINE)
    js_str = re.sub(r'/\*[\s\S]*?\*/', '', js_str)
    js_str = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', js_str)
    js_str = js_str.replace("'", '"')
    js_str = re.sub(r',(\s*[}\]])', r'\1', js_str)
    
    try:
        data = json.loads(js_str)
        return True, "", len(data)
    except json.JSONDecodeError as e:
        # Get error context
        context = js_str[max(0, e.pos-30):e.pos+30]
        return False, f"{e.msg} at line {e.lineno}, col {e.colno}: ...{context}...", 0


def print_report(issues: List[Dict], parse_ok: bool, parse_msg: str, slide_count: int, verbose: bool = False):
    """Print test report"""
    print("=" * 60)
    print("Slides Data Validator Report")
    print("=" * 60)
    
    # Statistical question types
    issue_types = {}
    for issue in issues:
        t = issue['type']
        issue_types[t] = issue_types.get(t, 0) + 1
    
    print(f"\ndetected {len(issues)} questions:")
    type_names = {
        'unicode_symbol': 'Special Unicode symbols',
        'chinese_quote': 'Chinese quotation marks',
        'emoji': 'Emoji',
        'array_comment': 'In-array comments',
        'single_quote_in_string': 'single quotes inside string'
    }
    for t, count in issue_types.items():
        print(f"  - {type_names.get(t, t)}: {count} indivual")
    
    if verbose and issues:
        print("Detailed list of questions:")
        print("-" * 60)
        for i, issue in enumerate(issues[:50], 1):  # Limit display to first 50
            print(f"{i:3}. [{issue['type']}] Line {issue['line']}, Col {issue['column']}")
            print(f"     character: {repr(issue['char'])} -> {repr(issue['replacement'])}")
            print(f"     context: {issue['context']}")
        if len(issues) > 50:
            print(f"  ... English {len(issues) - 50} questions not shown")
    
    print("\n" + "-" * 60)
    print("JSON parsing test:")
    if parse_ok:
        print(f"  [OK] Parsed successfully {slide_count} slides")
    else:
        print(f"  [FAIL] Parsing failed: {parse_msg}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Detect and fix issues in slides-data.js file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python validate_data.py projects/my-slides.js # Detection only
  python validate_data.py projects/my-slides.js --fix # Detect and fix (overwrite original file)
  python validate_data.py projects/my-slides.js --fix -o out.js # Fix and output to new file
  python validate_data.py projects/my-slides.js -v # Detailed output"""
    )
    parser.add_argument('input', help='Input JS data file')
    parser.add_argument('--fix', '-f', action='store_true', help='Fix detected issues')
    parser.add_argument('--output', '-o', help='Output file path (overwrites the original file by default)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show details')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode, only output results')
    
    args = parser.parse_args()
    
    # read file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File does not exist: {input_path}")
        sys.exit(1)
    
    content = input_path.read_text(encoding='utf-8')
    
    if not args.quiet:
        print(f"detection file: {input_path}")
        print(f"file size: {len(content)} character, {content.count(chr(10))} OK")
    
    # Detection issues
    issues = detect_issues(content)
    
    # Verify JSON parsing
    parse_ok, parse_msg, slide_count = validate_json_parse(content)
    
    # Print report
    if not args.quiet:
        print_report(issues, parse_ok, parse_msg, slide_count, args.verbose)
    
    # repair
    if args.fix:
        fixed_content = fix_content(content)
        
        # Verify again
        fix_parse_ok, fix_parse_msg, fix_slide_count = validate_json_parse(fixed_content)
        
        if not args.quiet:
            print("Verification after repair:")
            if fix_parse_ok:
                print(f"  [OK] Parsed successfully {fix_slide_count} slides")
            else:
                print(f"  [WARN] Still have problems: {fix_parse_msg}")
                print("You may need to manually fix the single quote issue within the string")
        
        # output
        output_path = Path(args.output) if args.output else input_path
        fixed_content_final = fixed_content
        output_path.write_text(fixed_content_final, encoding='utf-8')
        
        if not args.quiet:
            print(f"\nRepaired file saved: {output_path}")
    
    # Return status code
    if parse_ok or (args.fix and fix_parse_ok):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
