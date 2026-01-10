#!/usr/bin/env python3
"""
TypeScript Strict Mode Validator

Validates TypeScript files for strict mode violations before compilation.
Returns exit code 0 if all checks pass, 1 if violations found.

Usage:
    python validate-types.py --file path/to/file.ts
    python validate-types.py --dir path/to/directory
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class Violation:
    """Represents a type violation found in code."""

    def __init__(self, file_path: str, line_num: int, rule: str, message: str, line: str):
        self.file_path = file_path
        self.line_num = line_num
        self.rule = rule
        self.message = message
        self.line = line.strip()

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_num} [{self.rule}] {self.message}\n  {self.line}"


class TypeValidator:
    """Validates TypeScript code for strict mode violations."""

    def __init__(self):
        self.violations: List[Violation] = []

    def validate_file(self, file_path: Path) -> None:
        """Validate a single TypeScript file."""
        if not file_path.suffix in ['.ts', '.tsx']:
            return

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            for i, line in enumerate(lines, start=1):
                self._check_line(str(file_path), i, line, lines)

        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    def _check_line(self, file_path: str, line_num: int, line: str, all_lines: List[str]) -> None:
        """Check a single line for violations."""
        # Skip comments
        if line.strip().startswith('//') or line.strip().startswith('*'):
            return

        # Check for 'any' type usage
        self._check_any_type(file_path, line_num, line)

        # Check for @ts-ignore
        self._check_ts_ignore(file_path, line_num, line)

        # Check for non-null assertions
        self._check_non_null_assertion(file_path, line_num, line)

        # Check for console.log in production code
        self._check_console_log(file_path, line_num, line)

        # Check for missing return types on functions
        self._check_missing_return_type(file_path, line_num, line)

        # Check for implicit any in parameters
        self._check_implicit_any(file_path, line_num, line)

    def _check_any_type(self, file_path: str, line_num: int, line: str) -> None:
        """Check for usage of 'any' type."""
        # Skip if it's in a comment or type definition
        if '//' in line and line.index('//') < line.find('any'):
            return

        # Pattern: : any, <any>, any[], Array<any>, etc.
        patterns = [
            r':\s*any\b',           # : any
            r'<any>',                # <any>
            r'any\[\]',              # any[]
            r'Array<any>',           # Array<any>
            r'Promise<any>',         # Promise<any>
            r'\(.*:\s*any\)',        # (param: any)
        ]

        for pattern in patterns:
            if re.search(pattern, line):
                # Allow in test files and type definitions
                if not ('__tests__' in file_path or '.test.' in file_path or '.spec.' in file_path):
                    self.violations.append(Violation(
                        file_path, line_num, 'no-any',
                        "Use of 'any' type detected. Use explicit types or 'unknown' instead.",
                        line
                    ))
                    break

    def _check_ts_ignore(self, file_path: str, line_num: int, line: str) -> None:
        """Check for @ts-ignore comments."""
        if re.search(r'@ts-ignore', line):
            self.violations.append(Violation(
                file_path, line_num, 'no-ts-ignore',
                "Use of @ts-ignore detected. Fix the underlying type error instead.",
                line
            ))

    def _check_non_null_assertion(self, file_path: str, line_num: int, line: str) -> None:
        """Check for non-null assertion operator (!)."""
        # Pattern: something! (but not !== or !=)
        pattern = r'\w+!'

        # Exclude comparison operators
        if '!=' in line or '!==' in line:
            return

        # Look for non-null assertion
        if re.search(r'\w+\s*!\s*[.\[]', line):
            self.violations.append(Violation(
                file_path, line_num, 'no-non-null-assertion',
                "Non-null assertion (!) detected. Use optional chaining or type guards instead.",
                line
            ))

    def _check_console_log(self, file_path: str, line_num: int, line: str) -> None:
        """Check for console.log in production code."""
        if 'console.log' in line or 'console.dir' in line or 'console.table' in line:
            # Allow in test files and development-only code
            if not ('__tests__' in file_path or '.test.' in file_path or '.spec.' in file_path):
                if '__DEV__' not in line and 'process.env.NODE_ENV' not in line:
                    self.violations.append(Violation(
                        file_path, line_num, 'no-console-log',
                        "console.log detected in production code. Use proper logger instead.",
                        line
                    ))

    def _check_missing_return_type(self, file_path: str, line_num: int, line: str) -> None:
        """Check for functions missing explicit return types."""
        # Pattern: function name(...) { or const name = (...) =>
        patterns = [
            r'function\s+\w+\s*\([^)]*\)\s*\{',           # function name() {
            r'const\s+\w+\s*=\s*\([^)]*\)\s*=>',         # const name = () =>
            r'async\s+function\s+\w+\s*\([^)]*\)\s*\{',  # async function name() {
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                # Check if return type is specified (: Type before { or =>)
                if not re.search(r':\s*\w+', match.group()):
                    # Skip test files and type declaration files
                    if not ('__tests__' in file_path or '.test.' in file_path or '.d.ts' in file_path):
                        self.violations.append(Violation(
                            file_path, line_num, 'explicit-return-type',
                            "Function missing explicit return type annotation.",
                            line
                        ))

    def _check_implicit_any(self, file_path: str, line_num: int, line: str) -> None:
        """Check for function parameters without type annotations."""
        # Pattern: function with parameters but no types
        match = re.search(r'function\s+\w+\s*\(([^)]+)\)', line)
        if match:
            params = match.group(1)
            # Check if parameters have type annotations
            if params and ':' not in params:
                # Skip destructured parameters (complex to validate)
                if not '{' in params:
                    self.violations.append(Violation(
                        file_path, line_num, 'no-implicit-any',
                        "Function parameter without type annotation (implicit any).",
                        line
                    ))

    def validate_directory(self, dir_path: Path) -> None:
        """Recursively validate all TypeScript files in directory."""
        for file_path in dir_path.rglob('*.ts'):
            # Skip node_modules and build directories
            if 'node_modules' in str(file_path) or 'dist' in str(file_path) or 'build' in str(file_path):
                continue

            self.validate_file(file_path)

        for file_path in dir_path.rglob('*.tsx'):
            if 'node_modules' in str(file_path) or 'dist' in str(file_path) or 'build' in str(file_path):
                continue

            self.validate_file(file_path)

    def report(self) -> int:
        """Print validation report and return exit code."""
        if not self.violations:
            print("✅ No TypeScript strict mode violations found!")
            return 0

        print(f"❌ Found {len(self.violations)} TypeScript strict mode violation(s):\n")

        # Group violations by file
        violations_by_file = {}
        for violation in self.violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(violation)

        # Print grouped violations
        for file_path in sorted(violations_by_file.keys()):
            print(f"\n{file_path}:")
            for violation in violations_by_file[file_path]:
                print(f"  Line {violation.line_num}: [{violation.rule}] {violation.message}")
                print(f"    {violation.line}")

        print(f"\n❌ Total violations: {len(self.violations)}")
        print("\nFix these violations before committing code.")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate TypeScript files for strict mode violations"
    )
    parser.add_argument(
        '--file',
        type=Path,
        help="Path to a single TypeScript file to validate"
    )
    parser.add_argument(
        '--dir',
        type=Path,
        help="Path to directory to recursively validate"
    )

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(1)

    validator = TypeValidator()

    if args.file:
        if not args.file.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        validator.validate_file(args.file)

    if args.dir:
        if not args.dir.exists():
            print(f"Error: Directory not found: {args.dir}", file=sys.stderr)
            sys.exit(1)

        validator.validate_directory(args.dir)

    sys.exit(validator.report())


if __name__ == '__main__':
    main()
