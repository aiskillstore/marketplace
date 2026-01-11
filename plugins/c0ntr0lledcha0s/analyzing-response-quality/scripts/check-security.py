#!/usr/bin/env python3
"""
Security Checker

Validates the security of code in Claude's responses by checking:
- Common vulnerability patterns (OWASP Top 10)
- Hardcoded secrets
- Insecure functions
- Input validation gaps

Usage:
    python3 check-security.py <file-or-text>
    echo "code" | python3 check-security.py -

Returns JSON with security scores and vulnerabilities found.
"""

import ast
import json
import re
import sys
from typing import Any


# Vulnerability patterns by severity
CRITICAL_PATTERNS = [
    (r'\beval\s*\(', "eval()", "Code execution vulnerability - eval can run arbitrary code"),
    (r'\bexec\s*\(', "exec()", "Code execution vulnerability - exec can run arbitrary code"),
    (r'pickle\.(loads?|dump)', "pickle", "Insecure deserialization - pickle can execute arbitrary code"),
    (r'yaml\.load\s*\([^)]*\)', "yaml.load", "Use yaml.safe_load() instead of yaml.load()"),
    (r'subprocess.*shell\s*=\s*True', "shell=True", "Command injection risk - avoid shell=True"),
    (r'\bos\.system\s*\(', "os.system()", "Command injection risk - use subprocess with shell=False"),
    (r'\.innerHTML\s*=', "innerHTML", "XSS vulnerability - sanitize HTML or use textContent"),
    (r'document\.write\s*\(', "document.write()", "XSS vulnerability - avoid document.write"),
    (r"rm\s+-rf?\s+[\"']?\$", "rm -rf $var", "Dangerous file deletion with variable"),
    (r'curl.*\|\s*(?:ba)?sh', "curl | bash", "Remote code execution - never pipe curl to shell"),
]

