#!/usr/bin/env python3
"""
Code Quality Checker

Validates code quality in Claude's responses by analyzing:
- Code structure and organization
- Best practices adherence
- Error handling patterns
- Documentation quality

Usage:
    python3 check-code-quality.py <file-or-text>
    echo "code here" | python3 check-code-quality.py -

Returns JSON with quality scores and issues.
"""

import ast
import json
import re
import sys
from typing import Any


def check_python_quality(code: str) -> dict:
    """Check Python code quality and return scores."""
    result = {
        "score": 100,
        "issues": [],
        "metrics": {
            "functions": 0,
            "classes": 0,
            "documented_functions": 0,
            "type_hinted_functions": 0,
            "lines": code.count('\n') + 1
        }
    }

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        result["score"] = 0
        result["issues"].append({
            "severity": "critical",
            "message": f"Syntax error: {e.msg} at line {e.lineno}"
        })
        return result

    # Analyze functions
    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

    result["metrics"]["functions"] = len(functions)
    result["metrics"]["classes"] = len(classes)

    for func in functions:
        # Check for docstring
        if ast.get_docstring(func):
            result["metrics"]["documented_functions"] += 1
        else:
            func_lines = getattr(func, 'end_lineno', 0) - func.lineno
            if func_lines > 3:
                result["issues"].append({
                    "severity": "minor",
                    "message": f"Function '{func.name}' lacks docstring"
                })
                result["score"] -= 2

        # Check for return type hint
        if func.returns is not None:
            result["metrics"]["type_hinted_functions"] += 1
        elif func.name not in ("__init__", "__str__", "__repr__"):
            result["score"] -= 1

        # Check for too many arguments
        total_args = len(func.args.args) + len(func.args.kwonlyargs)
        if total_args > 7:
            result["issues"].append({
                "severity": "important",
                "message": f"Function '{func.name}' has {total_args} arguments (consider refactoring)"
            })
            result["score"] -= 5

        # Check for bare except
        for node in ast.walk(func):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                result["issues"].append({
                    "severity": "important",
                    "message": f"Bare except in '{func.name}'"
                })
                result["score"] -= 10

    # Check for wildcard imports
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    result["issues"].append({
                        "severity": "minor",
                        "message": f"Wildcard import from {node.module}"
                    })
                    result["score"] -= 3

    # Ensure score doesn't go negative
    result["score"] = max(0, result["score"])

    return result


def check_javascript_quality(code: str) -> dict:
    """Check JavaScript code quality using pattern analysis."""
    result = {
        "score": 100,
        "issues": [],
        "metrics": {
            "functions": len(re.findall(r'\bfunction\s+\w+\s*\(|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', code)),
            "lines": code.count('\n') + 1
        }
    }

    # Check for var usage
    var_count = len(re.findall(r'\bvar\s+', code))
    if var_count > 0:
        result["issues"].append({
            "severity": "minor",
            "message": f"Found {var_count} uses of 'var' - prefer let/const"
        })
        result["score"] -= var_count * 2

    # Check for == vs ===
    loose_eq = len(re.findall(r'[^=!]==[^=]', code))
    if loose_eq > 0:
        result["issues"].append({
            "severity": "minor",
            "message": f"Found {loose_eq} uses of '==' - prefer '==='"
        })
        result["score"] -= loose_eq

    # Check for console.log
    console_count = len(re.findall(r'console\.(log|warn|error)\s*\(', code))
    if console_count > 3:
        result["issues"].append({
            "severity": "minor",
            "message": f"Found {console_count} console statements"
        })
        result["score"] -= 2

    # Check for empty catch blocks
    empty_catch = len(re.findall(r'catch\s*\([^)]*\)\s*\{\s*\}', code))
    if empty_catch > 0:
        result["issues"].append({
            "severity": "important",
            "message": f"Found {empty_catch} empty catch blocks"
        })
        result["score"] -= empty_catch * 10

    result["score"] = max(0, result["score"])
    return result


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Extract code blocks with their language."""
    pattern = r"```(\w*)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang.lower() if lang else "unknown", code.strip()) for lang, code in matches]


def check_quality(text: str) -> dict:
    """Main entry point: check quality of all code in text."""
    blocks = extract_code_blocks(text)

    if not blocks:
        # Check if the text itself is code
        if re.search(r'(def |class |function |const |import |from )', text):
            blocks = [("unknown", text)]
        else:
            return {
                "overall_score": 100,
                "blocks_analyzed": 0,
                "results": [],
                "summary": "No code blocks found"
            }

    results = []
    total_score = 0

    for lang, code in blocks:
        if lang in ("python", "py", "python3", ""):
            result = check_python_quality(code)
        elif lang in ("javascript", "js", "typescript", "ts"):
            result = check_javascript_quality(code)
        else:
            result = {"score": 100, "issues": [], "metrics": {"lines": code.count('\n') + 1}}

        result["language"] = lang
        results.append(result)
        total_score += result["score"]

    overall = total_score // len(results) if results else 100

    return {
        "overall_score": overall,
        "blocks_analyzed": len(blocks),
        "results": results,
        "summary": f"Analyzed {len(blocks)} code blocks with average score {overall}/100"
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: check-code-quality.py <file-or-text>", file=sys.stderr)
        print("       echo 'code' | check-code-quality.py -", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                text = f.read()
        except FileNotFoundError:
            # Treat as inline code
            text = sys.argv[1]

    result = check_quality(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
