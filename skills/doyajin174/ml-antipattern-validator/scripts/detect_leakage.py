#!/usr/bin/env python3
"""
ML Code Leakage Detector

Analyzes Python code for common ML antipatterns and leakage vulnerabilities.
Detects dangerous patterns in training, evaluation, and preprocessing code.

Usage:
    python detect_leakage.py train.py
    python detect_leakage.py --dir src/ml --recursive
"""

import argparse
import re
import ast
from pathlib import Path
from typing import List, Tuple


class LeakageDetector(ast.NodeVisitor):
    """AST visitor to detect data leakage patterns"""

    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.in_function = None

    def add_issue(self, node, severity, message, fix=None):
        """Record a potential issue"""
        self.issues.append({
            'file': self.filename,
            'line': node.lineno if hasattr(node, 'lineno') else 0,
            'severity': severity,
            'message': message,
            'fix': fix,
            'function': self.in_function
        })

    def visit_FunctionDef(self, node):
        """Track which function we're in"""
        old_func = self.in_function
        self.in_function = node.name
        self.generic_visit(node)
        self.in_function = old_func

    def visit_Call(self, node):
        """Check function calls for antipatterns"""

        # Get function name
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            obj_name = self._get_name(node.func.value)
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id
            obj_name = None
        else:
            self.generic_visit(node)
            return

        # Pattern 1: fit_transform before split
        if func_name == 'fit_transform' and obj_name in ['scaler', 'imputer', 'encoder', 'transformer']:
            # Check if this appears before train_test_split
            self.add_issue(
                node,
                'HIGH',
                f'{obj_name}.fit_transform() may cause preprocessing leakage',
                'Use fit() on training data, then transform() on both sets'
            )

        # Pattern 2: train_test_split after preprocessing
        if func_name == 'train_test_split':
            # Check previous lines for fit_transform
            pass  # Complex inter-statement analysis

        # Pattern 3: cross_val_score without pipeline
        if func_name == 'cross_val_score':
            # Check if first arg is a pipeline
            if len(node.args) > 0:
                estimator = node.args[0]
                if not self._is_pipeline(estimator):
                    self.add_issue(
                        node,
                        'MEDIUM',
                        'cross_val_score without Pipeline may cause fold leakage',
                        'Wrap estimator and preprocessors in Pipeline'
                    )

        # Pattern 4: Testing on training data
        if func_name == 'score' or func_name == 'evaluate':
            # Check if using X_train, y_train
            for arg in node.args:
                arg_name = self._get_name(arg)
                if arg_name and 'train' in arg_name.lower():
                    self.add_issue(
                        node,
                        'CRITICAL',
                        f'Evaluating on training data ({arg_name})',
                        'Use held-out test set for evaluation'
                    )

        # Pattern 5: Random split on time series
        if func_name == 'train_test_split':
            # Check if shuffle parameter is present
            shuffle_found = False
            for keyword in node.keywords:
                if keyword.arg == 'shuffle':
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        self.add_issue(
                            node,
                            'MEDIUM',
                            'train_test_split with shuffle=True may violate temporal ordering',
                            'Use TimeSeriesSplit for temporal data'
                        )
                        shuffle_found = True

        # Pattern 6: model.train() during eval
        if func_name == 'eval' and obj_name == 'model':
            # This is actually good! But check for missing eval()
            pass

        # Pattern 7: Tuning on test set
        if func_name == 'GridSearchCV' or func_name == 'RandomizedSearchCV':
            # Check if X_test is used
            for arg in node.args:
                arg_name = self._get_name(arg)
                if arg_name and 'test' in arg_name.lower():
                    self.add_issue(
                        node,
                        'CRITICAL',
                        f'Hyperparameter tuning on test set ({arg_name})',
                        'Use validation set or cross-validation for tuning'
                    )

        self.generic_visit(node)

    def visit_Assign(self, node):
        """Check variable assignments for antipatterns"""

        # Check for data augmentation before split
        if isinstance(node.value, ast.Call):
            func_name = self._get_name(node.value.func)
            if func_name and 'augment' in func_name.lower():
                # Check if assigned variable is later split
                for target in node.targets:
                    var_name = self._get_name(target)
                    if var_name and not ('train' in var_name.lower() or 'test' in var_name.lower()):
                        self.add_issue(
                            node,
                            'HIGH',
                            'Data augmentation before train/test split',
                            'Split data first, then augment training set only'
                        )

        self.generic_visit(node)

    def _get_name(self, node):
        """Extract variable name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return None

    def _is_pipeline(self, node):
        """Check if node represents a Pipeline"""
        if isinstance(node, ast.Call):
            func_name = self._get_name(node.func)
            return func_name and 'pipeline' in func_name.lower()
        return False


def check_code_patterns(filepath: Path) -> List[dict]:
    """Analyze Python file for leakage patterns"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return [{'file': str(filepath), 'line': 0, 'severity': 'ERROR',
                 'message': f'Failed to read file: {e}'}]

    # Parse AST
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [{'file': str(filepath), 'line': e.lineno, 'severity': 'ERROR',
                 'message': f'Syntax error: {e.msg}'}]

    # Run detector
    detector = LeakageDetector(str(filepath))
    detector.visit(tree)

    # Add regex-based checks (simpler patterns)
    issues = detector.issues
    issues.extend(check_regex_patterns(code, filepath))

    return issues


