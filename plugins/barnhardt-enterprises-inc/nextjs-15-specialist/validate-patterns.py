#!/usr/bin/env python3
"""
Next.js 15 Pattern Validator

Validates Next.js 15 App Router patterns and catches common mistakes.
Run this script to check for anti-patterns in your codebase.

Usage:
    python validate-patterns.py [directory]

Example:
    python validate-patterns.py /Users/barnent1/Projects/quetrex/src
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

class ValidationError:
    def __init__(self, file: str, line: int, error: str, suggestion: str):
        self.file = file
        self.line = line
        self.error = error
        self.suggestion = suggestion

    def __str__(self):
        return f"{self.file}:{self.line} - {self.error}\n  Suggestion: {self.suggestion}"


class NextJsValidator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.errors: List[ValidationError] = []

    def validate(self):
        """Run all validation checks"""
        print(f"🔍 Validating Next.js patterns in {self.root_dir}")
        print("=" * 80)

        # Find all TypeScript/JavaScript files
        files = list(self.root_dir.rglob("*.tsx")) + \
                list(self.root_dir.rglob("*.ts")) + \
                list(self.root_dir.rglob("*.jsx")) + \
                list(self.root_dir.rglob("*.js"))

        for file in files:
            # Skip node_modules and .next
            if 'node_modules' in str(file) or '.next' in str(file):
                continue

            self.validate_file(file)

        # Print results
        self.print_results()

        return len(self.errors) == 0

    def validate_file(self, file: Path):
        """Validate a single file"""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Check if file is in app directory
            is_app_dir = '/app/' in str(file) or str(file).startswith('app/')

            # Run checks
            self.check_async_client_component(file, lines)
            self.check_client_apis_in_server_component(file, lines, content)
            self.check_use_client_directive(file, lines, content)
            self.check_server_action_directive(file, lines)
            self.check_image_optimization(file, lines)
            self.check_metadata_usage(file, lines, is_app_dir)
            self.check_dynamic_imports(file, lines, content)
            self.check_fetch_cache_strategy(file, lines)
            self.check_route_segment_config(file, lines, is_app_dir)

        except Exception as e:
            print(f"Error reading {file}: {e}")

    def check_async_client_component(self, file: Path, lines: List[str]):
        """Check for async Client Components (not allowed)"""
        has_use_client = any("'use client'" in line or '"use client"' in line for line in lines)

        if has_use_client:
            for i, line in enumerate(lines):
                # Check for async function component
                if re.search(r'export\s+default\s+async\s+function', line):
                    self.errors.append(ValidationError(
                        str(file),
                        i + 1,
                        "Client Components cannot be async",
                        "Remove 'use client' or remove 'async'. Use useEffect for data fetching in Client Components."
                    ))

    def check_client_apis_in_server_component(self, file: Path, lines: List[str], content: str):
        """Check for browser APIs in Server Components"""
        has_use_client = "'use client'" in content or '"use client"' in content

        if not has_use_client:
            # Server Component - check for client-only APIs
            client_apis = [
                (r'\buseState\b', 'useState'),
                (r'\buseEffect\b', 'useEffect'),
                (r'\buseContext\b', 'useContext'),
                (r'\bwindow\b', 'window'),
                (r'\blocalstorage\b', 'localStorage', re.IGNORECASE),
                (r'\bdocument\b', 'document'),
                (r'\bonClick\b', 'onClick'),
                (r'\bonChange\b', 'onChange'),
            ]

            for i, line in enumerate(lines):
                for pattern, api_name, *flags in client_apis:
                    flag = flags[0] if flags else 0
                    if re.search(pattern, line, flag):
                        self.errors.append(ValidationError(
                            str(file),
                            i + 1,
                            f"Server Components cannot use '{api_name}'",
                            f"Add 'use client' directive at the top of the file to use {api_name}."
                        ))

    def check_use_client_directive(self, file: Path, lines: List[str], content: str):
        """Check 'use client' directive placement"""
        if "'use client'" in content or '"use client"' in content:
            # Find line with 'use client'
            for i, line in enumerate(lines):
                if "'use client'" in line or '"use client"' in line:
                    # Check if it's the first non-empty, non-comment line
                    preceding_lines = lines[:i]
                    non_empty_lines = [l for l in preceding_lines if l.strip() and not l.strip().startswith('//')]

                    if non_empty_lines:
                        self.errors.append(ValidationError(
                            str(file),
                            i + 1,
                            "'use client' must be at the top of the file",
                            "Move 'use client' to the first line, before imports."
                        ))
                    break

    def check_server_action_directive(self, file: Path, lines: List[str]):
        """Check 'use server' directive in Server Actions"""
        for i, line in enumerate(lines):
            # Check for function with 'use server' inside
            if "'use server'" in line or '"use server"' in line:
                # Look for async function definition nearby
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                if not re.search(r'async\s+function', context):
                    self.errors.append(ValidationError(
                        str(file),
                        i + 1,
                        "Server Actions must be async functions",
                        "Add 'async' keyword to the function definition."
                    ))

    def check_image_optimization(self, file: Path, lines: List[str]):
        """Check for unoptimized images"""
        for i, line in enumerate(lines):
            # Check for <img> tag instead of next/image
            if re.search(r'<img\s+', line) and 'next/image' not in '\n'.join(lines):
                self.errors.append(ValidationError(
                    str(file),
                    i + 1,
                    "Use <Image> from next/image instead of <img>",
                    "Import Image from 'next/image' and replace <img> with <Image>."
                ))
                break

    def check_metadata_usage(self, file: Path, lines: List[str], is_app_dir: bool):
        """Check metadata API usage"""
        if is_app_dir and (file.name == 'page.tsx' or file.name == 'page.ts'):
            content = '\n'.join(lines)

            # Check if page exports metadata or generateMetadata
            has_metadata = 'export const metadata' in content
            has_generate_metadata = 'export async function generateMetadata' in content

            if not has_metadata and not has_generate_metadata:
                # Check if there's dynamic content that should have metadata
                if 'params' in content:
                    self.errors.append(ValidationError(
                        str(file),
                        1,
                        "Dynamic pages should export metadata",
                        "Add 'export async function generateMetadata()' for dynamic SEO."
                    ))

    def check_dynamic_imports(self, file: Path, lines: List[str], content: str):
        """Check for proper dynamic imports for heavy components"""
        # Look for 'use client' components that could be dynamically imported
        if "'use client'" in content or '"use client"' in content:
            # Check for heavy libraries without dynamic import
            heavy_libs = ['recharts', 'chart.js', 'three', '@monaco-editor']

            for lib in heavy_libs:
                if f"from '{lib}" in content or f'from "{lib}' in content:
                    if 'dynamic(' not in content:
                        self.errors.append(ValidationError(
                            str(file),
                            1,
                            f"Heavy library '{lib}' should be dynamically imported",
                            f"Use dynamic(() => import(...)) from 'next/dynamic' for better performance."
                        ))

    def check_fetch_cache_strategy(self, file: Path, lines: List[str]):
        """Check fetch calls have proper cache strategy"""
        for i, line in enumerate(lines):
            # Find fetch calls
            if 'fetch(' in line:
                # Check next 5 lines for cache options
                context = '\n'.join(lines[i:min(len(lines), i+5)])

                # Skip if it's in a Client Component
                if "'use client'" in '\n'.join(lines[:i]):
                    continue

                # Check for cache configuration
                has_cache_config = any([
                    'cache:' in context,
                    'next:' in context,
                    'revalidate' in context,
                ])

                if not has_cache_config:
                    self.errors.append(ValidationError(
                        str(file),
                        i + 1,
                        "fetch() should specify cache strategy",
                        "Add { cache: 'force-cache' } or { next: { revalidate: 60 } } to fetch options."
                    ))

    def check_route_segment_config(self, file: Path, lines: List[str], is_app_dir: bool):
        """Check route segment configuration"""
        if is_app_dir and (file.name in ['page.tsx', 'page.ts', 'layout.tsx', 'layout.ts']):
            content = '\n'.join(lines)

            # If dynamic is used, check for valid values
            if 'export const dynamic' in content:
                for i, line in enumerate(lines):
                    if 'export const dynamic' in line:
                        valid_values = ['auto', 'force-dynamic', 'force-static', 'error']
                        has_valid = any(val in line for val in valid_values)

                        if not has_valid:
                            self.errors.append(ValidationError(
                                str(file),
                                i + 1,
                                "Invalid 'dynamic' configuration value",
                                f"Use one of: {', '.join(valid_values)}"
                            ))

    def print_results(self):
        """Print validation results"""
        if not self.errors:
            print("\n✅ No Next.js pattern violations found!")
            print("=" * 80)
            return

        print(f"\n❌ Found {len(self.errors)} pattern violation(s):\n")
        print("=" * 80)

        for error in self.errors:
            print(f"\n{error}")
            print("-" * 80)

        print(f"\n📊 Summary: {len(self.errors)} errors found")
        print("=" * 80)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate-patterns.py <directory>")
        print("\nExample:")
        print("  python validate-patterns.py /Users/barnent1/Projects/quetrex/src")
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)

    validator = NextJsValidator(directory)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
