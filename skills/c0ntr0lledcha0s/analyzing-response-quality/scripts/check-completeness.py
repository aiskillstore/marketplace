#!/usr/bin/env python3
"""
Completeness Checker

Validates the completeness of Claude's responses by checking:
- All requirements addressed
- Edge cases considered
- Error handling present
- Documentation included where appropriate

Usage:
    python3 check-completeness.py <response-file> [requirements-file]
    echo "response" | python3 check-completeness.py -

Returns JSON with completeness scores and gaps.
"""

import json
import re
import sys


def analyze_completeness(response: str, requirements: str = "") -> dict:
    """Analyze the completeness of a response."""
    result = {
        "score": 100,
        "checks": [],
        "gaps": [],
        "suggestions": []
    }

    # Check for code blocks
    code_blocks = len(re.findall(r"```", response)) // 2
    has_code = code_blocks > 0

    # Extract code for analysis
    code_content = "\n".join(re.findall(r"```\w*\n(.*?)```", response, re.DOTALL))

    # Check 1: Error Handling
    if has_code:
        has_try_catch = bool(re.search(r'\b(try|catch|except|finally)\b', code_content))
        has_error_check = bool(re.search(r'\b(if\s+err|error\s*!=|\.catch\(|on_?error)\b', code_content))

        if has_try_catch or has_error_check:
            result["checks"].append({
                "name": "error_handling",
                "passed": True,
                "message": "Error handling is present"
            })
        else:
            result["checks"].append({
                "name": "error_handling",
                "passed": False,
                "message": "No error handling found"
            })
            result["gaps"].append("Missing error handling for potential failures")
            result["suggestions"].append("Add try/catch blocks or error checks for I/O, network, or parsing operations")
            result["score"] -= 15

    # Check 2: Input Validation
    if has_code:
        has_validation = bool(re.search(
            r'\b(validat|sanitiz|check|verify|assert|if\s+not?\s+|if\s+\w+\s*[!=]=|typeof|instanceof)\b',
            code_content, re.IGNORECASE
        ))

        if has_validation:
            result["checks"].append({
                "name": "input_validation",
                "passed": True,
                "message": "Input validation is present"
            })
        else:
            result["checks"].append({
                "name": "input_validation",
                "passed": False,
                "message": "No input validation found"
            })
            result["gaps"].append("Missing input validation")
            result["suggestions"].append("Validate inputs before processing (check types, ranges, null/undefined)")
            result["score"] -= 10

    # Check 3: Edge Cases
    edge_case_indicators = [
        r'\b(empty|null|none|undefined|zero|negative)\b',
        r'\b(edge\s*case|corner\s*case|boundary)\b',
        r'\bif\s+len\s*\([^)]+\)\s*[=<>]',
        r'\bif\s+not\s+\w+\b'
    ]

    edge_cases_mentioned = sum(1 for pattern in edge_case_indicators if re.search(pattern, response, re.IGNORECASE))

    if edge_cases_mentioned >= 2:
        result["checks"].append({
            "name": "edge_cases",
            "passed": True,
            "message": f"Edge cases considered ({edge_cases_mentioned} indicators found)"
        })
    else:
        result["checks"].append({
            "name": "edge_cases",
            "passed": False,
            "message": "Few edge cases considered"
        })
        result["gaps"].append("Edge cases may not be fully addressed")
        result["suggestions"].append("Consider: empty inputs, null values, boundary conditions, concurrent access")
        result["score"] -= 10

    # Check 4: Documentation/Explanation
    has_explanation = len(response) - len(code_content) > 100 if has_code else True
    has_comments = bool(re.search(r'(#|//|/\*|\"\"\"|\'\'\')', code_content))
    has_docstring = bool(re.search(r'(\"\"\"|\'\'\')[^"\']+\1', code_content))

    if has_explanation or has_comments or has_docstring:
        result["checks"].append({
            "name": "documentation",
            "passed": True,
            "message": "Explanation or documentation provided"
        })
    else:
        result["checks"].append({
            "name": "documentation",
            "passed": False,
            "message": "Minimal explanation provided"
        })
        result["gaps"].append("Code lacks explanation or comments")
        result["suggestions"].append("Add brief explanation of approach or comments for complex logic")
        result["score"] -= 5

    # Check 5: Tests or Usage Examples
    has_tests = bool(re.search(r'\b(test_|_test|Test|spec\.|describe\(|it\(|expect\(|assert)', response))
    has_examples = bool(re.search(r'(example|usage|output|result)[:\s]', response, re.IGNORECASE))

    if has_tests or has_examples:
        result["checks"].append({
            "name": "examples_tests",
            "passed": True,
            "message": "Tests or usage examples provided"
        })
    else:
        result["checks"].append({
            "name": "examples_tests",
            "passed": False,
            "message": "No tests or examples provided"
        })
        result["gaps"].append("Missing tests or usage examples")
        result["suggestions"].append("Include a usage example or basic test case")
        result["score"] -= 10

    # Check 6: Requirements Coverage (if requirements provided)
    if requirements:
        req_keywords = extract_keywords(requirements)
        resp_keywords = extract_keywords(response)

        covered = len(req_keywords & resp_keywords)
        total = len(req_keywords)

        if total > 0:
            coverage = (covered / total) * 100
            if coverage >= 80:
                result["checks"].append({
                    "name": "requirements_coverage",
                    "passed": True,
                    "message": f"Requirements coverage: {coverage:.0f}%"
                })
            else:
                result["checks"].append({
                    "name": "requirements_coverage",
                    "passed": False,
                    "message": f"Requirements coverage: {coverage:.0f}%"
                })
                missing = req_keywords - resp_keywords
                result["gaps"].append(f"Missing requirement keywords: {', '.join(list(missing)[:5])}")
                result["score"] -= int((100 - coverage) / 5)

    # Ensure score doesn't go negative
    result["score"] = max(0, result["score"])

    # Summary
    passed = sum(1 for c in result["checks"] if c["passed"])
    total = len(result["checks"])
    result["summary"] = f"Passed {passed}/{total} completeness checks with score {result['score']}/100"

    return result


def extract_keywords(text: str) -> set:
    """Extract significant keywords from text."""
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Extract words
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

    # Filter common words
    stopwords = {
        'that', 'this', 'with', 'from', 'have', 'will', 'would', 'could', 'should',
        'been', 'were', 'they', 'their', 'them', 'then', 'than', 'when', 'where',
        'what', 'which', 'while', 'also', 'your', 'about', 'into', 'some', 'more',
        'like', 'just', 'only', 'other', 'each', 'make', 'made', 'does', 'done'
    }

    return {w for w in words if w not in stopwords}


def main():
    if len(sys.argv) < 2:
        print("Usage: check-completeness.py <response-file> [requirements-file]", file=sys.stderr)
        print("       echo 'response' | check-completeness.py -", file=sys.stderr)
        sys.exit(1)

    # Read response
    if sys.argv[1] == "-":
        response = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                response = f.read()
        except FileNotFoundError:
            response = sys.argv[1]

    # Read requirements if provided
    requirements = ""
    if len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'r') as f:
                requirements = f.read()
        except FileNotFoundError:
            requirements = sys.argv[2]

    result = analyze_completeness(response, requirements)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