IMPORTANT_PATTERNS = [
    (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password", "Store passwords in environment variables or vaults"),
    (r'api_?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key", "Store API keys in environment variables"),
    (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret", "Store secrets securely, not in code"),
    (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token", "Store tokens in environment variables"),
    (r'["\']-----BEGIN (?:RSA |DSA )?PRIVATE KEY-----', "Private key in code", "Never commit private keys"),
    (r'(?:mysql|postgres|mongodb)://[^:]+:[^@]+@', "Database URL with password", "Use environment variables for credentials"),
    (r'SELECT.*FROM.*WHERE.*["\'].*\+', "SQL string concatenation", "Use parameterized queries"),
    (r'f["\'].*SELECT.*\{', "SQL f-string", "Use parameterized queries, not f-strings"),
    (r'query\s*\+\s*["\']', "SQL concatenation", "Use parameterized queries"),
    (r'\$_(?:GET|POST|REQUEST)\[', "Unsanitized PHP input", "Sanitize and validate all user input"),
    (r'dangerouslySetInnerHTML', "dangerouslySetInnerHTML", "XSS risk - sanitize content first"),
]

MINOR_PATTERNS = [
    (r'\bMD5\s*\(|hashlib\.md5', "MD5 hash", "MD5 is weak - use SHA-256 or bcrypt for passwords"),
    (r'\bSHA1\s*\(|hashlib\.sha1', "SHA1 hash", "SHA1 is weak - use SHA-256 or better"),
    (r'verify\s*=\s*False', "SSL verification disabled", "Don't disable SSL certificate verification"),
    (r'random\.(random|randint|choice)\s*\(', "Weak random", "Use secrets module for security-sensitive randomness"),
    (r'Math\.random\s*\(', "Math.random()", "Use crypto.getRandomValues() for security"),
    (r'chmod\s+777', "chmod 777", "Overly permissive - use minimal required permissions"),
    (r'console\.(log|warn)\s*\(.*(password|secret|key|token)', "Logging sensitive data", "Don't log secrets"),
]


def check_python_security(code: str) -> list[dict]:
    """Check Python code for security issues using AST."""
    issues = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues  # Can't parse, skip AST checks

    for node in ast.walk(tree):
        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            func_name = get_call_name(node)

            if func_name == "eval":
                issues.append({
                    "severity": "critical",
                    "type": "code_execution",
                    "message": "eval() can execute arbitrary code",
                    "line": node.lineno,
                    "fix": "Use ast.literal_eval() for data parsing, or explicit parsing"
                })

            if func_name == "exec":
                issues.append({
                    "severity": "critical",
                    "type": "code_execution",
                    "message": "exec() can execute arbitrary code",
                    "line": node.lineno,
                    "fix": "Avoid exec() - use explicit function calls instead"
                })

            if func_name in ("pickle.load", "pickle.loads"):
                issues.append({
                    "severity": "critical",
                    "type": "insecure_deserialization",
                    "message": "pickle can execute arbitrary code during deserialization",
                    "line": node.lineno,
                    "fix": "Use JSON or other safe serialization formats"
                })

        # Check for hardcoded secrets in assignments
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    if any(s in var_name for s in ("password", "secret", "api_key", "token", "credential")):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            if len(node.value.value) > 3:
                                issues.append({
                                    "severity": "important",
                                    "type": "hardcoded_secret",
                                    "message": f"Potential hardcoded secret in '{target.id}'",
                                    "line": node.lineno,
                                    "fix": "Use os.environ.get() or a secrets manager"
                                })

    return issues


def get_call_name(node: ast.Call) -> str:
    """Get the full name of a function call."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return ""


def check_patterns(code: str) -> list[dict]:
    """Check code against vulnerability patterns."""
    issues = []

    for pattern, name, message in CRITICAL_PATTERNS:
        matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "critical",
                "type": name.lower().replace(' ', '_').replace('()', ''),
                "message": message,
                "line": line_num,
                "match": match.group()[:50]
            })

    for pattern, name, message in IMPORTANT_PATTERNS:
        matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "important",
                "type": name.lower().replace(' ', '_'),
                "message": message,
                "line": line_num,
                "match": match.group()[:50]
            })

    for pattern, name, message in MINOR_PATTERNS:
        matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "severity": "minor",
                "type": name.lower().replace(' ', '_').replace('()', ''),
                "message": message,
                "line": line_num,
                "match": match.group()[:50]
            })

    return issues


def extract_code_blocks(text: str) -> str:
    """Extract all code from text (both in blocks and inline)."""
    # Get code blocks
    blocks = re.findall(r"```\w*\n(.*?)```", text, re.DOTALL)

    # Also get the full text in case code isn't in blocks
    return "\n".join(blocks) + "\n" + text


def check_security(text: str) -> dict:
    """Main entry point: check security of all code in text."""
    code = extract_code_blocks(text)

    # Combine pattern-based and AST-based checks
    pattern_issues = check_patterns(code)
    ast_issues = check_python_security(code)

    # Deduplicate issues (same line and type)
    seen = set()
    unique_issues = []
    for issue in pattern_issues + ast_issues:
        key = (issue.get("line", 0), issue["type"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    # Calculate score
    score = 100
    for issue in unique_issues:
        if issue["severity"] == "critical":
            score -= 25
        elif issue["severity"] == "important":
            score -= 10
        else:
            score -= 3

    score = max(0, score)

    # Sort by severity
    severity_order = {"critical": 0, "important": 1, "minor": 2}
    unique_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

    # Summary
    critical = sum(1 for i in unique_issues if i["severity"] == "critical")
    important = sum(1 for i in unique_issues if i["severity"] == "important")
    minor = sum(1 for i in unique_issues if i["severity"] == "minor")

    if critical > 0:
        summary = f"CRITICAL: Found {critical} critical security issues"
    elif important > 0:
        summary = f"WARNING: Found {important} important security issues"
    elif minor > 0:
        summary = f"INFO: Found {minor} minor security concerns"
    else:
        summary = "PASS: No security issues detected"

    return {
        "score": score,
        "issues": unique_issues,
        "counts": {
            "critical": critical,
            "important": important,
            "minor": minor
        },
        "summary": summary
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: check-security.py <file-or-text>", file=sys.stderr)
        print("       echo 'code' | check-security.py -", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                text = f.read()
        except FileNotFoundError:
            text = sys.argv[1]

    result = check_security(text)
    print(json.dumps(result, indent=2))

    # Exit with error code if critical issues found
    if result["counts"]["critical"] > 0:
        sys.exit(2)
    elif result["counts"]["important"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
