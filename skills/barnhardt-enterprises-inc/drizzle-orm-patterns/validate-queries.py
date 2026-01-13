#!/usr/bin/env python3
"""
Drizzle ORM Query Validator

Validates TypeScript files using Drizzle ORM for common security and performance issues.

Usage:
    python validate-queries.py <file1.ts> [file2.ts ...]
    python validate-queries.py src/**/*.ts

Checks for:
- SQL injection risks (string interpolation in sql``)
- Missing parameterized queries
- select * usage (performance)
- Missing indexes on foreign keys
- N+1 query patterns (queries in loops)
"""

import re
import sys
import glob
from pathlib import Path
from typing import List, Tuple, Set
from dataclasses import dataclass


@dataclass
class Issue:
    """Represents a validation issue found in code."""
    file: str
    line: int
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str


class DrizzleValidator:
    """Validates Drizzle ORM usage for security and performance issues."""

    def __init__(self):
        self.issues: List[Issue] = []

    def validate_file(self, filepath: str) -> None:
        """Validate a single TypeScript file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Run all validation checks
            self._check_sql_injection(filepath, content, lines)
            self._check_select_star(filepath, content, lines)
            self._check_n_plus_one(filepath, content, lines)
            self._check_missing_indexes(filepath, content, lines)
            self._check_no_pagination(filepath, content, lines)
            self._check_transaction_issues(filepath, content, lines)
            self._check_type_safety(filepath, content, lines)

        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)

    def _check_sql_injection(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for SQL injection vulnerabilities."""

        # Pattern 1: String interpolation in sql`` templates
        sql_template_pattern = r'sql`[^`]*\$\{[^}]+\}[^`]*`'
        for i, line in enumerate(lines, start=1):
            if re.search(sql_template_pattern, line):
                # Check if it's using sql.placeholder (safe)
                if 'sql.placeholder' not in line and 'sql.raw' not in line:
                    # Check if interpolating variables (dangerous)
                    if re.search(r'\$\{(?!sql\.)[\w.]+\}', line):
                        self.issues.append(Issue(
                            file=filepath,
                            line=i,
                            severity='error',
                            category='SQL Injection',
                            message='String interpolation in sql template detected. Use parameterized queries with eq(), like(), etc.'
                        ))

        # Pattern 2: sql.raw with user input
        sql_raw_pattern = r'sql\.raw\('
        for i, line in enumerate(lines, start=1):
            if re.search(sql_raw_pattern, line):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='warning',
                    category='SQL Injection',
                    message='sql.raw() detected. Ensure this is not using user input. Consider using safe operators instead.'
                ))

        # Pattern 3: Dynamic column/table names
        dynamic_col_pattern = r'\.where\(sql`[^`]*\$\{[\w.]+\}[^`]*`\)'
        for i, line in enumerate(lines, start=1):
            if re.search(dynamic_col_pattern, line):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='error',
                    category='SQL Injection',
                    message='Dynamic column/table name in where clause. Validate against whitelist first.'
                ))

    def _check_select_star(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for select * usage (performance issue)."""

        # Pattern: .select().from(table)
        select_all_pattern = r'\.select\(\)\.from\('
        for i, line in enumerate(lines, start=1):
            if re.search(select_all_pattern, line):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='warning',
                    category='Performance',
                    message='select() without field list detected. Specify fields explicitly for better performance.'
                ))

        # Pattern: SELECT * in raw SQL
        sql_select_star = r'sql`\s*SELECT\s+\*\s+FROM'
        for i, line in enumerate(lines, start=1):
            if re.search(sql_select_star, line, re.IGNORECASE):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='warning',
                    category='Performance',
                    message='SELECT * detected in raw SQL. Specify columns explicitly.'
                ))

    def _check_n_plus_one(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for N+1 query patterns."""

        # Pattern: Query inside for loop
        in_loop = False
        loop_start = 0

        for i, line in enumerate(lines, start=1):
            # Detect loop start
            if re.search(r'\bfor\s*\(.*\bof\b', line) or re.search(r'\.forEach\(', line):
                in_loop = True
                loop_start = i

            # Detect loop end (simplified)
            if in_loop and re.search(r'^\s*\}', line):
                in_loop = False

            # Detect database query in loop
            if in_loop and (
                re.search(r'await\s+db\.select\(', line) or
                re.search(r'await\s+db\.insert\(', line) or
                re.search(r'await\s+db\.update\(', line) or
                re.search(r'await\s+db\.delete\(', line)
            ):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='error',
                    category='Performance',
                    message=f'Possible N+1 query: database operation inside loop (started at line {loop_start}). Use joins or batch operations.'
                ))

    def _check_missing_indexes(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for missing indexes on foreign keys."""

        # Check if this is a schema file
        if 'pgTable' not in content:
            return

        # Pattern: .references(() => table.id)
        references_pattern = r'\.references\(\(\)\s*=>\s*[\w.]+\)'
        index_pattern = r'index\([\'"][\w_]+[\'"]\)\.on\('

        has_references = False
        has_index = False

        for line in lines:
            if re.search(references_pattern, line):
                has_references = True
            if re.search(index_pattern, line):
                has_index = True

        if has_references and not has_index:
            self.issues.append(Issue(
                file=filepath,
                line=1,
                severity='warning',
                category='Performance',
                message='Foreign key reference found without corresponding index. Add index on foreign key column for better join performance.'
            ))

    def _check_no_pagination(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for queries without pagination."""

        # Check for select queries without .limit()
        for i, line in enumerate(lines, start=1):
            if re.search(r'\.select\([^)]*\)\.from\(', line):
                # Look ahead for .limit() in next few lines
                has_limit = False
                for j in range(i, min(i + 5, len(lines))):
                    if '.limit(' in lines[j]:
                        has_limit = True
                        break

                # Check if it's a findFirst (has implicit limit)
                if 'findFirst' in line:
                    has_limit = True

                if not has_limit:
                    self.issues.append(Issue(
                        file=filepath,
                        line=i,
                        severity='info',
                        category='Performance',
                        message='Query without pagination detected. Consider adding .limit() to prevent fetching too many rows.'
                    ))

    def _check_transaction_issues(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for transaction issues."""

        in_transaction = False
        transaction_start = 0

        for i, line in enumerate(lines, start=1):
            # Detect transaction start
            if 'db.transaction(' in line or '.transaction(async' in line:
                in_transaction = True
                transaction_start = i

            # Detect transaction end
            if in_transaction and re.search(r'^\s*\}\);?\s*$', line):
                in_transaction = False

            # Check for external API calls in transaction
            if in_transaction:
                if any(api in line for api in ['fetch(', 'axios.', 'stripe.', 'await sendEmail']):
                    self.issues.append(Issue(
                        file=filepath,
                        line=i,
                        severity='error',
                        category='Transaction',
                        message=f'External API call inside transaction (started at line {transaction_start}). Keep transactions short and move external calls outside.'
                    ))

    def _check_type_safety(self, filepath: str, content: str, lines: List[str]) -> None:
        """Check for type safety issues."""

        # Pattern: Using 'any' type
        for i, line in enumerate(lines, start=1):
            if re.search(r':\s*any\b', line):
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='warning',
                    category='Type Safety',
                    message="Using 'any' type loses type safety. Use proper types or typeof table.$inferSelect."
                ))

        # Pattern: @ts-ignore
        for i, line in enumerate(lines, start=1):
            if '@ts-ignore' in line:
                self.issues.append(Issue(
                    file=filepath,
                    line=i,
                    severity='error',
                    category='Type Safety',
                    message='@ts-ignore detected. Fix type error instead of suppressing it.'
                ))

    def print_report(self) -> int:
        """Print validation report and return exit code."""
        if not self.issues:
            print("✅ No issues found!")
            return 0

        # Group issues by severity
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        infos = [i for i in self.issues if i.severity == 'info']

        # Print errors
        if errors:
            print(f"\n❌ {len(errors)} Error(s):")
            for issue in errors:
                print(f"  {issue.file}:{issue.line} [{issue.category}] {issue.message}")

        # Print warnings
        if warnings:
            print(f"\n⚠️  {len(warnings)} Warning(s):")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line} [{issue.category}] {issue.message}")

        # Print info
        if infos:
            print(f"\nℹ️  {len(infos)} Info:")
            for issue in infos:
                print(f"  {issue.file}:{issue.line} [{issue.category}] {issue.message}")

        # Summary
        print(f"\n📊 Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")

        # Return non-zero exit code if errors found
        return 1 if errors else 0


def expand_globs(patterns: List[str]) -> Set[str]:
    """Expand glob patterns to file paths."""
    files = set()
    for pattern in patterns:
        if '*' in pattern:
            files.update(glob.glob(pattern, recursive=True))
        else:
            files.add(pattern)
    return files


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate-queries.py <file1.ts> [file2.ts ...]")
        print("       python validate-queries.py src/**/*.ts")
        sys.exit(1)

    # Get file paths
    patterns = sys.argv[1:]
    files = expand_globs(patterns)

    if not files:
        print("No files found matching pattern(s)")
        sys.exit(1)

    # Filter TypeScript files
    ts_files = [f for f in files if f.endswith('.ts') or f.endswith('.tsx')]

    if not ts_files:
        print("No TypeScript files found")
        sys.exit(1)

    print(f"Validating {len(ts_files)} file(s)...\n")

    # Validate files
    validator = DrizzleValidator()
    for filepath in sorted(ts_files):
        if Path(filepath).exists():
            validator.validate_file(filepath)
        else:
            print(f"Warning: File not found: {filepath}", file=sys.stderr)

    # Print report and exit
    exit_code = validator.print_report()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