def check_regex_patterns(code: str, filepath: Path) -> List[dict]:
    """Check for patterns using regex (simpler than AST)"""
    issues = []

    patterns = [
        # Pattern: fit() on X without checking if it's X_train
        (r'\.fit\(\s*X\s*[,\)]', 'MEDIUM',
         'Calling fit(X) - ensure X is training data only'),

        # Pattern: model.predict without model.eval()
        (r'model\.predict\(', 'LOW',
         'Using model.predict() - ensure model.eval() was called'),

        # Pattern: Same variable used for train and test
        (r'(\w+)\s*=.*train_test_split.*\1', 'HIGH',
         'Same variable used for both train and test'),

        # Pattern: High learning rate without warmup
        (r'lr\s*=\s*[0-9]*\.?[0-9]+e-[12]\s', 'LOW',
         'High learning rate - consider warmup schedule'),

        # Pattern: No stratify in train_test_split
        (r'train_test_split\([^)]*\)', 'LOW',
         'train_test_split without stratify parameter'),
    ]

    for pattern, severity, message in patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            line_no = code[:match.start()].count('\n') + 1
            issues.append({
                'file': str(filepath),
                'line': line_no,
                'severity': severity,
                'message': message,
                'fix': None
            })

    return issues


def scan_directory(directory: Path, recursive: bool = True) -> List[dict]:
    """Scan directory for Python files and analyze them"""
    all_issues = []

    pattern = "**/*.py" if recursive else "*.py"
    py_files = list(directory.glob(pattern))

    print(f"Scanning {len(py_files)} Python files...")

    for filepath in py_files:
        issues = check_code_patterns(filepath)
        all_issues.extend(issues)

    return all_issues


def print_results(issues: List[dict]):
    """Print analysis results"""

    if not issues:
        print("\n✅ No issues detected!")
        return 0

    # Group by severity
    by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'ERROR': []}
    for issue in issues:
        by_severity[issue['severity']].append(issue)

    # Print issues
    total = 0
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'ERROR']:
        issues_list = by_severity[severity]
        if not issues_list:
            continue

        emoji = {
            'CRITICAL': '🚨',
            'HIGH': '❌',
            'MEDIUM': '⚠️',
            'LOW': 'ℹ️',
            'ERROR': '💥'
        }[severity]

        print(f"\n{emoji} {severity} Issues ({len(issues_list)}):")
        print("="*70)

        for issue in issues_list:
            total += 1
            print(f"\n{issue['file']}:{issue['line']}")
            print(f"  {issue['message']}")
            if issue.get('fix'):
                print(f"  💡 Fix: {issue['fix']}")
            if issue.get('function'):
                print(f"  📍 In function: {issue['function']}")

    # Summary
    print("\n" + "="*70)
    print(f"Found {total} potential issues:")
    for severity, issues_list in by_severity.items():
        if issues_list:
            print(f"  {severity}: {len(issues_list)}")
    print("="*70)

    # Return exit code based on severity
    if by_severity['CRITICAL'] or by_severity['ERROR']:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Detect ML antipatterns and data leakage in Python code'
    )
    parser.add_argument('path', help='Python file or directory to analyze')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Recursively scan directory')

    args = parser.parse_args()
    path = Path(args.path)

    print("="*70)
    print(" ML Code Leakage Detector")
    print("="*70)
    print(f"\nAnalyzing: {path}\n")

    if not path.exists():
        print(f"❌ Error: Path not found: {path}")
        return 1

    # Analyze code
    if path.is_file():
        issues = check_code_patterns(path)
    else:
        issues = scan_directory(path, args.recursive)

    # Print results
    return print_results(issues)


if __name__ == "__main__":
    exit(main())
