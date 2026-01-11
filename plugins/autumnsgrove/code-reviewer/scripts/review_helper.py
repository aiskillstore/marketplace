#!/usr/bin/env python3
"""
Code Review Helper Script

Automated code analysis tool for security scanning, complexity metrics,
and report generation.

Usage:
    python review_helper.py --file path/to/file.py --report full
    python review_helper.py --security-scan path/to/directory
    python review_helper.py --complexity path/to/file.py

Dependencies:
    pip install radon bandit safety pylint
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


class CodeReviewer:
    """Automated code review analyzer."""

    def __init__(self, target_path: str):
        self.target_path = Path(target_path)
        self.results = {
            'security': [],
            'complexity': {},
            'quality': [],
            'summary': {}
        }

    def run_security_scan(self) -> List[Dict[str, Any]]:
        """
        Run security vulnerability scanning using Bandit.

        Returns:
            List of security issues found
        """
        print(f"🔒 Running security scan on {self.target_path}...")

        issues = []
        try:
            # Run Bandit security scanner
            cmd = ['bandit', '-r', str(self.target_path), '-f', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    issues.append({
                        'file': issue.get('filename'),
                        'line': issue.get('line_number'),
                        'severity': issue.get('issue_severity'),
                        'confidence': issue.get('issue_confidence'),
                        'issue': issue.get('issue_text'),
                        'code': issue.get('code')
                    })

            self.results['security'] = issues
            print(f"   Found {len(issues)} security issue(s)")

        except FileNotFoundError:
            print("   ⚠️  Bandit not installed. Run: pip install bandit")
        except subprocess.TimeoutExpired:
            print("   ⚠️  Security scan timed out")
        except Exception as e:
            print(f"   ⚠️  Error running security scan: {e}")

        return issues

    def analyze_complexity(self) -> Dict[str, Any]:
        """
        Analyze code complexity using Radon.

        Returns:
            Dictionary with complexity metrics
        """
        print(f"📊 Analyzing code complexity...")

        complexity = {
            'cyclomatic': {},
            'maintainability': {},
            'raw_metrics': {}
        }

        try:
            # Cyclomatic complexity
            cmd = ['radon', 'cc', str(self.target_path), '-s', '-j']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                complexity['cyclomatic'] = json.loads(result.stdout)

            # Maintainability index
            cmd = ['radon', 'mi', str(self.target_path), '-s', '-j']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                complexity['maintainability'] = json.loads(result.stdout)

            # Raw metrics
            cmd = ['radon', 'raw', str(self.target_path), '-s', '-j']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                complexity['raw_metrics'] = json.loads(result.stdout)

            self.results['complexity'] = complexity
            print(f"   ✓ Complexity analysis complete")

        except FileNotFoundError:
            print("   ⚠️  Radon not installed. Run: pip install radon")
        except subprocess.TimeoutExpired:
            print("   ⚠️  Complexity analysis timed out")
        except Exception as e:
            print(f"   ⚠️  Error analyzing complexity: {e}")

        return complexity

    def run_quality_checks(self) -> List[Dict[str, Any]]:
        """
        Run code quality checks using Pylint.

        Returns:
            List of quality issues
        """
        print(f"✨ Running quality checks...")

        issues = []
        try:
            cmd = ['pylint', str(self.target_path), '--output-format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data:
                    issues.append({
                        'file': issue.get('path'),
                        'line': issue.get('line'),
                        'column': issue.get('column'),
                        'type': issue.get('type'),
                        'symbol': issue.get('symbol'),
                        'message': issue.get('message'),
                        'category': issue.get('message-id')
                    })

            self.results['quality'] = issues
            print(f"   Found {len(issues)} quality issue(s)")

        except FileNotFoundError:
            print("   ⚠️  Pylint not installed. Run: pip install pylint")
        except subprocess.TimeoutExpired:
            print("   ⚠️  Quality check timed out")
        except Exception as e:
            print(f"   ⚠️  Error running quality checks: {e}")

        return issues

    def check_dependencies(self) -> List[Dict[str, Any]]:
        """
        Check for vulnerable dependencies using Safety.

        Returns:
            List of vulnerable dependencies
        """
        print(f"📦 Checking dependencies for vulnerabilities...")

        vulnerabilities = []
        try:
            cmd = ['safety', 'check', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.stdout:
                data = json.loads(result.stdout)
                vulnerabilities = data

            print(f"   Found {len(vulnerabilities)} vulnerable dependenc(y/ies)")

        except FileNotFoundError:
            print("   ⚠️  Safety not installed. Run: pip install safety")
        except subprocess.TimeoutExpired:
            print("   ⚠️  Dependency check timed out")
        except Exception as e:
            print(f"   ⚠️  Error checking dependencies: {e}")

        return vulnerabilities

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary of all findings.

        Returns:
            Summary dictionary
        """
        security_count = len(self.results.get('security', []))
        quality_count = len(self.results.get('quality', []))

        # Count high complexity functions
        high_complexity = 0
        complexity_data = self.results.get('complexity', {}).get('cyclomatic', {})
        for file_data in complexity_data.values():
            if isinstance(file_data, list):
                for func in file_data:
                    if func.get('complexity', 0) > 10:
                        high_complexity += 1

        summary = {
            'total_security_issues': security_count,
            'total_quality_issues': quality_count,
            'high_complexity_functions': high_complexity,
            'critical_issues': security_count + high_complexity
        }

        self.results['summary'] = summary
        return summary

    def generate_report(self, output_format: str = 'markdown') -> str:
        """
        Generate comprehensive review report.

        Args:
            output_format: Format for report (markdown, json, text)

        Returns:
            Formatted report string
        """
        if output_format == 'json':
            return json.dumps(self.results, indent=2)

        if output_format == 'markdown':
            return self._generate_markdown_report()

        return self._generate_text_report()

    def _generate_markdown_report(self) -> str:
        """Generate Markdown formatted report."""
        summary = self.results.get('summary', {})

        report = [
            "# Code Review Report",
            "",
            f"**Target:** `{self.target_path}`",
            "",
            "## Summary",
            "",
            f"- 🔒 Security Issues: {summary.get('total_security_issues', 0)}",
            f"- ✨ Quality Issues: {summary.get('total_quality_issues', 0)}",
            f"- 📊 High Complexity Functions: {summary.get('high_complexity_functions', 0)}",
            "",
        ]

        # Security section
        if self.results.get('security'):
            report.extend([
                "## 🔒 Security Issues",
                ""
            ])
            for issue in self.results['security'][:10]:  # Show top 10
                report.append(f"### {issue.get('file')}:{issue.get('line')}")
                report.append(f"**Severity:** {issue.get('severity')} | **Confidence:** {issue.get('confidence')}")
                report.append(f"{issue.get('issue')}")
                report.append("")

        # Complexity section
        complexity = self.results.get('complexity', {}).get('cyclomatic', {})
        if complexity:
            report.extend([
                "## 📊 Complexity Analysis",
                ""
            ])
            high_complexity_funcs = []
            for file_path, functions in complexity.items():
                if isinstance(functions, list):
                    for func in functions:
                        if func.get('complexity', 0) > 10:
                            high_complexity_funcs.append({
                                'file': file_path,
                                'function': func.get('name'),
                                'complexity': func.get('complexity'),
                                'line': func.get('lineno')
                            })

            for func in sorted(high_complexity_funcs, key=lambda x: x['complexity'], reverse=True)[:10]:
                report.append(f"- `{func['function']}` in {func['file']}:{func['line']} - Complexity: {func['complexity']}")

        # Quality issues
        if self.results.get('quality'):
            report.extend([
                "",
                "## ✨ Quality Issues",
                ""
            ])
            for issue in self.results['quality'][:10]:  # Show top 10
                report.append(f"- [{issue.get('type')}] {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")

        report.extend([
            "",
            "---",
            "*Generated by Code Review Helper*"
        ])

        return "\n".join(report)

    def _generate_text_report(self) -> str:
        """Generate plain text report."""
        summary = self.results.get('summary', {})

        lines = [
            "=" * 60,
            "CODE REVIEW REPORT",
            "=" * 60,
            f"Target: {self.target_path}",
            "",
            "SUMMARY:",
            f"  Security Issues: {summary.get('total_security_issues', 0)}",
            f"  Quality Issues: {summary.get('total_quality_issues', 0)}",
            f"  High Complexity Functions: {summary.get('high_complexity_functions', 0)}",
            "",
            "=" * 60
        ]

        return "\n".join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Automated code review helper',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--file', '-f',
        help='Path to file or directory to review',
        required=True
    )

    parser.add_argument(
        '--security-scan',
        action='store_true',
        help='Run security vulnerability scan only'
    )

    parser.add_argument(
        '--complexity',
        action='store_true',
        help='Run complexity analysis only'
    )

    parser.add_argument(
        '--quality',
        action='store_true',
        help='Run quality checks only'
    )

    parser.add_argument(
        '--report',
        choices=['full', 'summary', 'json'],
        default='summary',
        help='Type of report to generate'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file for report (default: stdout)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: Path '{args.file}' does not exist")
        sys.exit(1)

    reviewer = CodeReviewer(args.file)

    # Run selected analyses
    if args.security_scan or args.report == 'full':
        reviewer.run_security_scan()

    if args.complexity or args.report == 'full':
        reviewer.analyze_complexity()

    if args.quality or args.report == 'full':
        reviewer.run_quality_checks()

    if args.report == 'full':
        reviewer.check_dependencies()

    # Generate summary
    reviewer.generate_summary()

    # Generate report
    output_format = 'json' if args.report == 'json' else 'markdown'
    report = reviewer.generate_report(output_format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n✓ Report written to {args.output}")
    else:
        print("\n" + report)


if __name__ == '__main__':
    main()
